# 📧 Sistema de Email Tranzas para Telegram Bot

## 🚀 Descripción

Sistema completo de envío de emails masivos integrado en un bot de Telegram. Permite gestionar listas de correos, crear plantillas personalizadas y enviar campañas de tranzas a múltiples destinatarios.

## ✨ Características

- ✅ Sistema de membresías con control de acceso
- 📋 Gestión de listas de correos y destinatarios
- 📄 Plantillas de email personalizables con variables
- 📨 Envío de campañas masivas con rate limiting
- 📊 Estadísticas y seguimiento de campañas
- 🔐 Configuración SMTP flexible (Gmail, Outlook, etc.)
- 🛡️ Sistema de permisos (Admin/Miembros)

## 📦 Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**

Crea un archivo `.env` con:
```env
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
ADMIN_USER_ID=tu_id_de_telegram
```

3. **Ejecutar el bot:**
```bash
python bot.py
```

## 🔧 Configuración Inicial

### 1. Configurar SMTP

Primero, configura tu servidor SMTP. Para **Gmail**:

```
/setsmtp smtp.gmail.com 587 tu@gmail.com tu_contraseña_app tu@gmail.com "Tu Nombre"
```

**⚠️ Importante para Gmail:**
- Ve a tu cuenta de Google → Seguridad
- Activa la verificación en dos pasos
- Genera una "Contraseña de aplicación"
- Usa esa contraseña en el comando

**Otros proveedores SMTP:**
- **Outlook/Hotmail:** smtp.office365.com:587
- **Yahoo:** smtp.mail.yahoo.com:587
- **SendGrid:** smtp.sendgrid.net:587
- **Mailgun:** smtp.mailgun.org:587

### 2. Verificar configuración

```
/smtpstatus
```

## 📋 Comandos Disponibles

### Comandos Generales

| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar el bot y ver menú principal |
| `/help` | Ver ayuda y comandos disponibles |
| `/status` | Ver tu estado de membresía |
| `/execute` | Menú principal de Email Tranzas |

### Administración de Usuarios (Solo Admin)

| Comando | Ejemplo |
|---------|---------|
| `/addmember <user_id>` | `/addmember 123456789` |
| `/removemember <user_id>` | `/removemember 123456789` |
| `/listmembers` | Ver todos los miembros |
| `/memberinfo <user_id>` | `/memberinfo 123456789` |
| `/stats` | Ver estadísticas del bot |
| `/logs` | Ver registro de actividades |

### Configuración SMTP (Solo Admin)

| Comando | Descripción |
|---------|-------------|
| `/setsmtp <server> <port> <usuario> <password> <email> <nombre>` | Configurar SMTP |
| `/smtpstatus` | Ver configuración actual |

### Gestión de Listas (Solo Admin)

| Comando | Ejemplo |
|---------|---------|
| `/createlist <nombre> <descripción>` | `/createlist clientes "Clientes potenciales"` |
| `/addrecipient <list_id> <email> <nombre>` | `/addrecipient 1 juan@email.com "Juan Pérez"` |
| `/listslists` | Ver todas las listas |
| `/viewrecipients <list_id>` | `/viewrecipients 1` |

### Gestión de Plantillas (Solo Admin)

| Comando | Ejemplo |
|---------|---------|
| `/createtemplate <nombre>\|\|\|<asunto>\|\|\|<cuerpo>` | Ver ejemplo abajo |
| `/listtemplates` | Ver todas las plantillas |

**Ejemplo de plantilla:**
```
/createtemplate bienvenida|||¡Bienvenido!|||<h1>Hola {name}</h1><p>Gracias por unirte a nosotros.</p>
```

**Variables disponibles:**
- `{name}` - Se reemplaza automáticamente con el nombre del destinatario

### Campañas (Solo Admin)

| Comando | Ejemplo |
|---------|---------|
| `/sendcampaign <nombre> <template_id> <list_id>` | `/sendcampaign "Black Friday" 1 1` |
| `/campaigns` | Ver todas las campañas |
| `/campaignstats <campaign_id>` | `/campaignstats 1` |

## 🎯 Flujo de Trabajo Típico

### Paso 1: Configurar SMTP
```
/setsmtp smtp.gmail.com 587 tu@gmail.com contraseña_app tu@gmail.com "Mi Empresa"
```

### Paso 2: Crear Lista de Correos
```
/createlist clientes "Lista de clientes 2024"
```

### Paso 3: Agregar Destinatarios
```
/addrecipient 1 cliente1@email.com "María García"
/addrecipient 1 cliente2@email.com "Pedro López"
/addrecipient 1 cliente3@email.com "Ana Martínez"
```

### Paso 4: Crear Plantilla
```
/createtemplate oferta|||¡Oferta Especial Solo Para Ti!|||
<html>
<body>
  <h1>Hola {name},</h1>
  <p>Tenemos una oferta especial solo para ti.</p>
  <p><strong>50% de descuento</strong> en todos nuestros productos.</p>
  <p>¡No te lo pierdas!</p>
  <p>Saludos,<br>El equipo</p>
</body>
</html>
```

### Paso 5: Enviar Campaña
```
/sendcampaign "Campaña Descuento" 1 1
```

### Paso 6: Ver Estadísticas
```
/campaignstats 1
```

## 📊 Estructura de Base de Datos

El sistema crea automáticamente las siguientes tablas:

- **members** - Usuarios con membresía
- **activity_log** - Registro de actividades
- **email_lists** - Listas de correos
- **email_recipients** - Destinatarios en cada lista
- **email_templates** - Plantillas de email
- **campaigns** - Campañas enviadas
- **smtp_config** - Configuración del servidor SMTP

## 🔐 Seguridad

- ✅ Sistema de permisos por roles (Admin/Miembros)
- ✅ Contraseñas SMTP almacenadas en base de datos local
- ✅ Validación de emails y datos
- ✅ Rate limiting entre envíos (1 segundo por defecto)
- ✅ Registro de todas las actividades

## ⚙️ Configuración Avanzada

### Ajustar delay entre emails

Por defecto hay 1 segundo de espera entre cada email. Para cambiar esto, modifica el valor en `email_sender.py`:

```python
delay_between_emails REAL DEFAULT 1.0
```

### Usar HTML en plantillas

Las plantillas soportan HTML completo:

```html
<html>
<head>
  <style>
    .header { background-color: #007bff; color: white; padding: 20px; }
    .content { padding: 20px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Bienvenido {name}</h1>
  </div>
  <div class="content">
    <p>Tu contenido aquí...</p>
  </div>
</body>
</html>
```

## 🐛 Solución de Problemas

### Error: "SMTP no configurado"
- Ejecuta `/setsmtp` con los datos correctos de tu servidor SMTP

### Error al enviar con Gmail
- Asegúrate de usar una "Contraseña de aplicación", no tu contraseña normal
- Verifica que la verificación en dos pasos esté activada

### Emails no llegan
- Verifica la carpeta de spam
- Confirma que la configuración SMTP sea correcta con `/smtpstatus`
- Revisa que los emails de destinatarios sean válidos

### Error: "Can't parse entities"
- Este error ocurría con caracteres especiales en HTML
- Ya está corregido usando `&lt;` y `&gt;` en lugar de `<>` en los mensajes

## 📝 Notas Importantes

- **Límites de envío:** Respeta los límites de tu proveedor SMTP
  - Gmail: 500 emails/día (cuenta gratuita)
  - SendGrid: Según tu plan
  - Mailgun: Según tu plan

- **Buenas prácticas:**
  - No envíes spam
  - Incluye siempre opción de desuscripción
  - Respeta las leyes de privacidad (GDPR, CAN-SPAM, etc.)
  - Usa listas opt-in (con consentimiento)

## 🆘 Soporte

Si tienes problemas o preguntas:
1. Revisa este README
2. Verifica los logs del bot
3. Usa `/help` para ver comandos disponibles
4. Contacta al administrador del bot

## 📄 Licencia

Este proyecto es de uso personal/comercial según los términos acordados.

---

**Desarrollado con ❤️ para facilitar el email tranzas**
