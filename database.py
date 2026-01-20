"""
Módulo de Base de Datos - Sistema de Membresías
Gestiona el almacenamiento y recuperación de datos de membresía de usuarios
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from config import Config


class MembershipDatabase:
    """Clase para gestionar la base de datos de membresías"""
    
    def __init__(self, db_name: str = None):
        """
        Inicializa la conexión a la base de datos
        
        Args:
            db_name: Nombre del archivo de base de datos (opcional)
        """
        self.db_name = db_name or Config.DATABASE_NAME
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Crea y retorna una nueva conexión a la base de datos"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Crea las tablas necesarias si no existen"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de miembros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                added_date TEXT NOT NULL,
                added_by INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Tabla de logs de actividad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                performed_by INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_member(self, user_id: int, username: str = None, 
                   first_name: str = None, last_name: str = None,
                   added_by: int = None) -> bool:
        """
        Añade un nuevo miembro a la base de datos
        
        Args:
            user_id: ID de Telegram del usuario
            username: Nombre de usuario de Telegram (opcional)
            first_name: Nombre del usuario (opcional)
            last_name: Apellido del usuario (opcional)
            added_by: ID del usuario que añadió al miembro
            
        Returns:
            True si se añadió exitosamente, False si ya existe
        """
        if self.is_member(user_id):
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO members (user_id, username, first_name, last_name, added_date, added_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, datetime.now().isoformat(), added_by))
            
            # Registrar en el log
            self._log_activity(cursor, user_id, 'MEMBER_ADDED', added_by)
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def remove_member(self, user_id: int, removed_by: int) -> bool:
        """
        Elimina un miembro de la base de datos
        
        Args:
            user_id: ID de Telegram del usuario a eliminar
            removed_by: ID del usuario que eliminó al miembro
            
        Returns:
            True si se eliminó exitosamente, False si no existe
        """
        if not self.is_member(user_id):
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM members WHERE user_id = ?', (user_id,))
        
        # Registrar en el log
        self._log_activity(cursor, user_id, 'MEMBER_REMOVED', removed_by)
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def is_member(self, user_id: int) -> bool:
        """
        Verifica si un usuario es miembro activo
        
        Args:
            user_id: ID de Telegram del usuario
            
        Returns:
            True si es miembro activo, False en caso contrario
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM members 
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        
        result = cursor.fetchone() is not None
        conn.close()
        
        return result
    
    def get_all_members(self) -> List[dict]:
        """
        Obtiene una lista de todos los miembros activos
        
        Returns:
            Lista de diccionarios con información de miembros
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, last_name, added_date
            FROM members
            WHERE is_active = 1
            ORDER BY added_date DESC
        ''')
        
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return members
    
    def get_member_count(self) -> int:
        """
        Obtiene el número total de miembros activos
        
        Returns:
            Cantidad de miembros activos
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM members WHERE is_active = 1')
        count = cursor.fetchone()['count']
        
        conn.close()
        return count
    
    def get_member_info(self, user_id: int) -> Optional[dict]:
        """
        Obtiene información detallada de un miembro
        
        Args:
            user_id: ID de Telegram del usuario
            
        Returns:
            Diccionario con información del miembro o None si no existe
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, last_name, added_date, added_by, is_active
            FROM members
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def _log_activity(self, cursor: sqlite3.Cursor, user_id: int, 
                      action: str, performed_by: int):
        """
        Registra una actividad en el log
        
        Args:
            cursor: Cursor de la base de datos
            user_id: ID del usuario afectado
            action: Acción realizada
            performed_by: ID del usuario que realizó la acción
        """
        cursor.execute('''
            INSERT INTO activity_log (user_id, action, timestamp, performed_by)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action, datetime.now().isoformat(), performed_by))
    
    def get_activity_log(self, limit: int = 50) -> List[dict]:
        """
        Obtiene el registro de actividades recientes
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de actividades registradas
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, action, timestamp, performed_by
            FROM activity_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
