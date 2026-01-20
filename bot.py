"""
Bot de Telegram con Sistema de Membresías
Punto de entrada principal de la aplicación
"""

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from config import Config
from handlers import (
    start_command,
    help_command,
    status_command,
    add_member_command,
    remove_member_command,
    list_members_command,
    member_info_command,
    stats_command,
    logs_command,
    execute_command,
    set_smtp_command,
    smtp_status_command,
    create_list_command,
    add_recipient_command,
    lists_lists_command,
    view_recipients_command,
    create_template_command,
    list_templates_command,
    send_campaign_command,
    campaigns_command,
    campaign_stats_command,
    unknown_command,
    error_handler
)
from callback_router import route_callback
from wizard_handlers import (
    smtp_wizard_start,
    smtp_select_provider,
    smtp_enter_email,
    smtp_enter_password,
    smtp_enter_name,
    smtp_save,
    list_wizard_start,
    list_enter_name,
    list_enter_desc,
    list_create,
    cancel_wizard,
    SMTP_SELECT_PROVIDER,
    SMTP_ENTER_EMAIL,
    SMTP_ENTER_PASSWORD,
    SMTP_ENTER_NAME,
    SMTP_CONFIRM,
    LIST_ENTER_NAME,
    LIST_ENTER_DESC,
    LIST_CONFIRM
)
from enhanced_wizard_handlers import (
    template_wizard_start,
    template_enter_name,
    template_enter_subject,
    template_enter_body,
    template_create,
    campaign_wizard_start,
    campaign_select_list,
    campaign_select_template,
    campaign_enter_name,
    campaign_send,
    cancel_enhanced_wizard,
    TEMPLATE_ENTER_NAME,
    TEMPLATE_ENTER_SUBJECT,
    TEMPLATE_ENTER_BODY,
    TEMPLATE_CONFIRM,
    CAMPAIGN_SELECT_LIST,
    CAMPAIGN_SELECT_TEMPLATE,
    CAMPAIGN_ENTER_NAME,
    CAMPAIGN_CONFIRM
)
from contact_wizard_handlers import (
    contact_wizard_start,
    contact_select_method,
    contact_enter_email,
    contact_enter_name,
    contact_save,
    contact_bulk_paste,
    contact_bulk_save,
    cancel_contact_wizard,
    CONTACT_SELECT_METHOD,
    CONTACT_ENTER_EMAIL,
    CONTACT_ENTER_NAME,
    CONTACT_CONFIRM,
    CONTACT_BULK_PASTE
)


def main():
    """
    Función principal que inicializa y ejecuta el bot
    """
    try:
        # Validar configuración
        Config.validate()
        print("✅ Configuración validada correctamente")
        
        # Crear la aplicación del bot
        print("🤖 Inicializando bot...")
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # ============================================
        # CONVERSATION HANDLERS (WIZARDS)
        # ============================================
        
        # Wizard SMTP
        smtp_wizard = ConversationHandler(
            entry_points=[CallbackQueryHandler(smtp_wizard_start, pattern="^wizard_smtp$")],
            states={
                SMTP_SELECT_PROVIDER: [
                    CallbackQueryHandler(smtp_select_provider, pattern="^smtp_provider_")
                ],
                SMTP_ENTER_EMAIL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, smtp_enter_email)
                ],
                SMTP_ENTER_PASSWORD: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, smtp_enter_password)
                ],
                SMTP_ENTER_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, smtp_enter_name)
                ],
                SMTP_CONFIRM: [
                    CallbackQueryHandler(smtp_save, pattern="^smtp_save"),
                    CallbackQueryHandler(smtp_wizard_start, pattern="^wizard_smtp$")
                ]
            },
            fallbacks=[CallbackQueryHandler(cancel_wizard, pattern="^menu_email$")]
        )
        
        # Wizard Lista
        list_wizard = ConversationHandler(
            entry_points=[CallbackQueryHandler(list_wizard_start, pattern="^wizard_list$")],
            states={
                LIST_ENTER_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, list_enter_name)
                ],
                LIST_ENTER_DESC: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, list_enter_desc),
                    CallbackQueryHandler(list_enter_desc, pattern="^list_skip_desc$")
                ],
                LIST_CONFIRM: [
                    CallbackQueryHandler(list_create, pattern="^list_create$"),
                    CallbackQueryHandler(list_wizard_start, pattern="^wizard_list$")
                ]
            },
            fallbacks=[CallbackQueryHandler(cancel_wizard, pattern="^menu_email$")]
        )
        
        application.add_handler(smtp_wizard)
        application.add_handler(list_wizard)
        
        # Wizard Plantilla
        template_wizard = ConversationHandler(
            entry_points=[CallbackQueryHandler(template_wizard_start, pattern="^wizard_template$")],
            states={
                TEMPLATE_ENTER_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, template_enter_name)
                ],
                TEMPLATE_ENTER_SUBJECT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, template_enter_subject)
                ],
                TEMPLATE_ENTER_BODY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, template_enter_body)
                ],
                TEMPLATE_CONFIRM: [
                    CallbackQueryHandler(template_create, pattern="^template_create$"),
                    CallbackQueryHandler(template_wizard_start, pattern="^wizard_template$")
                ]
            },
            fallbacks=[CallbackQueryHandler(cancel_enhanced_wizard, pattern="^menu_email$")]
        )
        
        # Wizard Campaña
        campaign_wizard = ConversationHandler(
            entry_points=[CallbackQueryHandler(campaign_wizard_start, pattern="^wizard_campaign$")],
            states={
                CAMPAIGN_SELECT_LIST: [
                    CallbackQueryHandler(campaign_select_list, pattern="^campaign_list_")
                ],
                CAMPAIGN_SELECT_TEMPLATE: [
                    CallbackQueryHandler(campaign_select_template, pattern="^campaign_template_")
                ],
                CAMPAIGN_ENTER_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, campaign_enter_name)
                ],
                CAMPAIGN_CONFIRM: [
                    CallbackQueryHandler(campaign_send, pattern="^campaign_send$"),
                    CallbackQueryHandler(campaign_wizard_start, pattern="^wizard_campaign$")
                ]
            },
            fallbacks=[CallbackQueryHandler(cancel_enhanced_wizard, pattern="^menu_email$")]
        )
        
        application.add_handler(template_wizard)
        application.add_handler(campaign_wizard)
        
        # Wizard Contactos
        contact_wizard = ConversationHandler(
            entry_points=[CallbackQueryHandler(contact_wizard_start, pattern="^add_contacts_")],
            states={
                CONTACT_SELECT_METHOD: [
                    CallbackQueryHandler(contact_select_method, pattern="^contact_method_")
                ],
                CONTACT_ENTER_EMAIL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, contact_enter_email)
                ],
                CONTACT_ENTER_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, contact_enter_name)
                ],
                CONTACT_BULK_PASTE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, contact_bulk_paste)
                ],
                CONTACT_CONFIRM: [
                    CallbackQueryHandler(contact_save, pattern="^contact_save$"),
                    CallbackQueryHandler(contact_bulk_save, pattern="^contact_bulk_save$"),
                    CallbackQueryHandler(contact_wizard_start, pattern="^add_contacts_")
                ]
            },
            fallbacks=[
                CallbackQueryHandler(cancel_contact_wizard, pattern="^list_detail_"),
                CallbackQueryHandler(cancel_contact_wizard, pattern="^menu_email$")
            ]
        )
        
        application.add_handler(contact_wizard)
        
        # ============================================
        # CALLBACK QUERY HANDLER (BOTONES)
        # ============================================
        application.add_handler(CallbackQueryHandler(route_callback))
        
        # ============================================
        # REGISTRAR COMANDOS PÚBLICOS
        # ============================================
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        
        # ============================================
        # REGISTRAR COMANDOS DE ADMINISTRADOR
        # ============================================
        application.add_handler(CommandHandler("addmember", add_member_command))
        application.add_handler(CommandHandler("removemember", remove_member_command))
        application.add_handler(CommandHandler("listmembers", list_members_command))
        application.add_handler(CommandHandler("memberinfo", member_info_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("logs", logs_command))
        
        # ============================================
        # REGISTRAR COMANDOS FUNCIONALES
        # ============================================
        application.add_handler(CommandHandler("execute", execute_command))
        
        # ============================================
        # COMANDOS DE EMAIL TRANZAS
        # ============================================
        # Configuración SMTP
        application.add_handler(CommandHandler("setsmtp", set_smtp_command))
        application.add_handler(CommandHandler("smtpstatus", smtp_status_command))
        
        # Listas de correos
        application.add_handler(CommandHandler("createlist", create_list_command))
        application.add_handler(CommandHandler("addrecipient", add_recipient_command))
        application.add_handler(CommandHandler("listslists", lists_lists_command))
        application.add_handler(CommandHandler("viewrecipients", view_recipients_command))
        
        # Plantillas
        application.add_handler(CommandHandler("createtemplate", create_template_command))
        application.add_handler(CommandHandler("listtemplates", list_templates_command))
        
        # Campañas
        application.add_handler(CommandHandler("sendcampaign", send_campaign_command))
        application.add_handler(CommandHandler("campaigns", campaigns_command))
        application.add_handler(CommandHandler("campaignstats", campaign_stats_command))
        
        # ============================================
        # MANEJADORES DE ERRORES Y MENSAJES NO RECONOCIDOS
        # ============================================
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        application.add_error_handler(error_handler)
        
        # Información de inicio
        print("\n" + "="*50)
        print("🚀 BOT DE TELEGRAM INICIADO")
        print("="*50)
        print(f"🔑 Admin ID: {Config.ADMIN_USER_ID}")
        print(f"💾 Base de datos: {Config.DATABASE_NAME}")
        print("="*50)
        print("\n✅ El bot está ejecutándose. Presiona Ctrl+C para detener.\n")
        
        # Iniciar el bot
        application.run_polling(allowed_updates=True)
        
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        print("\n💡 Asegúrate de que el archivo .env existe y contiene:")
        print("   TELEGRAM_BOT_TOKEN=tu_token_aqui")
        print("   ADMIN_USER_ID=tu_id_aqui")
    except Exception as e:
        import traceback
        print(f"❌ Error al iniciar el bot: {e}")
        print("\n📋 Detalles del error:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
