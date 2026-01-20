# 🚂 Guía de Despliegue en Railway.app

## 📋 Requisitos Previos

- Cuenta de GitHub
- Cuenta de Railway.app (usa GitHub para registrarte)
- Tu código en un repositorio de GitHub

---

## 🚀 Paso 1: Preparar el Repositorio

### 1.1 Inicializar Git (si no lo has hecho)

```powershell
git init
git add .
git commit -m "Initial commit - Telegram Email Bot"
git branch -M main
```

### 1.2 Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `telegram-email-bot` (o el que prefieras)
3. **NO inicialices** con README, .gitignore o licencia
4. Click "Create repository"

### 1.3 Subir el Código

```powershell
git remote add origin https://github.com/TU_USUARIO/telegram-email-bot.git
git push -u origin main
```

---

## 🚂 Paso 2: Desplegar en Railway

### 2.1 Crear Proyecto

1. Ve a https://railway.app
2. Click "Start a New Project"
3. Selecciona "Deploy from GitHub repo"
4. Autoriza Railway para acceder a GitHub (si es primera vez)
5. Selecciona tu repositorio `telegram-email-bot`

### 2.2 Configurar Variables de Entorno

Una vez creado el proyecto:

1. Click en tu servicio
2. Ve a la pestaña "Variables"
3. Agrega las siguientes variables:

   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   ADMIN_USER_ID=tu_id_aqui
   ```

4. Click "Add" para cada variable

### 2.3 Configurar Railway Volume (Para persistir la base de datos)

**Opción A: Usando Railway Volumes (Recomendado)**

1. En el dashboard del proyecto, click en tu servicio
2. Ve a "Settings" → "Volumes"
3. Click "New Volume"
4. Configuración:
   - **Mount Path**: `/app`
   - **Name**: `bot-data`
5. Click "Add Volume"

Esto persistirá tu archivo `membership.db` entre deployments.

**Opción B: Usar una base de datos externa**

Si prefieres no usar volúmenes, Railway ofrece bases de datos PostgreSQL/MySQL/MongoDB:

1. En el dashboard, click "+ New"
2. Selecciona "Database" → "PostgreSQL" (o la que prefieras)
3. Railway creará automáticamente las variables de conexión
4. Actualiza `database.py` para usar la base de datos externa en lugar de SQLite

---

## ⚙️ Paso 3: Verificar el Despliegue

### 3.1 Ver Logs

1. En tu servicio, ve a "Deployments"
2. Click en el deployment más reciente
3. Ve a "View Logs"
4. Deberías ver:
   ```
   ✅ Configuración validada correctamente
   🤖 Inicializando bot...
   🚀 BOT DE TELEGRAM INICIADO
   ✅ El bot está ejecutándose...
   ```

### 3.2 Probar el Bot

1. Abre Telegram
2. Envía `/start` a tu bot
3. Deberías recibir el menú principal

---

## 🔄 Actualizaciones Automáticas

Railway redesplegará automáticamente cuando hagas push a GitHub:

```powershell
git add .
git commit -m "Actualización del bot"
git push
```

Railway detectará el cambio y redesplegar automáticamente.

---

## 📊 Monitoreo

### Ver Métricas

1. En tu servicio, ve a "Metrics"
2. Verás:
   - CPU usage
   - Memory usage
   - Network traffic

### Ver Logs en Tiempo Real

```powershell
# Instala Railway CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

---

## 💰 Costos

Railway ofrece:

- **Plan Hobby**: $5 de crédito gratis al mes
- **Plan Pro**: $20/mes con $20 de crédito incluido

Un bot simple de Telegram consume muy poco:
- ~$0.50 - $2 al mes
- El plan gratuito es suficiente para empezar

---

## 🔧 Troubleshooting

### El bot no inicia

**Verifica los logs:**
1. Ve a "Deployments" → Click en el último → "View Logs"
2. Busca errores

**Problemas comunes:**
- Variables de entorno mal configuradas
- Token de Telegram incorrecto
- ID de admin incorrecto

### La base de datos se borra en cada deploy

**Solución:** Asegúrate de tener configurado el Railway Volume:
1. Settings → Volumes
2. Mount path: `/app`
3. Esto persistirá `membership.db`

### Error: "Port already in use"

Los bots de Telegram no usan puertos HTTP. Railway puede mostrar una advertencia, ignórala.

---

## 🛠️ Comandos Útiles Railway CLI

```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Enlazar proyecto
railway link

# Ver logs
railway logs

# Ejecutar comando en el servicio
railway run python bot.py

# Ver variables
railway variables

# Agregar variable
railway variables set TELEGRAM_BOT_TOKEN=tu_token

# Abrir en navegador
railway open
```

---

## 🔐 Seguridad

### ✅ Buenas Prácticas

1. **NUNCA hagas commit del archivo .env**
   - Ya está en `.gitignore`
   - Usa solo variables de Railway

2. **Rota tu token regularmente**
   - Ve a @BotFather en Telegram
   - `/token` → selecciona tu bot → "Revoke current token"

3. **Mantén actualizado tu código**
   ```powershell
   git pull
   # hacer cambios
   git add .
   git commit -m "Security update"
   git push
   ```

---

## 📱 Configuración Avanzada

### Auto-scaling (Plan Pro)

Railway puede escalar automáticamente si tu bot crece:

1. Settings → "Deployment"
2. "Replicas": Ajusta el número de instancias

### Custom Domain

Si quieres un dominio personalizado para webhooks:

1. Settings → "Networking"
2. "Custom Domain"
3. Agrega tu dominio

---

## ✅ Checklist de Deployment

- [ ] Código subido a GitHub
- [ ] Proyecto creado en Railway
- [ ] Variables de entorno configuradas
- [ ] Railway Volume configurado (para persistir DB)
- [ ] Bot iniciado correctamente (verificar logs)
- [ ] Prueba con `/start` en Telegram
- [ ] Configuración SMTP verificada con `/smtpstatus`

---

## 🆘 Soporte

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Twitter: @Railway

**Este Bot:**
- GitHub Issues: En tu repositorio
- Logs: `railway logs` o en el dashboard

---

¡Listo! Tu bot estará funcionando 24/7 en la nube. 🎉
