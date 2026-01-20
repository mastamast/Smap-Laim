"""
Wizards Adicionales y Mejorados
Implementa wizards completos para plantillas, campañas y contactos
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from email_sender import EmailSender
from config import Config
import re

# Estados adicionales del wizard
TEMPLATE_ENTER_NAME, TEMPLATE_ENTER_SUBJECT, TEMPLATE_ENTER_BODY, TEMPLATE_CONFIRM = range(20, 24)
CAMPAIGN_SELECT_LIST, CAMPAIGN_SELECT_TEMPLATE, CAMPAIGN_ENTER_NAME, CAMPAIGN_CONFIRM = range(24, 28)
ADD_CONTACT_METHOD, ADD_CONTACT_SINGLE, ADD_CONTACT_BULK, ADD_CONTACT_CONFIRM = range(28, 32)


# ============================================
# WIZARD: CREAR PLANTILLA
# ============================================

async def template_wizard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de creación de plantilla"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "📄 <b>Crear Nueva Plantilla (Paso 1 de 4)</b>\n\n"
        "Una plantilla es un diseño de email que puedes\n"
        "reutilizar múltiples veces.\n\n"
        "💡 <b>Consejo:</b> Puedes usar la variable <code>{{name}}</code>\n"
        "en tu contenido para personalizar cada email.\n\n"
        "📝 Envía un nombre para tu plantilla:\n"
        "<i>Ejemplos: Bienvenida, Promocion_Verano, Newsletter_Semanal</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("📚 Ver Ejemplos", callback_data="template_examples")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return TEMPLATE_ENTER_NAME


async def template_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el nombre de la plantilla"""
    template_name = update.message.text.strip()
    
    if len(template_name) < 3:
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 3 caracteres.\n"
            "Por favor, envía un nombre más descriptivo:"
        )
        return TEMPLATE_ENTER_NAME
    
    # Verificar si ya existe
    email_service = EmailSender()
    templates = email_service.get_all_templates()
    if any(t['name'].lower() == template_name.lower() for t in templates):
        await update.message.reply_text(
            f"⚠️ Ya existe una plantilla llamada '{template_name}'.\n"
            "Por favor, elige otro nombre:"
        )
        return TEMPLATE_ENTER_NAME
    
    context.user_data['template_name'] = template_name
    
    message = (
        f"📄 <b>Crear Plantilla (Paso 2 de 4)</b>\n\n"
        f"✅ Nombre: {template_name}\n\n"
        f"📧 Ahora envía el <b>asunto</b> del email:\n\n"
        f"💡 El asunto es lo primero que verá el destinatario.\n"
        f"Puedes usar la variable <code>{{name}}</code> para personalizar.\n\n"
        f"<b>Ejemplo:</b> <code>¡Hola {{name}}, tenemos una oferta especial!</code>"
    )
    
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return TEMPLATE_ENTER_SUBJECT


async def template_enter_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el asunto de la plantilla"""
    subject = update.message.text.strip()
    
    if len(subject) < 5:
        await update.message.reply_text(
            "❌ El asunto debe tener al menos 5 caracteres.\n"
            "Un buen asunto es clave para que abran el email:"
        )
        return TEMPLATE_ENTER_SUBJECT
    
    context.user_data['template_subject'] = subject
    
    message = (
        f"📄 <b>Crear Plantilla (Paso 3 de 4)</b>\n\n"
        f"✅ Nombre: {context.user_data['template_name']}\n"
        f"✅ Asunto: {subject}\n\n"
        f"📝 Ahora envía el <b>cuerpo</b> del email:\n\n"
        f"💡 <b>Importante:</b>\n"
        f"• Escribe SOLO el contenido que quieres enviar\n"
        f"• Puedes usar etiquetas HTML\n"
        f"• Usa la variable <code>{{name}}</code> donde quieras que aparezca el nombre\n\n"
        f"<b>Ejemplo de contenido:</b>\n"
        f"<code>Hola {{name}}, esta es una oferta especial solo para ti. Aprovecha ahora!</code>"
    )
    
    keyboard = [
        [InlineKeyboardButton("📚 Ver Ejemplos HTML", callback_data="template_html_examples")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return TEMPLATE_ENTER_BODY


async def template_enter_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el cuerpo de la plantilla"""
    body = update.message.text.strip()
    
    if len(body) < 10:
        await update.message.reply_text(
            "❌ El cuerpo del email es muy corto.\n"
            "Por favor, escribe un mensaje más completo:"
        )
        return TEMPLATE_ENTER_BODY
    
    context.user_data['template_body'] = body
    
    # Vista previa del cuerpo (primeros 200 caracteres)
    preview = body[:200] + "..." if len(body) > 200 else body
    preview = preview.replace('<', '&lt;').replace('>', '&gt;')
    
    message = (
        f"📄 <b>Crear Plantilla (Paso 4 de 4)</b>\n\n"
        f"📋 <b>Resumen:</b>\n\n"
        f"<b>Nombre:</b> {context.user_data['template_name']}\n"
        f"<b>Asunto:</b> {context.user_data['template_subject']}\n\n"
        f"<b>Cuerpo (vista previa):</b>\n"
        f"<code>{preview}</code>\n\n"
        f"¿Deseas crear esta plantilla?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Crear Plantilla", callback_data="template_create"),
            InlineKeyboardButton("🔄 Reiniciar", callback_data="wizard_template")
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return TEMPLATE_CONFIRM


async def template_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea la plantilla en la base de datos"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    user_id = update.effective_user.id
    
    template_id = email_service.create_template(
        name=context.user_data['template_name'],
        subject=context.user_data['template_subject'],
        body=context.user_data['template_body'],
        created_by=user_id
    )
    
    if template_id:
        message = (
            f"✅ <b>¡Plantilla Creada Exitosamente!</b>\n\n"
            f"📄 Nombre: {context.user_data['template_name']}\n"
            f"📧 Asunto: {context.user_data['template_subject']}\n"
            f"🆔 ID: {template_id}\n\n"
            f"🎯 <b>Siguiente paso:</b>\n"
            f"Puedes usar esta plantilla al enviar campañas"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Enviar Campaña", callback_data="wizard_campaign")],
            [InlineKeyboardButton("📄 Ver Mis Plantillas", callback_data="view_templates")],
            [InlineKeyboardButton("🏠 Ir al Menú", callback_data="menu_email")]
        ]
    else:
        message = (
            f"❌ <b>Error al Crear Plantilla</b>\n\n"
            f"Hubo un problema al guardar la plantilla.\n"
            f"Por favor, intenta nuevamente."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Intentar de Nuevo", callback_data="wizard_template")],
            [InlineKeyboardButton("🏠 Volver", callback_data="menu_email")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    # Limpiar datos temporales
    context.user_data.clear()
    
    return ConversationHandler.END


# ============================================
# WIZARD: ENVIAR CAMPAÑA
# ============================================

async def campaign_wizard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de envío de campaña"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    
    # Verificar prerequisitos
    smtp_config = email_service.get_smtp_config()
    lists = email_service.get_all_lists()
    templates = email_service.get_all_templates()
    
    if not smtp_config:
        message = (
            "⚠️ <b>Email No Configurado</b>\n\n"
            "Antes de enviar campañas necesitas\n"
            "configurar tu email SMTP."
        )
        keyboard = [
            [InlineKeyboardButton("⚙️ Configurar Email", callback_data="wizard_smtp")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
        return ConversationHandler.END
    
    if not lists:
        message = (
            "⚠️ <b>Sin Listas de Correos</b>\n\n"
            "Necesitas al menos una lista con contactos\n"
            "para enviar una campaña."
        )
        keyboard = [
            [InlineKeyboardButton("📋 Crear Lista", callback_data="wizard_list")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
        return ConversationHandler.END
    
    if not templates:
        message = (
            "⚠️ <b>Sin Plantillas</b>\n\n"
            "Necesitas al menos una plantilla\n"
            "para enviar una campaña."
        )
        keyboard = [
            [InlineKeyboardButton("📄 Crear Plantilla", callback_data="wizard_template")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu_email")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
        return ConversationHandler.END
    
    # Todo OK, comenzar wizard
    message = (
        "🚀 <b>Enviar Nueva Campaña (Paso 1 de 4)</b>\n\n"
        f"Tienes {len(lists)} lista(s) disponible(s).\n\n"
        "📋 Selecciona la lista de destinatarios:"
    )
    
    keyboard = []
    for lst in lists[:10]:  # Máximo 10 listas
        keyboard.append([
            InlineKeyboardButton(
                f"📋 {lst['name']} ({lst['recipient_count']} contactos)",
                callback_data=f"campaign_list_{lst['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return CAMPAIGN_SELECT_LIST


async def campaign_select_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la selección de lista"""
    query = update.callback_query
    await query.answer()
    
    list_id = int(query.data.replace('campaign_list_', ''))
    context.user_data['campaign_list_id'] = list_id
    
    # Obtener info de la lista
    email_service = EmailSender()
    lists = email_service.get_all_lists()
    list_info = next((l for l in lists if l['id'] == list_id), None)
    
    if not list_info or list_info['recipient_count'] == 0:
        await query.answer("⚠️ Esta lista no tiene contactos", show_alert=True)
        return CAMPAIGN_SELECT_LIST
    
    templates = email_service.get_all_templates()
    
    message = (
        f"🚀 <b>Enviar Nueva Campaña (Paso 2 de 4)</b>\n\n"
        f"✅ Lista: {list_info['name']}\n"
        f"👥 Destinatarios: {list_info['recipient_count']}\n\n"
        f"📄 Ahora selecciona la plantilla a usar:"
    )
    
    keyboard = []
    for template in templates[:10]:  # Máximo 10 plantillas
        subject_preview = template['subject'][:40] + "..." if len(template['subject']) > 40 else template['subject']
        keyboard.append([
            InlineKeyboardButton(
                f"📄 {template['name']} - {subject_preview}",
                callback_data=f"campaign_template_{template['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("⬅️ Atrás", callback_data="wizard_campaign")])
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return CAMPAIGN_SELECT_TEMPLATE


async def campaign_select_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la selección de plantilla y pide nombre de campaña"""
    query = update.callback_query
    await query.answer()
    
    template_id = int(query.data.replace('campaign_template_', ''))
    context.user_data['campaign_template_id'] = template_id
    
    # Obtener info
    email_service = EmailSender()
    template = email_service.get_template(template_id)
    lists = email_service.get_all_lists()
    list_info = next((l for l in lists if l['id'] == context.user_data['campaign_list_id']), None)
    
    message = (
        f"🚀 <b>Enviar Nueva Campaña (Paso 3 de 4)</b>\n\n"
        f"✅ Lista: {list_info['name']} ({list_info['recipient_count']} contactos)\n"
        f"✅ Plantilla: {template['name']}\n"
        f"✅ Asunto: {template['subject']}\n\n"
        f"📝 Envía un nombre para esta campaña:\n\n"
        f"<i>Ejemplos: Campaña Navidad 2024,\n"
        f"Promoción Verano, Newsletter Enero, etc.</i>"
    )
    
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return CAMPAIGN_ENTER_NAME


async def campaign_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el nombre de la campaña y muestra confirmación"""
    campaign_name = update.message.text.strip()
    
    if len(campaign_name) < 3:
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 3 caracteres.\n"
            "Por favor, envía un nombre más descriptivo:"
        )
        return CAMPAIGN_ENTER_NAME
    
    context.user_data['campaign_name'] = campaign_name
    
    # Obtener toda la info para resumen
    email_service = EmailSender()
    lists = email_service.get_all_lists()
    list_info = next((l for l in lists if l['id'] == context.user_data['campaign_list_id']), None)
    template = email_service.get_template(context.user_data['campaign_template_id'])
    
    message = (
        f"🚀 <b>Enviar Nueva Campaña (Paso 4 de 4)</b>\n\n"
        f"📋 <b>Resumen Final:</b>\n\n"
        f"<b>Campaña:</b> {campaign_name}\n"
        f"<b>Lista:</b> {list_info['name']}\n"
        f"<b>Destinatarios:</b> {list_info['recipient_count']}\n"
        f"<b>Plantilla:</b> {template['name']}\n"
        f"<b>Asunto:</b> {template['subject']}\n\n"
        f"⏱️ <b>Tiempo estimado:</b> ~{list_info['recipient_count']} segundos\n\n"
        f"⚠️ <b>Importante:</b> Una vez iniciado el envío,\n"
        f"no se puede detener.\n\n"
        f"¿Confirmas que deseas enviar esta campaña?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, Enviar Ahora", callback_data="campaign_send"),
        ],
        [
            InlineKeyboardButton("🔄 Reiniciar", callback_data="wizard_campaign"),
            InlineKeyboardButton("❌ Cancelar", callback_data="menu_email")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return CAMPAIGN_CONFIRM


async def campaign_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ejecuta el envío de la campaña"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    user_id = update.effective_user.id
    
    # Crear campaña
    campaign_id = email_service.create_campaign(
        name=context.user_data['campaign_name'],
        template_id=context.user_data['campaign_template_id'],
        list_id=context.user_data['campaign_list_id'],
        created_by=user_id
    )
    
    if not campaign_id:
        message = "❌ Error al crear la campaña."
        keyboard = [
            [InlineKeyboardButton("🔄 Reintentar", callback_data="wizard_campaign")],
            [InlineKeyboardButton("🏠 Volver", callback_data="menu_email")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        context.user_data.clear()
        return ConversationHandler.END
    
    # Mostrar mensaje de inicio
    await query.edit_message_text(
        f"🚀 <b>Iniciando campaña...</b>\n\n"
        f"Por favor espera. Esto puede tomar varios minutos.\n"
        f"No cierres el bot.",
        parse_mode='HTML'
    )
    
    # Enviar campaña
    result = email_service.send_campaign(campaign_id)
    
    if result['success']:
        success_rate = (result['sent'] / result['total'] * 100) if result['total'] > 0 else 0
        
        message = (
            f"✅ <b>¡Campaña Enviada!</b>\n\n"
            f"📊 <b>Resultados:</b>\n"
            f"✉️ Enviados: {result['sent']}/{result['total']}\n"
            f"❌ Fallidos: {result['failed']}\n"
            f"📈 Tasa de éxito: {success_rate:.1f}%\n\n"
            f"🆔 ID de campaña: <code>{campaign_id}</code>\n\n"
            f"Puedes ver estadísticas detalladas en cualquier momento."
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 Ver Estadísticas", callback_data=f"campaign_detail_{campaign_id}")],
            [InlineKeyboardButton("📨 Mis Campañas", callback_data="view_campaigns")],
            [InlineKeyboardButton("🏠 Ir al Menú", callback_data="menu_email")]
        ]
    else:
        message = (
            f"❌ <b>Error al Enviar Campaña</b>\n\n"
            f"Error: {result.get('error', 'Desconocido')}\n\n"
            f"Por favor, verifica tu configuración SMTP\n"
            f"y vuelve a intentarlo."
        )
        
        keyboard = [
            [InlineKeyboardButton("⚙️ Ver Config SMTP", callback_data="view_smtp")],
            [InlineKeyboardButton("🔄 Reintentar", callback_data="wizard_campaign")],
            [InlineKeyboardButton("🏠 Volver", callback_data="menu_email")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    # Limpiar datos temporales
    context.user_data.clear()
    
    return ConversationHandler.END


# ============================================
# FUNCIÓN DE CANCELACIÓN
# ============================================

async def cancel_enhanced_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela cualquier wizard mejorado en progreso"""
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
