"""
Handlers de Callbacks Mejorados
Implementa todos los callbacks faltantes con funcionalidad completa
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from email_sender import EmailSender
from database import MembershipDatabase
from config import Config
import smtplib
import ssl


# ============================================
# TEST SMTP CONNECTION
# ============================================

async def test_smtp_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prueba la conexión SMTP"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🧪 <b>Probando Conexión SMTP...</b>\n\n"
        "Por favor espera...",
        parse_mode='HTML'
    )
    
    email_service = EmailSender()
    config = email_service.get_smtp_config()
    
    if not config:
        message = "❌ No hay configuración SMTP guardada."
        keyboard = [
            [InlineKeyboardButton("⚙️ Configurar", callback_data="wizard_smtp")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="view_smtp")]
        ]
    else:
        try:
            # Intentar conectar
            context_ssl = ssl.create_default_context()
            with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=10) as server:
                if config['use_tls']:
                    server.starttls(context=context_ssl)
                server.login(config['smtp_username'], config['smtp_password'])
            
            message = (
                "✅ <b>¡Conexión Exitosa!</b>\n\n"
                f"📮 Servidor: {config['smtp_server']}:{config['smtp_port']}\n"
                f"👤 Usuario: {config['smtp_username']}\n\n"
                f"Tu configuración SMTP está funcionando correctamente.\n"
                f"Puedes enviar campañas sin problemas."
            )
            keyboard = [
                [InlineKeyboardButton("🚀 Enviar Campaña", callback_data="wizard_campaign")],
                [InlineKeyboardButton("⬅️ Volver", callback_data="view_smtp")]
            ]
        except smtplib.SMTPAuthenticationError:
            message = (
                "❌ <b>Error de Autenticación</b>\n\n"
                "El usuario o contraseña son incorrectos.\n\n"
                "<b>💡 Para Gmail:</b>\n"
                "Debes usar una 'Contraseña de aplicación',\n"
                "no tu contraseña normal.\n\n"
                "Ve a: myaccount.google.com/apppasswords"
            )
            keyboard = [
                [InlineKeyboardButton("🔄 Reconfigurar", callback_data="wizard_smtp")],
                [InlineKeyboardButton("⬅️ Volver", callback_data="view_smtp")]
            ]
        except smtplib.SMTPConnectError:
            message = (
                "❌ <b>Error de Conexión</b>\n\n"
                f"No se pudo conectar al servidor:\n"
                f"{config['smtp_server']}:{config['smtp_port']}\n\n"
                "Verifica tu conexión a internet y\n"
                "que el servidor y puerto sean correctos."
            )
            keyboard = [
                [InlineKeyboardButton("🔄 Reconfigurar", callback_data="wizard_smtp")],
                [InlineKeyboardButton("⬅️ Volver", callback_data="view_smtp")]
            ]
        except Exception as e:
            message = (
                f"❌ <b>Error Inesperado</b>\n\n"
                f"Detalle: {str(e)}\n\n"
                f"Por favor, verifica tu configuración."
            )
            keyboard = [
                [InlineKeyboardButton("🔄 Reconfigurar", callback_data="wizard_smtp")],
                [InlineKeyboardButton("⬅️ Volver", callback_data="view_smtp")]
            ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# DETAIL VIEWS
# ============================================

async def show_template_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, template_id: int):
    """Muestra el detalle de una plantilla"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    template = email_service.get_template(template_id)
    
    if not template:
        await query.answer("❌ Plantilla no encontrada", show_alert=True)
        return
    
    # Vista previa del cuerpo
    body_preview = template['body'][:300] + "..." if len(template['body']) > 300 else template['body']
    body_preview = body_preview.replace('<', '&lt;').replace('>', '&gt;')
    
    message = (
        f"📄 <b>{template['name']}</b>\n\n"
        f"📧 <b>Asunto:</b>\n{template['subject']}\n\n"
        f"📝 <b>Cuerpo (vista previa):</b>\n"
        f"<code>{body_preview}</code>\n\n"
        f"📅 <b>Creada:</b> {template['created_date'][:10]}\n"
        f"🆔 <b>ID:</b> {template_id}"
    )
    
    user_id = update.effective_user.id
    is_admin = user_id == Config.ADMIN_USER_ID
    
    keyboard = []
    
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("🚀 Usar en Campaña", callback_data="wizard_campaign")
        ])
        keyboard.append([
            InlineKeyboardButton("🗑️ Eliminar", callback_data=f"delete_template_{template_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("⬅️ Volver a Plantillas", callback_data="view_templates")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


async def show_campaign_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, campaign_id: int):
    """Muestra el detalle de una campaña"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    stats = email_service.get_campaign_stats(campaign_id)
    
    if not stats:
        await query.answer("❌ Campaña no encontrada", show_alert=True)
        return
    
    status_emoji = {
        'PENDING': '⏳',
        'RUNNING': '🔄',
        'COMPLETED': '✅',
        'FAILED': '❌'
    }.get(stats['status'], '❓')
    
    success_rate = (stats['sent_count'] / stats['total_recipients'] * 100) if stats['total_recipients'] > 0 else 0
    
    message = (
        f"📊 <b>Detalles de Campaña</b>\n\n"
        f"📝 <b>Nombre:</b> {stats['name']}\n"
        f"{status_emoji} <b>Estado:</b> {stats['status']}\n\n"
        f"📄 <b>Plantilla:</b> {stats['template_name']}\n"
        f"📋 <b>Lista:</b> {stats['list_name']}\n\n"
        f"<b>📊 Resultados:</b>\n"
        f"✉️ Enviados: {stats['sent_count']}\n"
        f"❌ Fallidos: {stats['failed_count']}\n"
        f"📝 Total: {stats['total_recipients']}\n"
        f"📈 Éxito: {success_rate:.1f}%\n\n"
        f"📅 <b>Creado:</b> {stats['created_date'][:10]}"
    )
    
    if stats['started_date']:
        message += f"\n🚀 <b>Iniciado:</b> {stats['started_date'][:19]}"
    if stats['completed_date']:
        message += f"\n✅ <b>Completado:</b> {stats['completed_date'][:19]}"
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Volver a Campañas", callback_data="view_campaigns")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# HELP SECTIONS
# ============================================

async def show_help_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    """Muestra ayuda sobre un tema específico"""
    query = update.callback_query
    await query.answer()
    
    help_content = {
        'help_email_tranzas': {
            'title': '📧 Email Tranzas',
            'content': (
                "El sistema de Email Tranzas te permite:\n\n"
                "✅ Gestionar listas de contactos\n"
                "✅ Crear plantillas reutilizables\n"
                "✅ Enviar campañas masivas\n"
                "✅ Ver estadísticas detalladas\n\n"
                "<b>Flujo básico:</b>\n"
                "1. Configura tu email (SMTP)\n"
                "2. Crea una lista de contactos\n"
                "3. Crea una plantilla\n"
                "4. Envía tu campaña\n\n"
                "Todo está guiado paso a paso con botones."
            )
        },
        'help_lists': {
            'title': '📋 Gestión de Listas',
            'content': (
                "<b>¿Qué es una lista?</b>\n"
                "Una lista es un grupo de contactos a los que\n"
                "enviarás tus campañas.\n\n"
                "<b>Cómo crear una lista:</b>\n"
                "1. Click en 'Crear Lista'\n"
                "2. Escribe un nombre\n"
                "3. Agrega contactos\n\n"
                "<b>Agregar contactos:</b>\n"
                "• Uno por uno manualmente\n"
                "• Importar desde CSV (próximamente)\n\n"
                "Puedes tener múltiples listas para\n"
                "diferentes tipos de destinatarios."
            )
        },
        'help_templates': {
            'title': '📄 Crear Plantillas',
            'content': (
                "<b>¿Qué es una plantilla?</b>\n"
                "Es un diseño de email que puedes\n"
                "reutilizar múltiples veces.\n\n"
                "<b>Partes de una plantilla:</b>\n"
                "• Nombre: Para identificarla\n"
                "• Asunto: Lo que ve el destinatario\n"
                "• Cuerpo: Contenido del email\n\n"
                "<b>Personalización:</b>\n"
                "Usa <code>{{name}}</code> y se reemplazará\n"
                "automáticamente con el nombre del contacto.\n\n"
                "<b>HTML:</b>\n"
                "Puedes usar etiquetas HTML en el contenido."
            )
        },
        'help_campaigns': {
            'title': '🚀 Enviar Campañas',
            'content': (
                "<b>Requisitos previos:</b>\n"
                "✅ Email configurado (SMTP)\n"
                "✅ Lista con contactos\n"
                "✅ Plantilla creada\n\n"
                "<b>Proceso de envío:</b>\n"
                "1. Selecciona una lista\n"
                "2. Selecciona una plantilla\n"
                "3. Dale un nombre a la campaña\n"
                "4. Confirma y envía\n\n"
                "<b>Durante el envío:</b>\n"
                "• No cierres el bot\n"
                "• El proceso puede tardar varios minutos\n"
                "• Recibirás confirmación al finalizar\n\n"
                "Puedes ver estadísticas después."
            )
        },
        'help_faq': {
            'title': '❓ Preguntas Frecuentes',
            'content': (
                "<b>¿Por qué Gmail rechaza mi contraseña?</b>\n"
                "Debes usar una 'Contraseña de aplicación',\n"
                "no tu contraseña normal.\n\n"
                "<b>¿Cuántos emails puedo enviar?</b>\n"
                "Depende de tu proveedor:\n"
                "• Gmail: 500/día (gratis)\n"
                "• Otros: Consulta sus límites\n\n"
                "<b>¿Los emails llegan a spam?</b>\n"
                "Depende del contenido. Buenas prácticas:\n"
                "• No uses palabras como 'GRATIS'\n"
                "• Incluye opción de desuscripción\n"
                "• Envía solo a quien dio permiso\n\n"
                "<b>¿Puedo cancelar un envío?</b>\n"
                "No, una vez iniciado no se puede detener."
            )
        }
    }
    
    help_info = help_content.get(topic, {
        'title': '❓ Ayuda',
        'content': 'Información no disponible.'
    })
    
    message = f"<b>{help_info['title']}</b>\n\n{help_info['content']}"
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Volver a Ayuda", callback_data="help_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# VIEW ALL WITH PAGINATION
# ============================================

async def show_all_members_with_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra todos los miembros con botones interactivos"""
    query = update.callback_query
    await query.answer()
    
    db = MembershipDatabase()
    members = db.get_all_members()
    
    if not members:
        message = "📝 No hay miembros registrados aún."
        keyboard = [
            [InlineKeyboardButton("➕ Agregar Miembro", callback_data="wizard_add_member")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu_users")]
        ]
    else:
        message = f"👥 <b>Todos los Miembros</b> ({len(members)} total)\n\n"
        
        keyboard = []
        
        # Mostrar hasta 10 miembros con botones
        for member in members[:10]:
            name = member['first_name'] or member['username'] or "Sin nombre"
            keyboard.append([
                InlineKeyboardButton(
                    f"👤 {name} (ID: {member['user_id']})",
                    callback_data=f"member_info_{member['user_id']}"
                )
            ])
        
        if len(members) > 10:
            message += f"\n<i>Mostrando 10 de {len(members)}. Usa /listmembers para ver todos.</i>\n"
        
        keyboard.append([
            InlineKeyboardButton("➕ Agregar", callback_data="wizard_add_member"),
            InlineKeyboardButton("➖ Eliminar", callback_data="wizard_remove_member")
        ])
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="menu_users")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


async def show_member_info_button(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Muestra información de un miembro desde botón"""
    query = update.callback_query
    await query.answer()
    
    db = MembershipDatabase()
    member = db.get_member_info(user_id)
    
    if not member:
        await query.answer("❌ Miembro no encontrado", show_alert=True)
        return
    
    name = member['first_name'] or "Sin nombre"
    username = f"@{member['username']}" if member['username'] else "Sin username"
    status = "✅ Activo" if member['is_active'] else "❌ Inactivo"
    
    message = (
        f"👤 <b>Información del Miembro</b>\n\n"
        f"📝 Nombre: {name}\n"
        f"🆔 ID: <code>{member['user_id']}</code>\n"
        f"📱 Username: {username}\n"
        f"📅 Registro: {member['added_date'][:10]}\n"
        f"👤 Añadido por: <code>{member['added_by']}</code>\n"
        f"📊 Estado: {status}"
    )
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Volver a Miembros", callback_data="list_all_members")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# VIEW ACTIVITY LOGS
# ============================================

async def show_activity_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los registros de actividad"""
    query = update.callback_query
    await query.answer()
    
    db = MembershipDatabase()
    logs = db.get_activity_log(limit=15)
    
    if not logs:
        message = "📝 No hay actividades registradas aún."
    else:
        message = f"📋 <b>Actividad Reciente</b> (últimas 15)\n\n"
        
        for log in logs:
            timestamp = log['timestamp'][:19].replace('T', ' ')
            action_emoji = "➕" if log['action'] == "MEMBER_ADDED" else "➖"
            action_text = "Añadido" if log['action'] == "MEMBER_ADDED" else "Eliminado"
            
            message += (
                f"{action_emoji} {action_text}\n"
                f"   Usuario: <code>{log['user_id']}</code>\n"
                f"   Por: <code>{log['performed_by']}</code>\n"
                f"   🕐 {timestamp}\n\n"
            )
    
    keyboard = [
        [InlineKeyboardButton("🔄 Actualizar", callback_data="view_logs")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="menu_users")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
