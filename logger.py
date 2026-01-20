"""
Sistema de Logging Mejorado
Proporciona logging estructurado para el bot
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class BotLogger:
    """Logger personalizado para el bot"""
    
    def __init__(self, name: str = "TelegramBot", log_file: str = "bot.log"):
        """
        Inicializa el logger
        
        Args:
            name: Nombre del logger
            log_file: Archivo donde guardar los logs
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicar handlers
        if self.logger.handlers:
            return
        
        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para archivo
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"No se pudo crear archivo de log: {e}")
    
    def info(self, message: str, user_id: Optional[int] = None):
        """Log de información"""
        if user_id:
            message = f"[User {user_id}] {message}"
        self.logger.info(message)
    
    def error(self, message: str, error: Optional[Exception] = None, user_id: Optional[int] = None):
        """Log de error"""
        if user_id:
            message = f"[User {user_id}] {message}"
        if error:
            message = f"{message}: {str(error)}"
        self.logger.error(message)
    
    def warning(self, message: str, user_id: Optional[int] = None):
        """Log de advertencia"""
        if user_id:
            message = f"[User {user_id}] {message}"
        self.logger.warning(message)
    
    def debug(self, message: str, user_id: Optional[int] = None):
        """Log de debug"""
        if user_id:
            message = f"[User {user_id}] {message}"
        self.logger.debug(message)
    
    def log_command(self, command: str, user_id: int, username: Optional[str] = None):
        """Log de comando ejecutado"""
        user_info = f"@{username}" if username else f"ID:{user_id}"
        self.info(f"Comando ejecutado: {command} por {user_info}", user_id=user_id)
    
    def log_campaign(self, campaign_id: int, sent: int, failed: int, total: int, user_id: int):
        """Log de campaña enviada"""
        success_rate = (sent / total * 100) if total > 0 else 0
        self.info(
            f"Campaña {campaign_id}: {sent}/{total} enviados ({success_rate:.1f}%), {failed} fallidos",
            user_id=user_id
        )
    
    def log_smtp_test(self, success: bool, server: str, user_id: int):
        """Log de test SMTP"""
        status = "exitoso" if success else "fallido"
        self.info(f"Test SMTP {status} para servidor {server}", user_id=user_id)
    
    def log_member_action(self, action: str, target_user_id: int, by_user_id: int):
        """Log de acción sobre miembros"""
        self.info(f"Acción '{action}' sobre usuario {target_user_id} por admin {by_user_id}")


# Instancia global del logger
bot_logger = BotLogger()
