"""
Manejadores de Comandos del Bot
Define todos los comandos disponibles y su lógica
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from decorators import admin_only, members_only, log_command
from database import MembershipDatabase
from email_sender import EmailSender
from config import Config
import csv
import io


# ============================================
# COMANDOS PÚBLICOS
# ============================================

@log_command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /start - Mensaje de bienvenida con menú interactivo
    """
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    db = MembershipDatabase()
    
    is_admin = user_id == Config.ADMIN_USER_ID
    is_member = db.is_member(user_id)
    
    welcome_message = f"👋 <b>¡Hola {first_name}!</b>\n\n"
    
    if is_admin:
        welcome_message += (
            "🔑 <b>Panel de Administrador</b>\n\n"
            "Bienvenido al sistema de Email Tranzas.\n"
            "Selecciona una opción del menú:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📧 Email Tranzas", callback_data="menu_email"),
                InlineKeyboardButton("👥 Usuarios", callback_data="menu_users")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats_menu"),
                InlineKeyboardButton("⚙️ Configuración", callback_data="menu_settings")
            ],
            [
                InlineKeyboardButton("❓ Ayuda", callback_data="help_menu")
            ]
        ]
    elif is_member:
        welcome_message += (
            "✅ <b>Membresía Activa</b>\n\n"
            "¿Qué deseas hacer hoy?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📧 Email Tranzas", callback_data="menu_email")
            ],
            [
                InlineKeyboardButton("👤 Mi Cuenta", callback_data="my_account"),
                InlineKeyboardButton("❓ Ayuda", callback_data="help_menu")
            ]
        ]
    else:
        welcome_message += (
            "⚠️ <b>Sin Membresía</b>\n\n"
            f"Tu ID: <code>{user_id}</code>\n\n"
            "Contacta al administrador para obtener acceso."
        )
        
        keyboard = [
            [
                InlineKeyboardButton("ℹ️ Más información", callback_data="info"),
                InlineKeyboardButton("❓ Ayuda", callback_data="help_menu")
            ]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, parse_mode='HTML', reply_markup=reply_markup)


@log_command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /help - Muestra ayuda y comandos disponibles
    """
    user_id = update.effective_user.id
    db = MembershipDatabase()
    
    is_admin = user_id == Config.ADMIN_USER_ID
    is_member = db.is_member(user_id)
    
    help_message = "📚 <b>Ayuda del Bot</b>\n\n"
    
    if is_admin:
        help_message += (
            "<b>🔑 Comandos de Administrador:</b>\n"
            "/addmember &lt;user_id&gt; - Añadir un nuevo miembro\n"
            "/removemember &lt;user_id&gt; - Eliminar un miembro\n"
            "/listmembers - Ver lista de todos los miembros\n"
            "/memberinfo &lt;user_id&gt; - Ver información de un miembro\n"
            "/stats - Ver estadísticas del bot\n"
            "/logs - Ver registro de actividades\n\n"
        )
    
    help_message += (
        "<b>📋 Comandos Generales:</b>\n"
        "/start - Iniciar el bot\n"
        "/help - Mostrar esta ayuda\n"
        "/status - Ver tu estado de membresía\n"
    )
    
    if is_member or is_admin:
        help_message += (
            "\n<b>⚙️ Comandos Funcionales:</b>\n"
            "/execute - Ejecutar funcionalidad principal (placeholder)\n"
        )
    
    await update.message.reply_text(help_message, parse_mode='HTML')


@log_command
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /status - Muestra el estado de membresía del usuario
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Sin username"
    first_name = update.effective_user.first_name
    db = MembershipDatabase()
    
    status_message = f"📊 <b>Estado de Membresía</b>\n\n"
    status_message += f"👤 Usuario: {first_name}\n"
    status_message += f"🆔 ID: <code>{user_id}</code>\n"
    status_message += f"📱 Username: @{username}\n\n"
    
    if user_id == Config.ADMIN_USER_ID:
        status_message += "🔑 <b>Rol:</b> Administrador\n"
        status_message += "✅ <b>Estado:</b> Acceso Total\n"
    elif db.is_member(user_id):
        member_info = db.get_member_info(user_id)
        status_message += "👥 <b>Rol:</b> Miembro\n"
        status_message += "✅ <b>Estado:</b> Activo\n"
        if member_info:
            status_message += f"📅 <b>Fecha de registro:</b> {member_info['added_date'][:10]}\n"
    else:
        status_message += "❌ <b>Estado:</b> Sin membresía\n"
        status_message += "\n⚠️ No tienes acceso a las funcionalidades del bot.\n"
        status_message += "Contacta al administrador para solicitar acceso."
    
    await update.message.reply_text(status_message, parse_mode='HTML')


# ============================================
# COMANDOS DE ADMINISTRADOR
# ============================================

@admin_only
@log_command
async def add_member_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /addmember - Añade un nuevo miembro (solo admin)
    Uso: /addmember <user_id>
    """
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /addmember <user_id>\n"
            "Ejemplo: /addmember 123456789"
        )
        return
    
    try:
        new_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ El user_id debe ser un número válido.")
        return
    
    db = MembershipDatabase()
    admin_id = update.effective_user.id
    
    if db.add_member(new_user_id, added_by=admin_id):
        await update.message.reply_text(
            f"✅ Miembro añadido exitosamente!\n\n"
            f"🆔 User ID: <code>{new_user_id}</code>\n"
            f"📅 Fecha: {db.get_member_info(new_user_id)['added_date'][:10]}\n\n"
            f"Total de miembros: {db.get_member_count()}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"⚠️ El usuario <code>{new_user_id}</code> ya es miembro.",
            parse_mode='HTML'
        )


@admin_only
@log_command
async def remove_member_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /removemember - Elimina un miembro (solo admin)
    Uso: /removemember <user_id>
    """
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /removemember <user_id>\n"
            "Ejemplo: /removemember 123456789"
        )
        return
    
    try:
        user_id_to_remove = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ El user_id debe ser un número válido.")
        return
    
    if user_id_to_remove == Config.ADMIN_USER_ID:
        await update.message.reply_text("⛔ No puedes eliminar al administrador.")
        return
    
    db = MembershipDatabase()
    admin_id = update.effective_user.id
    
    if db.remove_member(user_id_to_remove, removed_by=admin_id):
        await update.message.reply_text(
            f"✅ Miembro eliminado exitosamente!\n\n"
            f"🆔 User ID: <code>{user_id_to_remove}</code>\n\n"
            f"Total de miembros: {db.get_member_count()}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"⚠️ El usuario <code>{user_id_to_remove}</code> no es miembro.",
            parse_mode='HTML'
        )


@admin_only
@log_command
async def list_members_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /listmembers - Lista todos los miembros activos (solo admin)
    """
    db = MembershipDatabase()
    members = db.get_all_members()
    
    if not members:
        await update.message.reply_text("📝 No hay miembros registrados aún.")
        return
    
    message = f"👥 <b>Lista de Miembros</b> ({len(members)} total)\n\n"
    
    for i, member in enumerate(members, 1):
        name = member['first_name'] or member['username'] or "Sin nombre"
        username = f"@{member['username']}" if member['username'] else "Sin username"
        date = member['added_date'][:10]
        
        message += (
            f"{i}. {name}\n"
            f"   🆔 ID: <code>{member['user_id']}</code>\n"
            f"   📱 {username}\n"
            f"   📅 Registrado: {date}\n\n"
        )
    
    # Dividir el mensaje si es muy largo
    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096], parse_mode='HTML')
    else:
        await update.message.reply_text(message, parse_mode='HTML')


@admin_only
@log_command
async def member_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /memberinfo - Muestra información detallada de un miembro (solo admin)
    Uso: /memberinfo <user_id>
    """
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /memberinfo <user_id>\n"
            "Ejemplo: /memberinfo 123456789"
        )
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ El user_id debe ser un número válido.")
        return
    
    db = MembershipDatabase()
    member = db.get_member_info(user_id)
    
    if not member:
        await update.message.reply_text(
            f"⚠️ No se encontró información para el usuario <code>{user_id}</code>.",
            parse_mode='HTML'
        )
        return
    
    name = member['first_name'] or "Sin nombre"
    username = f"@{member['username']}" if member['username'] else "Sin username"
    status = "✅ Activo" if member['is_active'] else "❌ Inactivo"
    
    info_message = (
        f"👤 <b>Información del Miembro</b>\n\n"
        f"📝 Nombre: {name}\n"
        f"🆔 ID: <code>{member['user_id']}</code>\n"
        f"📱 Username: {username}\n"
        f"📅 Fecha de registro: {member['added_date'][:10]}\n"
        f"👤 Añadido por: <code>{member['added_by']}</code>\n"
        f"📊 Estado: {status}\n"
    )
    
    await update.message.reply_text(info_message, parse_mode='HTML')


@admin_only
@log_command
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /stats - Muestra estadísticas del bot (solo admin)
    """
    db = MembershipDatabase()
    total_members = db.get_member_count()
    
    stats_message = (
        f"📊 <b>Estadísticas del Bot</b>\n\n"
        f"👥 Total de miembros: {total_members}\n"
        f"🔑 Administrador: <code>{Config.ADMIN_USER_ID}</code>\n"
        f"💾 Base de datos: {Config.DATABASE_NAME}\n"
    )
    
    await update.message.reply_text(stats_message, parse_mode='HTML')


@admin_only
@log_command
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /logs - Muestra el registro de actividades recientes (solo admin)
    """
    db = MembershipDatabase()
    logs = db.get_activity_log(limit=20)
    
    if not logs:
        await update.message.reply_text("📝 No hay actividades registradas aún.")
        return
    
    message = f"📋 <b>Registro de Actividades</b> (últimas 20)\n\n"
    
    for log in logs:
        timestamp = log['timestamp'][:19].replace('T', ' ')
        action_emoji = "➕" if log['action'] == "MEMBER_ADDED" else "➖"
        action_text = "Añadido" if log['action'] == "MEMBER_ADDED" else "Eliminado"
        
        message += (
            f"{action_emoji} {action_text}\n"
            f"   👤 Usuario: <code>{log['user_id']}</code>\n"
            f"   🔧 Por: <code>{log['performed_by']}</code>\n"
            f"   🕐 {timestamp}\n\n"
        )
    
    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096], parse_mode='HTML')
    else:
        await update.message.reply_text(message, parse_mode='HTML')


# ============================================
# COMANDOS FUNCIONALES (SOLO MIEMBROS)
# ============================================

@members_only
@log_command
async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /execute - Menú principal de Email Tranzas
    """
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    is_admin = user_id == Config.ADMIN_USER_ID
    
    menu_message = (
        f"📧 <b>Sistema de Email Tranzas</b>\n\n"
        f"👤 Usuario: {first_name}\n\n"
    )
    
    if is_admin:
        menu_message += (
            "<b>📋 Comandos Disponibles:</b>\n\n"
            "<b>Configuración:</b>\n"
            "/setsmtp - Configurar servidor SMTP\n"
            "/smtpstatus - Ver configuración SMTP\n\n"
            "<b>Listas de Correos:</b>\n"
            "/createlist &lt;nombre&gt; - Crear lista\n"
            "/addrecipient &lt;list_id&gt; &lt;email&gt; &lt;nombre&gt; - Agregar destinatario\n"
            "/uploadlist - Cargar lista desde CSV\n"
            "/listslists - Ver todas las listas\n"
            "/viewrecipients &lt;list_id&gt; - Ver destinatarios de una lista\n\n"
            "<b>Plantillas:</b>\n"
            "/createtemplate - Crear plantilla de email\n"
            "/listtemplates - Ver todas las plantillas\n\n"
            "<b>Campañas:</b>\n"
            "/sendcampaign - Crear y enviar campaña\n"
            "/campaigns - Ver todas las campañas\n"
            "/campaignstats &lt;campaign_id&gt; - Ver estadísticas\n"
        )
    else:
        menu_message += (
            "<b>📋 Comandos Disponibles:</b>\n\n"
            "/listslists - Ver listas de correos\n"
            "/listtemplates - Ver plantillas\n"
            "/campaigns - Ver campañas enviadas\n"
        )
    
    await update.message.reply_text(menu_message, parse_mode='HTML')


# ============================================
# COMANDOS DE EMAIL TRANZAS
# ============================================

@admin_only
@log_command
async def set_smtp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /setsmtp - Configura el servidor SMTP
    Formato interactivo paso a paso
    """
    await update.message.reply_text(
        "📧 <b>Configuración de SMTP</b>\n\n"
        "Por favor, proporciona la configuración en el siguiente formato:\n\n"
        "<code>/setsmtp servidor puerto usuario contraseña email_remitente nombre_remitente</code>\n\n"
        "<b>Ejemplo para Gmail:</b>\n"
        "<code>/setsmtp smtp.gmail.com 587 tu@gmail.com tu_contraseña_app tu@gmail.com \"Tu Nombre\"</code>\n\n"
        "<b>⚠️ Nota:</b> Para Gmail, necesitas una contraseña de aplicación.\n"
        "Ve a: Configuración → Seguridad → Verificación en dos pasos → Contraseñas de aplicaciones",
        parse_mode='HTML'
    )
    
    if not context.args or len(context.args) < 6:
        return
    
    server = context.args[0]
    port = int(context.args[1])
    username = context.args[2]
    password = context.args[3]
    sender_email = context.args[4]
    sender_name = ' '.join(context.args[5:])
    
    email_service = EmailSender()
    
    if email_service.set_smtp_config(server, port, username, password, 
                                     sender_email, sender_name):
        await update.message.reply_text(
            "✅ <b>Configuración SMTP guardada exitosamente!</b>\n\n"
            f"📮 Servidor: {server}:{port}\n"
            f"👤 Usuario: {username}\n"
            f"📧 Email remitente: {sender_email}\n"
            f"✍️ Nombre remitente: {sender_name}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("❌ Error al guardar la configuración SMTP.")


@members_only
@log_command
async def smtp_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /smtpstatus - Muestra el estado de la configuración SMTP
    """
    email_service = EmailSender()
    config = email_service.get_smtp_config()
    
    if not config:
        await update.message.reply_text(
            "⚠️ <b>SMTP no configurado</b>\n\n"
            "Usa /setsmtp para configurar el servidor SMTP.",
            parse_mode='HTML'
        )
        return
    
    # Ocultar contraseña
    password_masked = '*' * len(config['smtp_password']) if config['smtp_password'] else 'No configurada'
    
    status_message = (
        "📧 <b>Estado de Configuración SMTP</b>\n\n"
        f"🌐 Servidor: {config['smtp_server']}\n"
        f"🔌 Puerto: {config['smtp_port']}\n"
        f"👤 Usuario: {config['smtp_username']}\n"
        f"🔒 Contraseña: {password_masked}\n"
        f"📮 Email remitente: {config['sender_email']}\n"
        f"✍️ Nombre remitente: {config['sender_name']}\n"
        f"🔐 TLS: {'Activado' if config['use_tls'] else 'Desactivado'}\n"
        f"⏱ Delay entre emails: {config['delay_between_emails']}s"
    )
    
    await update.message.reply_text(status_message, parse_mode='HTML')


@admin_only
@log_command
async def create_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /createlist - Crea una nueva lista de correos
    Uso: /createlist <nombre> <descripción>
    """
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /createlist &lt;nombre&gt; &lt;descripción&gt;\n"
            "Ejemplo: /createlist clientes \"Lista de clientes potenciales\"",
            parse_mode='HTML'
        )
        return
    
    name = context.args[0]
    description = ' '.join(context.args[1:])
    user_id = update.effective_user.id
    
    email_service = EmailSender()
    list_id = email_service.create_email_list(name, description, user_id)
    
    if list_id:
        await update.message.reply_text(
            f"✅ <b>Lista creada exitosamente!</b>\n\n"
            f"📋 Nombre: {name}\n"
            f"📝 Descripción: {description}\n"
            f"🆔 ID de lista: <code>{list_id}</code>\n\n"
            f"Ahora puedes agregar destinatarios con:\n"
            f"<code>/addrecipient {list_id} email@ejemplo.com \"Nombre\"</code>",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(f"⚠️ Ya existe una lista con el nombre '{name}'.")


@admin_only
@log_command
async def add_recipient_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /addrecipient - Agrega un destinatario a una lista
    Uso: /addrecipient <list_id> <email> <nombre>
    """
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /addrecipient &lt;list_id&gt; &lt;email&gt; &lt;nombre&gt;\n"
            "Ejemplo: /addrecipient 1 cliente@ejemplo.com \"Juan Pérez\"",
            parse_mode='HTML'
        )
        return
    
    try:
        list_id = int(context.args[0])
        email = context.args[1]
        name = ' '.join(context.args[2:])
        
        email_service = EmailSender()
        
        if email_service.add_recipient(list_id, email, name):
            await update.message.reply_text(
                f"✅ <b>Destinatario agregado!</b>\n\n"
                f"📧 Email: {email}\n"
                f"👤 Nombre: {name}\n"
                f"📋 Lista ID: {list_id}",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "⚠️ El email ya existe en esta lista o la lista no existe."
            )
    except ValueError:
        await update.message.reply_text("❌ El list_id debe ser un número válido.")


@members_only
@log_command
async def lists_lists_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /listslists - Muestra todas las listas de correos
    """
    email_service = EmailSender()
    lists = email_service.get_all_lists()
    
    if not lists:
        await update.message.reply_text("📝 No hay listas de correos creadas aún.")
        return
    
    message = f"📋 <b>Listas de Correos</b> ({len(lists)} total)\n\n"
    
    for lst in lists:
        message += (
            f"🆔 <b>ID:</b> <code>{lst['id']}</code>\n"
            f"📌 <b>Nombre:</b> {lst['name']}\n"
            f"📝 <b>Descripción:</b> {lst['description']}\n"
            f"👥 <b>Destinatarios:</b> {lst['recipient_count']}\n"
            f"📅 <b>Creado:</b> {lst['created_date'][:10]}\n\n"
        )
    
    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096], parse_mode='HTML')
    else:
        await update.message.reply_text(message, parse_mode='HTML')


@members_only
@log_command
async def view_recipients_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /viewrecipients - Ver destinatarios de una lista
    Uso: /viewrecipients <list_id>
    """
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /viewrecipients &lt;list_id&gt;\n"
            "Ejemplo: /viewrecipients 1",
            parse_mode='HTML'
        )
        return
    
    try:
        list_id = int(context.args[0])
        email_service = EmailSender()
        recipients = email_service.get_list_recipients(list_id)
        
        if not recipients:
            await update.message.reply_text(
                f"📝 La lista {list_id} no tiene destinatarios o no existe."
            )
            return
        
        message = f"👥 <b>Destinatarios de Lista {list_id}</b> ({len(recipients)} total)\n\n"
        
        for i, recipient in enumerate(recipients, 1):
            message += (
                f"{i}. {recipient['name'] or 'Sin nombre'}\n"
                f"   📧 {recipient['email']}\n"
                f"   📅 Agregado: {recipient['added_date'][:10]}\n\n"
            )
        
        if len(message) > 4096:
            for i in range(0, len(message), 4096):
                await update.message.reply_text(message[i:i+4096], parse_mode='HTML')
        else:
            await update.message.reply_text(message, parse_mode='HTML')
            
    except ValueError:
        await update.message.reply_text("❌ El list_id debe ser un número válido.")


@admin_only
@log_command
async def create_template_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /createtemplate - Crea una plantilla de email
    Uso interactivo
    """
    await update.message.reply_text(
        "📄 <b>Crear Plantilla de Email</b>\n\n"
        "Formato:\n"
        "<code>/createtemplate nombre|||asunto|||cuerpo</code>\n\n"
        "<b>Ejemplo:</b>\n"
        "<code>/createtemplate bienvenida|||¡Bienvenido!|||Hola {{name}}, gracias por unirte a nosotros.</code>\n\n"
        "<b>Variable disponible:</b>\n"
        "• Usa <code>{{name}}</code> donde quieras que aparezca el nombre del destinatario\n\n"
        "⚠️ Usa ||| (tres barras verticales) para separar nombre, asunto y cuerpo",
        parse_mode='HTML'
    )
    
    if not context.args:
        return
    
    full_text = ' '.join(context.args)
    parts = full_text.split('|||')
    
    if len(parts) < 3:
        await update.message.reply_text(
            "❌ Formato incorrecto. Usa ||| para separar nombre, asunto y cuerpo."
        )
        return
    
    name = parts[0].strip()
    subject = parts[1].strip()
    body = parts[2].strip()
    user_id = update.effective_user.id
    
    email_service = EmailSender()
    template_id = email_service.create_template(name, subject, body, user_id)
    
    if template_id:
        await update.message.reply_text(
            f"✅ <b>Plantilla creada exitosamente!</b>\n\n"
            f"📄 Nombre: {name}\n"
            f"📧 Asunto: {subject}\n"
            f"🆔 ID de plantilla: <code>{template_id}</code>\n\n"
            f"Puedes usar esta plantilla al crear una campaña.",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(f"⚠️ Ya existe una plantilla con el nombre '{name}'.")


@members_only
@log_command
async def list_templates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /listtemplates - Lista todas las plantillas
    """
    email_service = EmailSender()
    templates = email_service.get_all_templates()
    
    if not templates:
        await update.message.reply_text("📝 No hay plantillas creadas aún.")
        return
    
    message = f"📄 <b>Plantillas de Email</b> ({len(templates)} total)\n\n"
    
    for template in templates:
        message += (
            f"🆔 <b>ID:</b> <code>{template['id']}</code>\n"
            f"📌 <b>Nombre:</b> {template['name']}\n"
            f"📧 <b>Asunto:</b> {template['subject']}\n"
            f"📅 <b>Creado:</b> {template['created_date'][:10]}\n\n"
        )
    
    await update.message.reply_text(message, parse_mode='HTML')


@admin_only
@log_command
async def send_campaign_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /sendcampaign - Crea y envía una campaña
    Uso: /sendcampaign <nombre> <template_id> <list_id>
    """
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /sendcampaign &lt;nombre&gt; &lt;template_id&gt; &lt;list_id&gt;\n"
            "Ejemplo: /sendcampaign \"Campaña Navidad\" 1 1\n\n"
            "Usa /listtemplates y /listslists para ver IDs disponibles.",
            parse_mode='HTML'
        )
        return
    
    try:
        name = context.args[0]
        template_id = int(context.args[1])
        list_id = int(context.args[2])
        user_id = update.effective_user.id
        
        email_service = EmailSender()
        
        # Crear campaña
        campaign_id = email_service.create_campaign(name, template_id, list_id, user_id)
        
        if not campaign_id:
            await update.message.reply_text("❌ Error al crear la campaña.")
            return
        
        await update.message.reply_text(
            f"🚀 <b>Iniciando campaña...</b>\n\n"
            f"Esto puede tomar varios minutos dependiendo del número de destinatarios.\n"
            f"Por favor espera...",
            parse_mode='HTML'
        )
        
        # Enviar campaña
        result = email_service.send_campaign(campaign_id)
        
        if result['success']:
            await update.message.reply_text(
                f"✅ <b>Campaña enviada exitosamente!</b>\n\n"
                f"📊 <b>Estadísticas:</b>\n"
                f"✉️ Total enviados: {result['sent']}\n"
                f"❌ Fallidos: {result['failed']}\n"
                f"📝 Total destinatarios: {result['total']}\n"
                f"🆔 ID de campaña: <code>{campaign_id}</code>",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"❌ <b>Error al enviar la campaña</b>\n\n"
                f"Error: {result.get('error', 'Desconocido')}",
                parse_mode='HTML'
            )
            
    except ValueError:
        await update.message.reply_text("❌ Los IDs deben ser números válidos.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


@members_only
@log_command
async def campaigns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /campaigns - Lista todas las campañas
    """
    email_service = EmailSender()
    campaigns = email_service.get_all_campaigns()
    
    if not campaigns:
        await update.message.reply_text("📝 No hay campañas creadas aún.")
        return
    
    message = f"📨 <b>Campañas de Email</b> ({len(campaigns)} total)\n\n"
    
    for campaign in campaigns:
        status_emoji = {
            'PENDING': '⏳',
            'RUNNING': '🔄',
            'COMPLETED': '✅',
            'FAILED': '❌'
        }.get(campaign['status'], '❓')
        
        message += (
            f"🆔 <b>ID:</b> <code>{campaign['id']}</code>\n"
            f"📌 <b>Nombre:</b> {campaign['name']}\n"
            f"{status_emoji} <b>Estado:</b> {campaign['status']}\n"
            f"📄 <b>Plantilla:</b> {campaign['template_name']}\n"
            f"📋 <b>Lista:</b> {campaign['list_name']}\n"
            f"📊 <b>Enviados:</b> {campaign['sent_count']}/{campaign['total_recipients']}\n"
            f"📅 <b>Creado:</b> {campaign['created_date'][:10]}\n\n"
        )
    
    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096], parse_mode='HTML')
    else:
        await update.message.reply_text(message, parse_mode='HTML')


@members_only
@log_command
async def campaign_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /campaignstats - Ver estadísticas de una campaña
    Uso: /campaignstats <campaign_id>
    """
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Uso incorrecto.\n\n"
            "Formato: /campaignstats &lt;campaign_id&gt;\n"
            "Ejemplo: /campaignstats 1",
            parse_mode='HTML'
        )
        return
    
    try:
        campaign_id = int(context.args[0])
        email_service = EmailSender()
        stats = email_service.get_campaign_stats(campaign_id)
        
        if not stats:
            await update.message.reply_text(f"⚠️ No se encontró la campaña {campaign_id}.")
            return
        
        status_emoji = {
            'PENDING': '⏳',
            'RUNNING': '🔄',
            'COMPLETED': '✅',
            'FAILED': '❌'
        }.get(stats['status'], '❓')
        
        success_rate = (stats['sent_count'] / stats['total_recipients'] * 100) if stats['total_recipients'] > 0 else 0
        
        stats_message = (
            f"📊 <b>Estadísticas de Campaña</b>\n\n"
            f"🆔 <b>ID:</b> <code>{stats['id']}</code>\n"
            f"📌 <b>Nombre:</b> {stats['name']}\n"
            f"{status_emoji} <b>Estado:</b> {stats['status']}\n\n"
            f"📄 <b>Plantilla:</b> {stats['template_name']}\n"
            f"📋 <b>Lista:</b> {stats['list_name']}\n\n"
            f"<b>Resultados:</b>\n"
            f"✉️ Total enviados: {stats['sent_count']}\n"
            f"❌ Fallidos: {stats['failed_count']}\n"
            f"📝 Total destinatarios: {stats['total_recipients']}\n"
            f"📈 Tasa de éxito: {success_rate:.1f}%\n\n"
            f"📅 <b>Creado:</b> {stats['created_date'][:10]}\n"
        )
        
        if stats['started_date']:
            stats_message += f"🚀 <b>Iniciado:</b> {stats['started_date'][:19]}\n"
        if stats['completed_date']:
            stats_message += f"✅ <b>Completado:</b> {stats['completed_date'][:19]}\n"
        
        await update.message.reply_text(stats_message, parse_mode='HTML')
        
    except ValueError:
        await update.message.reply_text("❌ El campaign_id debe ser un número válido.")


# ============================================
# MANEJADOR DE MENSAJES NO RECONOCIDOS
# ============================================

@log_command
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejador para comandos no reconocidos
    """
    await update.message.reply_text(
        "❓ Comando no reconocido.\n\n"
        "Usa /help para ver los comandos disponibles."
    )


# ============================================
# MANEJADOR DE ERRORES
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejador global de errores
    """
    print(f"[ERROR] Ocurrió un error: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Ocurrió un error al procesar tu solicitud.\n"
            "Por favor, intenta nuevamente o contacta al administrador."
        )
