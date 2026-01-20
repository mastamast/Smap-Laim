"""
Wizard para Agregar Contactos a Listas
Permite agregar contactos de forma individual o masiva
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from email_sender import EmailSender
from config import Config
import re

# Estados del wizard de contactos
CONTACT_SELECT_METHOD, CONTACT_ENTER_EMAIL, CONTACT_ENTER_NAME, CONTACT_CONFIRM, CONTACT_BULK_PASTE = range(100, 105)


# ============================================
# WIZARD: AGREGAR CONTACTOS
# ============================================

async def contact_wizard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de agregar contactos"""
    query = update.callback_query
    await query.answer()
    
    # Extraer list_id del callback_data
    list_id = int(query.data.replace('add_contacts_', ''))
    context.user_data['contact_list_id'] = list_id
    
    # Obtener info de la lista
    email_service = EmailSender()
    lists = email_service.get_all_lists()
    list_info = next((l for l in lists if l['id'] == list_id), None)
    
    if not list_info:
        await query.answer("❌ Lista no encontrada", show_alert=True)
        return ConversationHandler.END
    
    message = (
        f"➕ <b>Agregar Contactos</b>\n\n"
        f"📋 Lista: {list_info['name']}\n"
        f"👥 Contactos actuales: {list_info['recipient_count']}\n\n"
        f"¿Cómo deseas agregar contactos?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("👤 Agregar Uno por Uno", callback_data="contact_method_single")
        ],
        [
            InlineKeyboardButton("📋 Agregar Múltiples (Pegar Lista)", callback_data="contact_method_bulk")
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data=f"list_detail_{list_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return CONTACT_SELECT_METHOD


async def contact_select_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la selección del método de agregar contactos"""
    query = update.callback_query
    await query.answer()
    
    method = query.data.replace('contact_method_', '')
    context.user_data['contact_method'] = method
    list_id = context.user_data['contact_list_id']
    
    if method == 'single':
        message = (
            "📧 <b>Agregar Contacto Individual</b>\n\n"
            "Envía el <b>email</b> del contacto:\n\n"
            "<i>Ejemplo: cliente@ejemplo.com</i>"
        )
        
        keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data=f"list_detail_{list_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
        return CONTACT_ENTER_EMAIL
        
    elif method == 'bulk':
        message = (
            "📋 <b>Agregar Múltiples Contactos</b>\n\n"
            "Pega tu lista de contactos en este formato:\n\n"
            "<code>email@ejemplo.com, Nombre Apellido\n"
            "otro@ejemplo.com, Otro Nombre\n"
            "mas@ejemplo.com, Más Nombre</code>\n\n"
            "<b>Formato:</b> email, nombre (separados por coma)\n"
            "<b>Un contacto por línea</b>\n\n"
            "💡 Puedes omitir el nombre si solo tienes emails:\n"
            "<code>email1@ejemplo.com\n"
            "email2@ejemplo.com</code>"
        )
        
        keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data=f"list_detail_{list_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
        return CONTACT_BULK_PASTE


async def contact_enter_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el email ingresado para contacto individual"""
    email = update.message.text.strip().lower()
    
    # Validación básica de email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        await update.message.reply_text(
            "❌ Email inválido. Por favor, envía un email válido:\n"
            "Ejemplo: cliente@ejemplo.com"
        )
        return CONTACT_ENTER_EMAIL
    
    context.user_data['contact_email'] = email
    
    message = (
        f"📧 <b>Agregar Contacto</b>\n\n"
        f"✅ Email: {email}\n\n"
        f"👤 Ahora envía el <b>nombre</b> del contacto:\n\n"
        f"<i>Ejemplo: Juan Pérez</i>\n\n"
        f"💡 O envía /skip para omitir el nombre"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')
    return CONTACT_ENTER_NAME


async def contact_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el nombre ingresado para contacto individual"""
    if update.message.text.strip() == '/skip':
        name = None
    else:
        name = update.message.text.strip()
        if len(name) < 2:
            await update.message.reply_text(
                "❌ El nombre debe tener al menos 2 caracteres.\n"
                "O envía /skip para omitir el nombre:"
            )
            return CONTACT_ENTER_NAME
    
    context.user_data['contact_name'] = name
    
    email = context.user_data['contact_email']
    display_name = name if name else "Sin nombre"
    
    message = (
        f"📋 <b>Confirmar Contacto</b>\n\n"
        f"📧 Email: {email}\n"
        f"👤 Nombre: {display_name}\n\n"
        f"¿Deseas agregar este contacto?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, Agregar", callback_data="contact_save"),
            InlineKeyboardButton("🔄 Reiniciar", callback_data=f"add_contacts_{context.user_data['contact_list_id']}")
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data=f"list_detail_{context.user_data['contact_list_id']}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return CONTACT_CONFIRM


async def contact_bulk_paste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la lista masiva de contactos"""
    text = update.message.text.strip()
    
    if not text:
        await update.message.reply_text(
            "❌ No se recibió ningún texto. Por favor, pega tu lista de contactos."
        )
        return CONTACT_BULK_PASTE
    
    # Procesar líneas
    lines = text.split('\n')
    contacts = []
    errors = []
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Intentar parsear: email, nombre
        if ',' in line:
            parts = line.split(',', 1)
            email = parts[0].strip().lower()
            name = parts[1].strip() if len(parts) > 1 else None
        else:
            email = line.strip().lower()
            name = None
        
        # Validar email
        if re.match(email_regex, email):
            contacts.append({'email': email, 'name': name})
        else:
            errors.append(f"Línea {i}: '{line}' - Email inválido")
    
    if not contacts:
        message = (
            "❌ <b>No se encontraron emails válidos</b>\n\n"
        )
        if errors:
            message += "<b>Errores encontrados:</b>\n"
            for error in errors[:5]:
                message += f"• {error}\n"
            if len(errors) > 5:
                message += f"\n... y {len(errors) - 5} más\n"
        
        message += "\n💡 Verifica el formato y vuelve a intentar."
        
        await update.message.reply_text(message, parse_mode='HTML')
        return CONTACT_BULK_PASTE
    
    context.user_data['bulk_contacts'] = contacts
    context.user_data['bulk_errors'] = errors
    
    # Mostrar resumen
    message = (
        f"📊 <b>Resumen de Importación</b>\n\n"
        f"✅ Contactos válidos: {len(contacts)}\n"
    )
    
    if errors:
        message += f"⚠️ Líneas con errores: {len(errors)}\n\n"
    else:
        message += "\n"
    
    message += "<b>Primeros contactos:</b>\n"
    for contact in contacts[:5]:
        name_display = contact['name'] if contact['name'] else 'Sin nombre'
        message += f"• {contact['email']} - {name_display}\n"
    
    if len(contacts) > 5:
        message += f"\n... y {len(contacts) - 5} más\n"
    
    message += "\n¿Deseas agregar estos contactos?"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, Agregar Todos", callback_data="contact_bulk_save")
        ],
        [
            InlineKeyboardButton("🔄 Reiniciar", callback_data=f"add_contacts_{context.user_data['contact_list_id']}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"list_detail_{context.user_data['contact_list_id']}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    return CONTACT_CONFIRM


async def contact_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el contacto individual en la base de datos"""
    query = update.callback_query
    await query.answer()
    
    email_service = EmailSender()
    list_id = context.user_data['contact_list_id']
    email = context.user_data['contact_email']
    name = context.user_data.get('contact_name')
    
    success = email_service.add_recipient(list_id, email, name)
    
    if success:
        message = (
            f"✅ <b>¡Contacto Agregado!</b>\n\n"
            f"📧 Email: {email}\n"
            f"👤 Nombre: {name if name else 'Sin nombre'}\n\n"
            f"¿Deseas agregar otro contacto?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Sí, Agregar Otro", callback_data=f"add_contacts_{list_id}")
            ],
            [
                InlineKeyboardButton("📋 Ver Lista", callback_data=f"list_detail_{list_id}"),
                InlineKeyboardButton("🏠 Menú", callback_data="menu_email")
            ]
        ]
    else:
        message = (
            f"⚠️ <b>Contacto Ya Existe</b>\n\n"
            f"El email {email} ya está en esta lista.\n\n"
            f"¿Qué deseas hacer?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Agregar Otro", callback_data=f"add_contacts_{list_id}")
            ],
            [
                InlineKeyboardButton("📋 Ver Lista", callback_data=f"list_detail_{list_id}")
            ]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    # Limpiar datos temporales
    context.user_data.clear()
    
    return ConversationHandler.END


async def contact_bulk_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda múltiples contactos en la base de datos"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⏳ <b>Agregando contactos...</b>\n\nPor favor espera...",
        parse_mode='HTML'
    )
    
    email_service = EmailSender()
    list_id = context.user_data['contact_list_id']
    contacts = context.user_data['bulk_contacts']
    
    added = 0
    duplicates = 0
    
    for contact in contacts:
        success = email_service.add_recipient(
            list_id,
            contact['email'],
            contact['name']
        )
        
        if success:
            added += 1
        else:
            duplicates += 1
    
    message = (
        f"✅ <b>¡Contactos Agregados!</b>\n\n"
        f"📊 <b>Resultados:</b>\n"
        f"✅ Agregados: {added}\n"
        f"⚠️ Duplicados omitidos: {duplicates}\n"
        f"📝 Total procesados: {len(contacts)}\n\n"
    )
    
    if duplicates > 0:
        message += "💡 Los contactos duplicados ya existían en la lista.\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Agregar Más", callback_data=f"add_contacts_{list_id}")
        ],
        [
            InlineKeyboardButton("📋 Ver Lista", callback_data=f"list_detail_{list_id}"),
            InlineKeyboardButton("🏠 Menú", callback_data="menu_email")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    # Limpiar datos temporales
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel_contact_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el wizard de contactos"""
    query = update.callback_query
    if query:
        await query.answer()
    
    list_id = context.user_data.get('contact_list_id', 0)
    context.user_data.clear()
    
    message = "❌ Operación cancelada."
    
    keyboard = [[InlineKeyboardButton("📋 Volver a Lista", callback_data=f"list_detail_{list_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    return ConversationHandler.END
