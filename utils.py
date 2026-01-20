"""
Utilidades y Helpers
Funciones auxiliares para validación, formateo y helpers
"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un email
    
    Returns:
        (is_valid, error_message)
    """
    if not email or len(email) < 5:
        return False, "Email muy corto"
    
    # Patrón básico de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    
    # Validaciones adicionales
    if '..' in email:
        return False, "Email no puede contener puntos consecutivos"
    
    if email.startswith('.') or email.endswith('.'):
        return False, "Email no puede empezar o terminar con punto"
    
    local_part, domain = email.rsplit('@', 1)
    
    if len(local_part) > 64:
        return False, "Parte local del email muy larga"
    
    if len(domain) > 255:
        return False, "Dominio muy largo"
    
    return True, None


def sanitize_html(html: str) -> str:
    """
    Sanitiza HTML básicamente (para plantillas)
    Elimina scripts y permite solo tags seguros
    """
    # Eliminar scripts
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'on\w+="[^"]*"', '', html)  # Eliminar event handlers
    html = re.sub(r"on\w+='[^']*'", '', html)
    
    return html


def validate_smtp_config(server: str, port: int, username: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Valida configuración SMTP
    
    Returns:
        (is_valid, error_message)
    """
    if not server or len(server) < 3:
        return False, "Servidor SMTP inválido"
    
    if not isinstance(port, int) or port < 1 or port > 65535:
        return False, "Puerto debe estar entre 1 y 65535"
    
    if not username or len(username) < 3:
        return False, "Usuario SMTP inválido"
    
    if not password or len(password) < 3:
        return False, "Contraseña SMTP muy corta"
    
    # Validar que el servidor tenga formato correcto
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$', server):
        return False, "Formato de servidor inválido"
    
    return True, None


def format_number(number: int) -> str:
    """Formatea un número con separadores de miles"""
    return f"{number:,}".replace(",", ".")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca texto a una longitud máxima"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """Escapa caracteres especiales para Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def parse_csv_line(line: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parsea una línea CSV simple (email, nombre)
    
    Returns:
        (email, name) or (None, None) if invalid
    """
    parts = [p.strip() for p in line.split(',')]
    
    if len(parts) < 1:
        return None, None
    
    email = parts[0]
    name = parts[1] if len(parts) > 1 else None
    
    is_valid, _ = validate_email(email)
    if not is_valid:
        return None, None
    
    return email, name


def is_html(text: str) -> bool:
    """Detecta si un texto contiene HTML"""
    html_pattern = r'<[^>]+>'
    return bool(re.search(html_pattern, text))


def get_smtp_provider_config(provider: str) -> dict:
    """
    Obtiene configuración predefinida para proveedores conocidos
    
    Args:
        provider: gmail, outlook, yahoo, etc.
        
    Returns:
        dict con server, port, use_tls
    """
    configs = {
        'gmail': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'name': 'Gmail'
        },
        'outlook': {
            'server': 'smtp.office365.com',
            'port': 587,
            'use_tls': True,
            'name': 'Outlook'
        },
        'yahoo': {
            'server': 'smtp.mail.yahoo.com',
            'port': 587,
            'use_tls': True,
            'name': 'Yahoo'
        },
        'sendgrid': {
            'server': 'smtp.sendgrid.net',
            'port': 587,
            'use_tls': True,
            'name': 'SendGrid'
        },
        'mailgun': {
            'server': 'smtp.mailgun.org',
            'port': 587,
            'use_tls': True,
            'name': 'Mailgun'
        }
    }
    
    return configs.get(provider.lower(), {
        'server': '',
        'port': 587,
        'use_tls': True,
        'name': 'Personalizado'
    })


def format_time_ago(timestamp_str: str) -> str:
    """
    Formatea un timestamp a tiempo relativo (hace X tiempo)
    
    Args:
        timestamp_str: ISO format timestamp string
        
    Returns:
        String con tiempo relativo
    """
    from datetime import datetime, timedelta
    
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        now = datetime.now()
        diff = now - timestamp
        
        if diff < timedelta(minutes=1):
            return "Hace menos de 1 minuto"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"Hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff < timedelta(days=30):
            days = diff.days
            return f"Hace {days} día{'s' if days > 1 else ''}"
        elif diff < timedelta(days=365):
            months = int(diff.days / 30)
            return f"Hace {months} mes{'es' if months > 1 else ''}"
        else:
            years = int(diff.days / 365)
            return f"Hace {years} año{'s' if years > 1 else ''}"
    except:
        return timestamp_str[:10]
