"""
Decoradores de Seguridad
Proporciona decoradores para controlar el acceso a funciones del bot
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from database import MembershipDatabase


def admin_only(func):
    """
    Decorador que restringe el acceso solo al administrador
    
    Usage:
        @admin_only
        async def admin_command(update, context):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_USER_ID:
            await update.message.reply_text(
                "⛔ Acceso denegado. Solo el administrador puede usar este comando."
            )
            return
        
        return await func(update, context)
    
    return wrapper


def members_only(func):
    """
    Decorador que restringe el acceso solo a miembros autorizados
    
    Usage:
        @members_only
        async def member_command(update, context):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        db = MembershipDatabase()
        
        # El administrador siempre tiene acceso
        if user_id == Config.ADMIN_USER_ID:
            return await func(update, context)
        
        # Verificar si es miembro
        if not db.is_member(user_id):
            await update.message.reply_text(
                "⛔ Acceso denegado. No tienes membresía activa para usar este bot.\n\n"
                "Contacta al administrador para solicitar acceso."
            )
            return
        
        return await func(update, context)
    
    return wrapper


def log_command(func):
    """
    Decorador que registra el uso de comandos
    
    Usage:
        @log_command
        async def some_command(update, context):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "Sin username"
        command = update.message.text
        
        print(f"[LOG] Usuario {user_id} (@{username}) ejecutó: {command}")
        
        return await func(update, context)
    
    return wrapper
