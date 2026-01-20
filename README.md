# 🤖 Bot de Telegram con Sistema de Membresías

Bot profesional de Telegram desarrollado en Python con sistema robusto de autenticación y autorización de usuarios mediante membresías.

## 📋 Características

- ✅ **Sistema de Membresías**: Control de acceso basado en membresías de usuario
- 🔐 **Autenticación Robusta**: Solo usuarios autorizados pueden acceder a las funcionalidades
- 👑 **Panel de Administración**: Gestión completa de membresías desde Telegram
- 📊 **Base de Datos SQLite**: Almacenamiento persistente de miembros y actividades
- 📝 **Registro de Actividades**: Log completo de todas las acciones administrativas
- 🔧 **Puntos de Integración**: Arquitectura preparada para integrar funcionalidades personalizadas

## 🚀 Instalación

### Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Instalar dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno**:
   
   El archivo `.env` ya está configurado con tus credenciales:
   ```
   TELEGRAM_BOT_TOKEN=8369750982:AAGKsQS_LBRXIMpTIY7o7fklpK_GMnAObpk
   ADMIN_USER_ID=6981281428
   ```

3. **Ejecutar el bot**:
   ```powershell
   python bot.py
   ```

## 📖 Uso

### Comandos Públicos

| Comando | Descripción |
|---------|-------------|
| `/start` | Inicia el bot y muestra mensaje de bienvenida |
| `/help` | Muestra ayuda y comandos disponibles |
| `/status` | Muestra el estado de membresía del usuario |

### Comandos de Administrador

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/addmember <user_id>` | Añade un nuevo miembro | `/addmember 123456789` |
| `/removemember <user_id>` | Elimina un miembro | `/removemember 123456789` |
| `/listmembers` | Lista todos los miembros activos | `/listmembers` |
| `/memberinfo <user_id>` | Muestra información de un miembro | `/memberinfo 123456789` |
| `/stats` | Muestra estadísticas del bot | `/stats` |
| `/logs` | Muestra registro de actividades | `/logs` |

### Comandos Funcionales (Solo Miembros)

| Comando | Descripción |
|---------|-------------|
| `/execute` | Ejecuta la funcionalidad principal (placeholder) |

## 🏗️ Arquitectura del Proyecto

```
spammailk/
├── bot.py              # Punto de entrada principal
├── config.py           # Gestión de configuración
├── database.py         # Módulo de base de datos
├── handlers.py         # Manejadores de comandos
├── decorators.py       # Decoradores de seguridad
├── requirements.txt    # Dependencias del proyecto
├── .env               # Variables de entorno (configurado)
├── .env.example       # Ejemplo de variables de entorno
├── .gitignore         # Archivos ignorados por git
└── README.md          # Este archivo
```

## 🔧 Integración de Funcionalidades Personalizadas

El bot está diseñado con puntos de integración claros para añadir funcionalidades específicas:

### Opción 1: Modificar el Comando `/execute`

Edita la función `execute_command` en `handlers.py`:

```python
@members_only
@log_command
async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /execute - Ejecuta la funcionalidad principal del bot
    """
    user_id = update.effective_user.id
    
    # TU CÓDIGO PERSONALIZADO AQUÍ
    # Ejemplo: procesar datos, consultar APIs, etc.
    
    result = tu_funcion_personalizada(user_id, context.args)
    
    await update.message.reply_text(result)
```

### Opción 2: Crear Nuevos Comandos

Añade nuevos manejadores en `handlers.py`:

```python
@members_only
@log_command
async def tu_comando_personalizado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tu nueva funcionalidad"""
    # Tu código aquí
    pass
```

Luego regístralo en `bot.py`:

```python
application.add_handler(CommandHandler("tucomando", tu_comando_personalizado))
```

### Opción 3: Importar Módulos Externos

Crea un archivo `funcionalidades.py` con tu código existente:

```python
# funcionalidades.py
def tu_funcionalidad_existente(parametros):
    # Tu código existente aquí
    return resultado
```

Luego impórtalo en `handlers.py`:

```python
from funcionalidades import tu_funcionalidad_existente

@members_only
@log_command
async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resultado = tu_funcionalidad_existente(context.args)
    await update.message.reply_text(resultado)
```

## 🔒 Sistema de Seguridad

### Decoradores Disponibles

- `@admin_only`: Restringe acceso solo al administrador
- `@members_only`: Permite acceso solo a miembros autorizados
- `@log_command`: Registra el uso de comandos en consola

### Flujo de Autenticación

1. Usuario envía un comando
2. El decorador verifica la identidad
3. Si es admin → acceso total
4. Si es miembro → acceso a comandos funcionales
5. Si no tiene membresía → mensaje de denegación

## 💾 Base de Datos

El bot utiliza SQLite con las siguientes tablas:

### Tabla `members`
- `user_id` (PRIMARY KEY): ID de Telegram del usuario
- `username`: Nombre de usuario de Telegram
- `first_name`: Nombre del usuario
- `last_name`: Apellido del usuario
- `added_date`: Fecha de registro
- `added_by`: ID del admin que añadió al usuario
- `is_active`: Estado de la membresía

### Tabla `activity_log`
- `id` (PRIMARY KEY): ID del registro
- `user_id`: ID del usuario afectado
- `action`: Acción realizada
- `timestamp`: Fecha y hora
- `performed_by`: ID de quien realizó la acción

## 🛠️ Mantenimiento

### Ver Logs en Tiempo Real

El bot muestra logs en consola al ejecutarse:

```
[LOG] Usuario 123456789 (@username) ejecutó: /start
```

### Backup de la Base de Datos

La base de datos se guarda en `membership.db`. Para hacer backup:

```powershell
Copy-Item membership.db membership_backup.db
```

### Actualizar Dependencias

```powershell
pip install --upgrade -r requirements.txt
```

## 📞 Soporte

Para obtener tu ID de usuario de Telegram:
1. Inicia el bot con `/start`
2. Usa el comando `/status`
3. Tu ID aparecerá en el mensaje

## 📝 Licencia

Este proyecto es propietario y confidencial.

## 👨‍💻 Desarrollo

**Versión**: 1.0.0  
**Lenguaje**: Python 3.10+  
**Framework**: python-telegram-bot 20.7  
**Base de Datos**: SQLite  

---

✨ **Bot desarrollado con estándares profesionales y ejecutivos**
