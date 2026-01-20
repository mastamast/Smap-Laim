"""
Wizards Guiados para Tareas Complejas
Proporciona asistentes paso a paso para configuración y creación
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from email_sender import EmailSender
from database import MembershipDatabase
from config import Config

# Estados del wizard SMTP
SMTP_SELECT_PROVIDER, SMTP_ENTER_EMAIL, SMTP_ENTER_PASSWORD, SMTP_ENTER_NAME, SMTP_CONFIRM = range(5)

# Estados del wizard Lista
LIST_ENTER_NAME, LIST_ENTER_DESC, LIST_CONFIRM = range(5, 8)

# Estados del wizard Plantilla
TEMPLATE_SELECT_TYPE, TEMPLATE_ENTER_NAME, TEMPLATE_ENTER_SUBJECT, TEMPLATE_ENTER_BODY, TEMPLATE_CONFIRM = range(8, 13)

# Estados del wizard Campaña
CAMPAIGN_SELECT_LIST, CAMPAIGN_SELECT_TEMPLATE, CAMPAIGN_ENTER_NAME, CAMPAIGN_CONFIRM = range(13, 17)


# ============================================
# WIZARD: CONFIGURACIÓN SMTP
# ============================================

async def smtp_wizard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de configuración SMTP"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "⚙️ <b>Configurar Email (Paso 1 de 5)</b>\n\n"
        "🎯 Selecciona tu proveedor de email:\n\n"
        "💡 <i>Configuraremos automáticamente el servidor\n"
        "y puerto según tu elección.</i>"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📧 Gmail", callback_data="smtp_provider_gmail"),
            InlineKeyboardButton("📧 Outlook", callback_data="smtp_provider_outlook")
        ],
        [
            InlineKeyboardButton("📧 Yahoo", callback_data="smtp_provider_yahoo"),
            InlineKeyboardButton("🔧 Otro", callback_data="smtp_provider_custom")
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return SMTP_SELECT_PROVIDER


async def smtp_select_provider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la selección del proveedor SMTP"""
    query = update.callback_query
    await query.answer()
    
    provider = query.data.replace('smtp_provider_', '')
    
    # Configuración automática por proveedor
    smtp_configs = {
        'gmail': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'name': 'Gmail',
            'help_url': 'https://support.google.com/accounts/answer/185833'
        },
        'outlook': {
            'server': 'smtp.office365.com',
            'port': 587,
            'name': 'Outlook',
            'help_url': 'https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353'
        },
        'yahoo': {
            'server': 'smtp.mail.yahoo.com',
            'port': 587,
            'name': 'Yahoo',
            'help_url': 'https://help.yahoo.com/kb/SLN4075.html'
        },
        'custom': {
            'server': '',
            'port': 587,
            'name': 'Personalizado',
            'help_url': ''
        }
    }
    
    config = smtp_configs.get(provider, smtp_configs['custom'])
    context.user_data['smtp_provider'] = provider
    context.user_data['smtp_server'] = config['server']
    context.user_data['smtp_port'] = config['port']
    context.user_data['smtp_provider_name'] = config['name']
    
    if provider == 'custom':
        message = (
            "⚙️ <b>Configurar Email (Paso 2 de 5)</b>\n\n"
            "🔧 Has seleccionado configuración personalizada.\n\n"
            "Por favor, envía el servidor SMTP:\n"
            "<i>Ejemplo: smtp.tuservidor.com</i>\n\n"
            "💡 Consulta la documentación de tu proveedor\n"
            "para obtener estos datos."
        )
        
        keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
        return SMTP_ENTER_EMAIL
    else:
        message = (
            f"⚙️ <b>Configurar Email (Paso 2 de 5)</b>\n\n"
            f"✅ Proveedor: {config['name']}\n"
            f"🌐 Servidor: {config['server']}\n"
            f"🔌 Puerto: {config['port']}\n\n"
            f"📧 Ahora, envía tu dirección de email:\n"
            f"<i>Ejemplo: tunombre@{provider}.com</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton("ℹ️ ¿Cómo obtener contraseña?", url=config['help_url'])],
            [InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
        return SMTP_ENTER_EMAIL


async def smtp_enter_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el email ingresado"""
    email = update.message.text.strip()
    
    # Validación básica de email
    if '@' not in email or '.' not in email:
        await update.message.reply_text(
            "❌ Email inválido. Por favor, envía un email válido:\n"
            "Ejemplo: tunombre@gmail.com"
        )
        return SMTP_ENTER_EMAIL
    
    context.user_data['smtp_email'] = email
    context.user_data['smtp_username'] = email
    
    provider_name = context.user_data.get('smtp_provider_name', 'tu proveedor')
    
    message = (
        f"⚙️ <b>Configurar Email (Paso 3 de 5)</b>\n\n"
        f"✅ Email: {email}\n\n"
        f"🔒 Ahora, envía tu contraseña:\n\n"
    )
    
    if context.user_data.get('smtp_provider') == 'gmail':
        message += (
            "⚠️ <b>IMPORTANTE para Gmail:</b>\n"
            "NO uses tu contraseña normal.\n"
            "Debes crear una 'Contraseña de aplicación':\n\n"
            "1. Ve a myaccount.google.com\n"
            "2. Seguridad → Verificación en 2 pasos\n"
            "3. Contraseñas de aplicaciones\n"
            "4. Genera una nueva contraseña\n\n"
            "📧 Envía esa contraseña aquí:"
        )
    else:
        message += (
            f"💡 Usa la contraseña de tu cuenta {provider_name}\n"
            f"o una contraseña de aplicación si está disponible.\n\n"
            f"🔒 Tu contraseña no se mostrará en pantalla."
        )
    
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return SMTP_ENTER_PASSWORD


async def smtp_enter_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la contraseña ingresada"""
    password = update.message.text.strip()
    
    # Eliminar el mensaje con la contraseña por seguridad
    try:
        await update.message.delete()
    except:
        pass
    
    context.user_data['smtp_password'] = password
    
    message = (
        f"⚙️ <b>Configurar Email (Paso 4 de 5)</b>\n\n"
        f"✅ Contraseña guardada de forma segura\n\n"
        f"✍️ ¿Cómo quieres que aparezca tu nombre\n"
        f"como remitente de los emails?\n\n"
        f"<i>Ejemplo: Mi Empresa, Juan Pérez, etc.</i>"
    )
    
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return SMTP_ENTER_NAME


async def smtp_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el nombre del remitente"""
    sender_name = update.message.text.strip()
    context.user_data['smtp_sender_name'] = sender_name
    
    # Resumen de configuración
    email = context.user_data['smtp_email']
    server = context.user_data['smtp_server']
    port = context.user_data['smtp_port']
    provider = context.user_data.get('smtp_provider_name', 'Personalizado')
    
    message = (
        f"⚙️ <b>Configurar Email (Paso 5 de 5)</b>\n\n"
        f"📋 <b>Resumen de Configuración:</b>\n\n"
        f"🌐 Proveedor: {provider}\n"
        f"📮 Servidor: {server}:{port}\n"
        f"📧 Email: {email}\n"
        f"✍️ Nombre remitente: {sender_name}\n"
        f"🔐 Contraseña: Guardada ✅\n"
        f"🔒 TLS: Activado\n\n"
        f"¿Todo correcto?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Guardar y Probar", callback_data="smtp_save_and_test"),
            InlineKeyboardButton("💾 Solo Guardar", callback_data="smtp_save")
        ],
        [
            InlineKeyboardButton("🔄 Reiniciar", callback_data="wizard_smtp"),
            InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return SMTP_CONFIRM


async def smtp_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda la configuración SMTP"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    
    success = email_service.set_smtp_config(
        server=context.user_data['smtp_server'],
        port=context.user_data['smtp_port'],
        username=context.user_data['smtp_username'],
        password=context.user_data['smtp_password'],
        sender_email=context.user_data['smtp_email'],
        sender_name=context.user_data['smtp_sender_name']
    )
    
    if success:
        message = (
            "✅ <b>¡Configuración Guardada!</b>\n\n"
            f"📧 Email: {context.user_data['smtp_email']}\n"
            f"✍️ Nombre: {context.user_data['smtp_sender_name']}\n\n"
            "🎉 Ya puedes enviar campañas de email.\n\n"
            "🎯 <b>Siguiente paso:</b>\n"
            "Crea tu primera lista de contactos"
        )
        
        keyboard = [
            [InlineKeyboardButton("➕ Crear Lista", callback_data="wizard_list")],
            [InlineKeyboardButton("🏠 Ir al Menú", callback_data="menu_email")]
        ]
    else:
        message = (
            "❌ <b>Error al Guardar</b>\n\n"
            "Hubo un problema al guardar la configuración.\n"
            "Por favor, intenta nuevamente."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Reintentar", callback_data="wizard_smtp")],
            [InlineKeyboardButton("🏠 Volver", callback_data="menu_email")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    # Limpiar datos temporales
    context.user_data.clear()
    
    return ConversationHandler.END


# ============================================
# WIZARD: CREAR LISTA
# ============================================

async def list_wizard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de creación de lista"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "📋 <b>Crear Nueva Lista (Paso 1 de 3)</b>\n\n"
        "Una lista es un grupo de contactos a los que\n"
        "enviarás tus campañas de email.\n\n"
        "📝 Envía un nombre para tu lista:\n"
        "<i>Ejemplos: Clientes VIP, Newsletter 2024,\n"
        "Prospectos México, etc.</i>"
    )
    
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return LIST_ENTER_NAME


async def list_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el nombre de la lista"""
    list_name = update.message.text.strip()
    
    if len(list_name) < 3:
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 3 caracteres.\n"
            "Por favor, envía un nombre más descriptivo:"
        )
        return LIST_ENTER_NAME
    
    context.user_data['list_name'] = list_name
    
    message = (
        f"📋 <b>Crear Nueva Lista (Paso 2 de 3)</b>\n\n"
        f"✅ Nombre: {list_name}\n\n"
        f"📝 Envía una descripción para tu lista:\n"
        f"<i>(Opcional - envía /skip para omitir)</i>\n\n"
        f"<i>Ejemplo: Clientes que compraron en el último mes</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("⏩ Omitir Descripción", callback_data="list_skip_desc")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return LIST_ENTER_DESC


async def list_enter_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la descripción de la lista"""
    if update.message:
        description = update.message.text.strip()
        context.user_data['list_desc'] = description
    else:
        query = update.callback_query
        await query.answer()
        context.user_data['list_desc'] = "Sin descripción"
    
    list_name = context.user_data['list_name']
    list_desc = context.user_data['list_desc']
    
    message = (
        f"📋 <b>Crear Nueva Lista (Paso 3 de 3)</b>\n\n"
        f"📝 <b>Resumen:</b>\n\n"
        f"Nombre: {list_name}\n"
        f"Descripción: {list_desc}\n\n"
        f"¿Deseas crear esta lista?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Crear Lista", callback_data="list_create"),
            InlineKeyboardButton("🔄 Reiniciar", callback_data="wizard_list")
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return LIST_CONFIRM


async def list_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea la lista en la base de datos"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    user_id = update.effective_user.id
    
    list_id = email_service.create_email_list(
        name=context.user_data['list_name'],
        description=context.user_data['list_desc'],
        created_by=user_id
    )
    
    if list_id:
        message = (
            f"✅ <b>¡Lista Creada Exitosamente!</b>\n\n"
            f"📋 Nombre: {context.user_data['list_name']}\n"
            f"🆔 ID: {list_id}\n"
            f"👥 Contactos: 0\n\n"
            f"🎯 <b>Siguiente paso:</b>\n"
            f"Agrega contactos a tu lista"
        )
        
        keyboard = [
            [InlineKeyboardButton("➕ Agregar Contactos", callback_data=f"add_contacts_{list_id}")],
            [InlineKeyboardButton("📋 Ver Mis Listas", callback_data="view_lists")],
            [InlineKeyboardButton("🏠 Ir al Menú", callback_data="menu_email")]
        ]
    else:
        message = (
            f"❌ <b>Error al Crear Lista</b>\n\n"
            f"Ya existe una lista con el nombre:\n"
            f"'{context.user_data['list_name']}'\n\n"
            f"Por favor, elige un nombre diferente."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Intentar de Nuevo", callback_data="wizard_list")],
            [InlineKeyboardButton("🏠 Volver", callback_data="menu_email")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    # Limpiar datos temporales
    context.user_data.clear()
    
    return ConversationHandler.END


# ============================================
# FUNCIÓN DE CANCELACIÓN GENERAL
# ============================================

async def cancel_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela cualquier wizard en progreso"""
    query = update.callback_query
    if query:
        await query.answer()
    
    context.user_data.clear()
    
    message = "❌ Operación cancelada."
    
    keyboard = [[InlineKeyboardButton("🏠 Volver al Menú", callback_data="menu_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    return ConversationHandler.END
