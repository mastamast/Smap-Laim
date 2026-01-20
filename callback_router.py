"""
Router de Callbacks para Botones Inline
Dirige los callbacks a sus respectivos handlers
"""

from telegram import Update
from telegram.ext import ContextTypes
from menu_handlers import (
    show_main_menu,
    show_email_menu,
    show_users_menu,
    show_lists_view,
    show_list_detail,
    show_templates_view,
    show_campaigns_view,
    show_smtp_config,
    show_help_smtp
)
from enhanced_callback_handlers import (
    test_smtp_connection,
    show_template_detail,
    show_campaign_detail,
    show_help_topic,
    show_all_members_with_buttons,
    show_member_info_button,
    show_activity_logs
)


async def route_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Router principal que dirige todos los callbacks
    """
    query = update.callback_query
    callback_data = query.data
    
    # Menús principales
    if callback_data == "main_menu":
        await show_main_menu(update, context)
    
    elif callback_data == "menu_email":
        await show_email_menu(update, context)
    
    elif callback_data == "menu_users":
        await show_users_menu(update, context)
    
    # Visualización de listas
    elif callback_data == "view_lists":
        await show_lists_view(update, context)
    
    elif callback_data.startswith("list_detail_"):
        list_id = int(callback_data.replace("list_detail_", ""))
        await show_list_detail(update, context, list_id)
    
    # Visualización de plantillas
    elif callback_data == "view_templates":
        await show_templates_view(update, context)
    
    # Visualización de campañas
    elif callback_data == "view_campaigns":
        await show_campaigns_view(update, context)
    
    # Configuración SMTP
    elif callback_data == "view_smtp":
        await show_smtp_config(update, context)
    
    elif callback_data == "help_smtp":
        await show_help_smtp(update, context)
    
    # Test SMTP
    elif callback_data == "test_smtp":
        await test_smtp_connection(update, context)
    
    # Template details
    elif callback_data.startswith("template_detail_"):
        template_id = int(callback_data.replace("template_detail_", ""))
        await show_template_detail(update, context, template_id)
    
    # Campaign details
    elif callback_data.startswith("campaign_detail_"):
        campaign_id = int(callback_data.replace("campaign_detail_", ""))
        await show_campaign_detail(update, context, campaign_id)
    
    # Member management
    elif callback_data == "list_all_members":
        await show_all_members_with_buttons(update, context)
    
    elif callback_data.startswith("member_info_"):
        user_id = int(callback_data.replace("member_info_", ""))
        await show_member_info_button(update, context, user_id)
    
    elif callback_data == "view_logs":
        await show_activity_logs(update, context)
    
    # Estadísticas
    elif callback_data == "stats_menu" or callback_data == "stats":
        await show_stats_menu(update, context)
    
    # Ayuda
    elif callback_data == "help_menu" or callback_data == "help":
        await show_help_menu(update, context)
    
    elif callback_data in ["help_email_tranzas", "help_lists", "help_templates", "help_campaigns", "help_faq"]:
        await show_help_topic(update, context, callback_data)
    
    # Otros callbacks se manejan en sus respectivos conversation handlers
    else:
        await query.answer("Función en desarrollo", show_alert=True)


async def show_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra menú de estadísticas (placeholder)"""
    query = update.callback_query
    await query.answer()
    
    from database import MembershipDatabase
    from email_sender import EmailSender
    
    db = MembershipDatabase()
    email_service = EmailSender()
    
    member_count = db.get_member_count()
    lists = email_service.get_all_lists()
    templates = email_service.get_all_templates()
    campaigns = email_service.get_all_campaigns()
    
    total_recipients = sum(lst['recipient_count'] for lst in lists)
    completed_campaigns = sum(1 for c in campaigns if c['status'] == 'COMPLETED')
    total_sent = sum(c['sent_count'] for c in campaigns if c['status'] == 'COMPLETED')
    
    message = (
        "📊 <b>Estadísticas del Sistema</b>\n\n"
        "<b>Usuarios:</b>\n"
        f"👥 Miembros activos: {member_count}\n\n"
        "<b>Email Tranzas:</b>\n"
        f"📋 Listas: {len(lists)}\n"
        f"👥 Total contactos: {total_recipients}\n"
        f"📄 Plantillas: {len(templates)}\n"
        f"📨 Campañas enviadas: {completed_campaigns}\n"
        f"✉️ Emails totales enviados: {total_sent}\n"
    )
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("📈 Ver Detalles", callback_data="stats_detailed")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)


async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra menú de ayuda"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "❓ <b>Centro de Ayuda</b>\n\n"
        "Selecciona un tema para obtener ayuda:\n"
    )
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("📧 Email Tranzas", callback_data="help_email_tranzas")],
        [InlineKeyboardButton("⚙️ Configuración SMTP", callback_data="help_smtp")],
        [InlineKeyboardButton("📋 Gestión de Listas", callback_data="help_lists")],
        [InlineKeyboardButton("📄 Crear Plantillas", callback_data="help_templates")],
        [InlineKeyboardButton("🚀 Enviar Campañas", callback_data="help_campaigns")],
        [InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="help_faq")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
