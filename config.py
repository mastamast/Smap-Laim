"""
Configuración del Bot de Telegram
Gestiona las variables de entorno y configuraciones globales
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Clase de configuración centralizada para el bot"""
    
    # Token de la API del bot de Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # ID del usuario administrador
    ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))
    
    # Nombre de la base de datos
    DATABASE_NAME = 'membership.db'
    
    @classmethod
    def validate(cls):
        """Valida que todas las configuraciones requeridas estén presentes"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en .env")
        
        if not cls.ADMIN_USER_ID:
            raise ValueError("ADMIN_USER_ID no está configurado en .env")
        
        return True
