"""
Módulo de Envío de Emails Masivos
Gestiona el envío de campañas de email tranzas
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
import time
import sqlite3
from config import Config


class EmailSender:
    """Clase para gestionar el envío de emails masivos"""
    
    def __init__(self):
        """Inicializa el servicio de envío de emails"""
        self.db_name = Config.DATABASE_NAME
        self.init_email_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Crea y retorna una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_email_database(self):
        """Crea las tablas necesarias para el sistema de emails"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de listas de correos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_date TEXT NOT NULL,
                created_by INTEGER NOT NULL,
                recipient_count INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de destinatarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                name TEXT,
                added_date TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (list_id) REFERENCES email_lists (id),
                UNIQUE(list_id, email)
            )
        ''')
        
        # Tabla de plantillas de email
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                created_date TEXT NOT NULL,
                created_by INTEGER NOT NULL
            )
        ''')
        
        # Tabla de campañas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template_id INTEGER NOT NULL,
                list_id INTEGER NOT NULL,
                status TEXT DEFAULT 'PENDING',
                created_date TEXT NOT NULL,
                started_date TEXT,
                completed_date TEXT,
                created_by INTEGER NOT NULL,
                total_recipients INTEGER DEFAULT 0,
                sent_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                FOREIGN KEY (template_id) REFERENCES email_templates (id),
                FOREIGN KEY (list_id) REFERENCES email_lists (id)
            )
        ''')
        
        # Tabla de configuración SMTP
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smtp_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                smtp_server TEXT,
                smtp_port INTEGER DEFAULT 587,
                smtp_username TEXT,
                smtp_password TEXT,
                sender_email TEXT,
                sender_name TEXT,
                use_tls INTEGER DEFAULT 1,
                delay_between_emails REAL DEFAULT 1.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============================================
    # GESTIÓN DE LISTAS DE CORREOS
    # ============================================
    
    def create_email_list(self, name: str, description: str, created_by: int) -> Optional[int]:
        """
        Crea una nueva lista de correos
        
        Args:
            name: Nombre de la lista
            description: Descripción de la lista
            created_by: ID del usuario que crea la lista
            
        Returns:
            ID de la lista creada o None si falló
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO email_lists (name, description, created_date, created_by)
                VALUES (?, ?, ?, ?)
            ''', (name, description, datetime.now().isoformat(), created_by))
            
            list_id = cursor.lastrowid
            conn.commit()
            return list_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def add_recipient(self, list_id: int, email: str, name: str = None) -> bool:
        """
        Añade un destinatario a una lista
        
        Args:
            list_id: ID de la lista
            email: Email del destinatario
            name: Nombre del destinatario (opcional)
            
        Returns:
            True si se añadió exitosamente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO email_recipients (list_id, email, name, added_date)
                VALUES (?, ?, ?, ?)
            ''', (list_id, email.lower(), name, datetime.now().isoformat()))
            
            # Actualizar contador de la lista
            cursor.execute('''
                UPDATE email_lists 
                SET recipient_count = (
                    SELECT COUNT(*) FROM email_recipients 
                    WHERE list_id = ? AND is_active = 1
                )
                WHERE id = ?
            ''', (list_id, list_id))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_lists(self) -> List[dict]:
        """Obtiene todas las listas de correos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, created_date, recipient_count
            FROM email_lists
            ORDER BY created_date DESC
        ''')
        
        lists = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return lists
    
    def get_list_recipients(self, list_id: int) -> List[dict]:
        """Obtiene todos los destinatarios de una lista"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, name, added_date
            FROM email_recipients
            WHERE list_id = ? AND is_active = 1
            ORDER BY added_date DESC
        ''', (list_id,))
        
        recipients = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return recipients
    
    # ============================================
    # GESTIÓN DE PLANTILLAS
    # ============================================
    
    def create_template(self, name: str, subject: str, body: str, created_by: int) -> Optional[int]:
        """
        Crea una nueva plantilla de email
        
        Args:
            name: Nombre de la plantilla
            subject: Asunto del email
            body: Cuerpo del email (soporta HTML)
            created_by: ID del usuario que crea la plantilla
            
        Returns:
            ID de la plantilla creada o None si falló
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO email_templates (name, subject, body, created_date, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, subject, body, datetime.now().isoformat(), created_by))
            
            template_id = cursor.lastrowid
            conn.commit()
            return template_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_all_templates(self) -> List[dict]:
        """Obtiene todas las plantillas de email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, subject, created_date
            FROM email_templates
            ORDER BY created_date DESC
        ''')
        
        templates = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return templates
    
    def get_template(self, template_id: int) -> Optional[dict]:
        """Obtiene una plantilla específica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, subject, body, created_date
            FROM email_templates
            WHERE id = ?
        ''', (template_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # ============================================
    # CONFIGURACIÓN SMTP
    # ============================================
    
    def set_smtp_config(self, server: str, port: int, username: str, 
                       password: str, sender_email: str, sender_name: str = None,
                       use_tls: bool = True, delay: float = 1.0) -> bool:
        """
        Configura los parámetros SMTP
        
        Args:
            server: Servidor SMTP (ej: smtp.gmail.com)
            port: Puerto SMTP (ej: 587)
            username: Usuario SMTP
            password: Contraseña SMTP
            sender_email: Email del remitente
            sender_name: Nombre del remitente
            use_tls: Usar TLS/SSL
            delay: Segundos de espera entre emails
            
        Returns:
            True si se configuró correctamente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO smtp_config 
            (id, smtp_server, smtp_port, smtp_username, smtp_password, 
             sender_email, sender_name, use_tls, delay_between_emails)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server, port, username, password, sender_email, sender_name, 
              1 if use_tls else 0, delay))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_smtp_config(self) -> Optional[dict]:
        """Obtiene la configuración SMTP actual"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM smtp_config WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # ============================================
    # ENVÍO DE CAMPAÑAS
    # ============================================
    
    def create_campaign(self, name: str, template_id: int, list_id: int, created_by: int) -> Optional[int]:
        """
        Crea una nueva campaña de envío
        
        Args:
            name: Nombre de la campaña
            template_id: ID de la plantilla a usar
            list_id: ID de la lista de destinatarios
            created_by: ID del usuario que crea la campaña
            
        Returns:
            ID de la campaña creada o None si falló
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener número de destinatarios
        cursor.execute('''
            SELECT COUNT(*) as count FROM email_recipients 
            WHERE list_id = ? AND is_active = 1
        ''', (list_id,))
        
        total_recipients = cursor.fetchone()['count']
        
        cursor.execute('''
            INSERT INTO campaigns 
            (name, template_id, list_id, created_date, created_by, total_recipients)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, template_id, list_id, datetime.now().isoformat(), created_by, total_recipients))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return campaign_id
    
    def send_campaign(self, campaign_id: int) -> Dict[str, any]:
        """
        Envía una campaña de emails
        
        Args:
            campaign_id: ID de la campaña a enviar
            
        Returns:
            Diccionario con resultados del envío
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener datos de la campaña
        cursor.execute('''
            SELECT c.*, t.subject, t.body, l.name as list_name
            FROM campaigns c
            JOIN email_templates t ON c.template_id = t.id
            JOIN email_lists l ON c.list_id = l.id
            WHERE c.id = ?
        ''', (campaign_id,))
        
        campaign = dict(cursor.fetchone())
        
        # Obtener destinatarios
        recipients = self.get_list_recipients(campaign['list_id'])
        
        # Obtener configuración SMTP
        smtp_config = self.get_smtp_config()
        
        if not smtp_config:
            conn.close()
            return {'success': False, 'error': 'SMTP no configurado'}
        
        # Actualizar estado de campaña
        cursor.execute('''
            UPDATE campaigns 
            SET status = 'RUNNING', started_date = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), campaign_id))
        conn.commit()
        
        # Iniciar envío
        sent_count = 0
        failed_count = 0
        
        try:
            # Configurar servidor SMTP
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                if smtp_config['use_tls']:
                    server.starttls(context=context)
                
                server.login(smtp_config['smtp_username'], smtp_config['smtp_password'])
                
                # Enviar a cada destinatario
                for recipient in recipients:
                    try:
                        # Personalizar email
                        subject = campaign['subject']
                        body = campaign['body'].replace('{name}', recipient['name'] or recipient['email'])
                        
                        # Crear mensaje
                        message = MIMEMultipart('alternative')
                        message['Subject'] = subject
                        message['From'] = f"{smtp_config['sender_name']} <{smtp_config['sender_email']}>"
                        message['To'] = recipient['email']
                        
                        # Agregar cuerpo (HTML)
                        html_part = MIMEText(body, 'html')
                        message.attach(html_part)
                        
                        # Enviar
                        server.send_message(message)
                        sent_count += 1
                        
                        # Delay entre emails
                        time.sleep(smtp_config['delay_between_emails'])
                        
                    except Exception as e:
                        print(f"Error enviando a {recipient['email']}: {e}")
                        failed_count += 1
            
            # Actualizar estadísticas de campaña
            cursor.execute('''
                UPDATE campaigns 
                SET status = 'COMPLETED', 
                    completed_date = ?,
                    sent_count = ?,
                    failed_count = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), sent_count, failed_count, campaign_id))
            
            conn.commit()
            
            return {
                'success': True,
                'sent': sent_count,
                'failed': failed_count,
                'total': len(recipients)
            }
            
        except Exception as e:
            cursor.execute('''
                UPDATE campaigns 
                SET status = 'FAILED'
                WHERE id = ?
            ''', (campaign_id,))
            conn.commit()
            
            return {'success': False, 'error': str(e)}
            
        finally:
            conn.close()
    
    def get_all_campaigns(self) -> List[dict]:
        """Obtiene todas las campañas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.name, c.status, c.created_date, c.total_recipients,
                   c.sent_count, c.failed_count, t.name as template_name,
                   l.name as list_name
            FROM campaigns c
            JOIN email_templates t ON c.template_id = t.id
            JOIN email_lists l ON c.list_id = l.id
            ORDER BY c.created_date DESC
        ''')
        
        campaigns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return campaigns
    
    def get_campaign_stats(self, campaign_id: int) -> Optional[dict]:
        """Obtiene estadísticas de una campaña"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, t.name as template_name, l.name as list_name
            FROM campaigns c
            JOIN email_templates t ON c.template_id = t.id
            JOIN email_lists l ON c.list_id = l.id
            WHERE c.id = ?
        ''', (campaign_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
