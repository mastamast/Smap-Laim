"""
Sistema de Menús Interactivos con Botones
Proporciona navegación intuitiva mediante InlineKeyboards
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from database import MembershipDatabase
from email_sender import EmailSender


# ============================================
# MENÚ PRINCIPAL
# ============================================

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú principal con botones interactivos"""
    query = update.callback_query
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    db = MembershipDatabase()
    is_admin = user_id == Config.ADMIN_USER_ID
    is_member = db.is_member(user_id)
    
    message = f"👋 <b>¡Hola {first_name}!</b>\n\n"
    
    if is_admin:
        message += "🔑 <b>Panel de Administrador</b>\n\n"
        message += "Selecciona una opción:"
        
        keyboard = [
            [
                InlineKeyboardButton("📧 Email Tranzas", callback_data="menu_email"),
                InlineKeyboardButton("👥 Usuarios", callback_data="menu_users")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats"),
                InlineKeyboardButton("⚙️ Configuración", callback_data="menu_settings")
            ],
            [
                InlineKeyboardButton("❓ Ayuda", callback_data="help")
            ]
        ]
    elif is_member:
        message += "✅ <b>Membresía Activa</b>\n\n"
        message += "Selecciona una opción:"
        
        keyboard = [
            [
                InlineKeyboardButton("📧 Email Tranzas", callback_data="menu_email")
            ],
            [
                InlineKeyboardButton("👤 Mi Cuenta", callback_data="my_account"),
                InlineKeyboardButton("❓ Ayuda", callback_data="help")
            ]
        ]
    else:
        message += (
            "⚠️ <b>Sin Membresía</b>\n\n"
            f"Tu ID: <code>{user_id}</code>\n\n"
            "Contacta al administrador para obtener acceso."
        )
        
        keyboard = [
            [
                InlineKeyboardButton("ℹ️ Más información", callback_data="info"),
                InlineKeyboardButton("❓ Ayuda", callback_data="help")
            ]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.answer()
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# MENÚ EMAIL TRANZAS
# ============================================

async def show_email_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de Email Tranzas"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    is_admin = user_id == Config.ADMIN_USER_ID
    
    # Verificar configuración
    email_service = EmailSender()
    smtp_config = email_service.get_smtp_config()
    lists = email_service.get_all_lists()
    templates = email_service.get_all_templates()
    
    # Estado del sistema
    status_lines = []
    if smtp_config:
        status_lines.append("✅ Email configurado")
    else:
        status_lines.append("⚠️ Email no configurado")
    
    status_lines.append(f"📋 {len(lists)} lista(s)")
    status_lines.append(f"📄 {len(templates)} plantilla(s)")
    
    message = (
        f"📧 <b>Email Tranzas</b>\n\n"
        f"Estado: {' • '.join(status_lines)}\n\n"
    )
    
    keyboard = []
    
    # Botón destacado para nuevos usuarios
    if not smtp_config and is_admin:
        message += "🎯 <b>Para empezar:</b> Configura tu email\n\n"
        keyboard.append([
            InlineKeyboardButton("🚀 Configurar Email (Paso 1)", callback_data="wizard_smtp")
        ])
        keyboard.append([
            InlineKeyboardButton("ℹ️ ¿Qué es SMTP?", callback_data="help_smtp")
        ])
    elif smtp_config and len(lists) == 0 and is_admin:
        message += "🎯 <b>Siguiente paso:</b> Crea tu primera lista\n\n"
        keyboard.append([
            InlineKeyboardButton("➕ Crear Mi Primera Lista", callback_data="wizard_list")
        ])
    elif smtp_config and len(lists) > 0 and len(templates) == 0 and is_admin:
        message += "🎯 <b>Siguiente paso:</b> Crea una plantilla\n\n"
        keyboard.append([
            InlineKeyboardButton("➕ Crear Plantilla", callback_data="wizard_template")
        ])
    elif smtp_config and len(lists) > 0 and len(templates) > 0:
        message += "✅ <b>Todo listo!</b> Puedes enviar campañas\n\n"
        keyboard.append([
            InlineKeyboardButton("🚀 Enviar Campaña", callback_data="wizard_campaign")
        ])
    
    # Opciones principales
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("📋 Mis Listas", callback_data="view_lists"),
            InlineKeyboardButton("📄 Plantillas", callback_data="view_templates")
        ])
        keyboard.append([
            InlineKeyboardButton("📨 Campañas", callback_data="view_campaigns"),
            InlineKeyboardButton("⚙️ Config Email", callback_data="view_smtp")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("📋 Ver Listas", callback_data="view_lists"),
            InlineKeyboardButton("📄 Ver Plantillas", callback_data="view_templates")
        ])
        keyboard.append([
            InlineKeyboardButton("📨 Ver Campañas", callback_data="view_campaigns")
        ])
    
    # Botón volver
    keyboard.append([
        InlineKeyboardButton("⬅️ Volver al Menú Principal", callback_data="main_menu")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# MENÚ USUARIOS (ADMIN)
# ============================================

async def show_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de gestión de usuarios"""
    query = update.callback_query
    await query.answer()
    
    db = MembershipDatabase()
    member_count = db.get_member_count()
    
    message = (
        f"👥 <b>Gestión de Usuarios</b>\n\n"
        f"Total de miembros: {member_count}\n\n"
        f"Selecciona una opción:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📋 Ver Todos los Miembros", callback_data="list_all_members")
        ],
        [
            InlineKeyboardButton("➕ Agregar Miembro", callback_data="wizard_add_member"),
            InlineKeyboardButton("➖ Eliminar Miembro", callback_data="wizard_remove_member")
        ],
        [
            InlineKeyboardButton("🔍 Buscar Usuario", callback_data="search_member")
        ],
        [
            InlineKeyboardButton("📊 Ver Actividad", callback_data="view_logs")
        ],
        [
            InlineKeyboardButton("⬅️ Volver", callback_data="main_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# VER LISTAS
# ============================================

async def show_lists_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra todas las listas de correos"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    lists = email_service.get_all_lists()
    
    user_id = update.effective_user.id
    is_admin = user_id == Config.ADMIN_USER_ID
    
    if not lists:
        message = (
            "📋 <b>Mis Listas de Correos</b>\n\n"
            "No tienes listas creadas aún.\n\n"
        )
        
        keyboard = []
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("➕ Crear Mi Primera Lista", callback_data="wizard_list")
            ])
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
        ])
    else:
        message = f"📋 <b>Mis Listas de Correos</b>\n\n"
        message += f"Total: {len(lists)} lista(s)\n\n"
        
        keyboard = []
        
        # Mostrar hasta 5 listas como botones
        for lst in lists[:5]:
            recipients_text = f"{lst['recipient_count']} contacto(s)"
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 {lst['name']} - {recipients_text}",
                    callback_data=f"list_detail_{lst['id']}"
                )
            ])
        
        if len(lists) > 5:
            keyboard.append([
                InlineKeyboardButton("📄 Ver todas las listas...", callback_data="list_all_lists")
            ])
        
        # Botones de acción
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("➕ Nueva Lista", callback_data="wizard_list")
            ])
        
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# VER DETALLE DE LISTA
# ============================================

async def show_list_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, list_id: int):
    """Muestra el detalle de una lista específica"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    
    # Obtener información de la lista
    lists = email_service.get_all_lists()
    list_info = next((l for l in lists if l['id'] == list_id), None)
    
    if not list_info:
        await query.answer("❌ Lista no encontrada", show_alert=True)
        return
    
    recipients = email_service.get_list_recipients(list_id)
    
    message = (
        f"📋 <b>{list_info['name']}</b>\n\n"
        f"📝 {list_info['description']}\n\n"
        f"👥 <b>Contactos:</b> {list_info['recipient_count']}\n"
        f"📅 <b>Creada:</b> {list_info['created_date'][:10]}\n\n"
    )
    
    if recipients:
        message += "<b>Últimos contactos:</b>\n"
        for recipient in recipients[:3]:
            message += f"• {recipient['name']} ({recipient['email']})\n"
        
        if len(recipients) > 3:
            message += f"\n... y {len(recipients) - 3} más\n"
    
    user_id = update.effective_user.id
    is_admin = user_id == Config.ADMIN_USER_ID
    
    keyboard = []
    
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("➕ Agregar Contactos", callback_data=f"add_contacts_{list_id}")
        ])
        keyboard.append([
            InlineKeyboardButton("👁️ Ver Todos", callback_data=f"view_all_recipients_{list_id}"),
            InlineKeyboardButton("🗑️ Eliminar Lista", callback_data=f"delete_list_{list_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("👁️ Ver Contactos", callback_data=f"view_all_recipients_{list_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("⬅️ Volver a Listas", callback_data="view_lists")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# VER PLANTILLAS
# ============================================

async def show_templates_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra todas las plantillas de email"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    templates = email_service.get_all_templates()
    
    user_id = update.effective_user.id
    is_admin = user_id == Config.ADMIN_USER_ID
    
    if not templates:
        message = (
            "📄 <b>Mis Plantillas</b>\n\n"
            "No tienes plantillas creadas aún.\n\n"
            "💡 Las plantillas te permiten reutilizar\n"
            "el mismo diseño de email múltiples veces.\n\n"
        )
        
        keyboard = []
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("➕ Crear Plantilla", callback_data="wizard_template")
            ])
            keyboard.append([
                InlineKeyboardButton("📚 Usar Plantilla Predefinida", callback_data="use_preset_template")
            ])
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
        ])
    else:
        message = f"📄 <b>Mis Plantillas</b>\n\n"
        message += f"Total: {len(templates)} plantilla(s)\n\n"
        
        keyboard = []
        
        # Mostrar hasta 5 plantillas
        for template in templates[:5]:
            subject_preview = template['subject'][:30] + "..." if len(template['subject']) > 30 else template['subject']
            keyboard.append([
                InlineKeyboardButton(
                    f"📄 {template['name']} - {subject_preview}",
                    callback_data=f"template_detail_{template['id']}"
                )
            ])
        
        if len(templates) > 5:
            keyboard.append([
                InlineKeyboardButton("📄 Ver todas...", callback_data="list_all_templates")
            ])
        
        # Botones de acción
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("➕ Nueva Plantilla", callback_data="wizard_template")
            ])
        
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# VER CAMPAÑAS
# ============================================

async def show_campaigns_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra todas las campañas"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    campaigns = email_service.get_all_campaigns()
    
    user_id = update.effective_user.id
    is_admin = user_id == Config.ADMIN_USER_ID
    
    if not campaigns:
        message = (
            "📨 <b>Mis Campañas</b>\n\n"
            "No has enviado campañas aún.\n\n"
        )
        
        keyboard = []
        if is_admin:
            # Verificar si está listo para enviar
            smtp_config = email_service.get_smtp_config()
            lists = email_service.get_all_lists()
            templates = email_service.get_all_templates()
            
            if smtp_config and lists and templates:
                keyboard.append([
                    InlineKeyboardButton("🚀 Enviar Mi Primera Campaña", callback_data="wizard_campaign")
                ])
            else:
                message += "⚠️ Primero debes:\n"
                if not smtp_config:
                    message += "• Configurar email\n"
                if not lists:
                    message += "• Crear una lista\n"
                if not templates:
                    message += "• Crear una plantilla\n"
        
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
        ])
    else:
        # Estadísticas resumidas
        completed = sum(1 for c in campaigns if c['status'] == 'COMPLETED')
        pending = sum(1 for c in campaigns if c['status'] == 'PENDING')
        failed = sum(1 for c in campaigns if c['status'] == 'FAILED')
        
        message = (
            f"📨 <b>Mis Campañas</b>\n\n"
            f"Total: {len(campaigns)}\n"
            f"✅ Completadas: {completed}\n"
            f"⏳ Pendientes: {pending}\n"
            f"❌ Fallidas: {failed}\n\n"
            f"<b>Últimas campañas:</b>\n\n"
        )
        
        keyboard = []
        
        # Mostrar hasta 5 campañas recientes
        for campaign in campaigns[:5]:
            status_emoji = {
                'PENDING': '⏳',
                'RUNNING': '🔄',
                'COMPLETED': '✅',
                'FAILED': '❌'
            }.get(campaign['status'], '❓')
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} {campaign['name']} ({campaign['sent_count']}/{campaign['total_recipients']})",
                    callback_data=f"campaign_detail_{campaign['id']}"
                )
            ])
        
        if len(campaigns) > 5:
            keyboard.append([
                InlineKeyboardButton("📄 Ver todas...", callback_data="list_all_campaigns")
            ])
        
        # Botón para nueva campaña
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("🚀 Nueva Campaña", callback_data="wizard_campaign")
            ])
        
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# VER CONFIGURACIÓN SMTP
# ============================================

async def show_smtp_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la configuración SMTP actual"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    config = email_service.get_smtp_config()
    
    if not config:
        message = (
            "⚙️ <b>Configuración de Email</b>\n\n"
            "⚠️ No has configurado tu email aún.\n\n"
            "💡 Necesitas configurar un servidor SMTP\n"
            "para poder enviar campañas de email.\n\n"
            "<b>Proveedores compatibles:</b>\n"
            "• Gmail\n"
            "• Outlook/Hotmail\n"
            "• Yahoo\n"
            "• Cualquier servidor SMTP\n"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🚀 Configurar Ahora", callback_data="wizard_smtp")
            ],
            [
                InlineKeyboardButton("ℹ️ ¿Qué es SMTP?", callback_data="help_smtp")
            ],
            [
                InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
            ]
        ]
    else:
        password_masked = '•' * 12
        
        message = (
            "⚙️ <b>Configuración de Email</b>\n\n"
            f"✅ <b>Estado:</b> Configurado\n\n"
            f"🌐 <b>Servidor:</b> {config['smtp_server']}\n"
            f"🔌 <b>Puerto:</b> {config['smtp_port']}\n"
            f"👤 <b>Usuario:</b> {config['smtp_username']}\n"
            f"🔒 <b>Contraseña:</b> {password_masked}\n"
            f"📧 <b>Email:</b> {config['sender_email']}\n"
            f"✍️ <b>Nombre:</b> {config['sender_name']}\n"
            f"🔐 <b>TLS:</b> {'Activado' if config['use_tls'] else 'Desactivado'}\n"
            f"⏱️ <b>Delay:</b> {config['delay_between_emails']}s\n"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Reconfigurar", callback_data="wizard_smtp"),
                InlineKeyboardButton("🧪 Probar Conexión", callback_data="test_smtp")
            ],
            [
                InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")
            ]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# AYUDA CONTEXTUAL
# ============================================

async def show_help_smtp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra ayuda sobre SMTP"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "ℹ️ <b>¿Qué es SMTP?</b>\n\n"
        "SMTP (Simple Mail Transfer Protocol) es el\n"
        "protocolo que se usa para enviar emails.\n\n"
        "<b>En palabras simples:</b>\n"
        "Es la configuración que permite a este bot\n"
        "enviar emails desde tu cuenta de correo.\n\n"
        "<b>¿Qué necesitas?</b>\n"
        "• Tu email (ej: tunombre@gmail.com)\n"
        "• Una contraseña especial de aplicación\n\n"
        "<b>Para Gmail:</b>\n"
        "1. Ve a tu cuenta de Google\n"
        "2. Seguridad → Verificación en 2 pasos\n"
        "3. Contraseñas de aplicaciones\n"
        "4. Genera una nueva contraseña\n\n"
        "💡 ¡Es más fácil de lo que parece!\n"
        "Te guiaremos paso a paso.\n"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 Empezar Configuración", callback_data="wizard_smtp")
        ],
        [
            InlineKeyboardButton("📺 Ver Video Tutorial", url="https://youtu.be/ejemplo")
        ],
        [
            InlineKeyboardButton("⬅️ Volver", callback_data="view_smtp")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
