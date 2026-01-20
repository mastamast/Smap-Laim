# 🚀 Guía para Mantener el Bot Funcionando 24/7

Tienes varias opciones para mantener tu bot ejecutándose continuamente:

---

## 🖥️ OPCIÓN 1: En tu PC Windows (Gratis)

### Método A: Script de Auto-Reinicio (Simple)

1. **Ejecuta el script de auto-reinicio:**
   ```powershell
   .\run_bot_forever.ps1
   ```

   Este script reiniciará automáticamente el bot si se cae.

2. **Para ejecutarlo en segundo plano:**
   - Abre PowerShell como Administrador
   - Ejecuta:
     ```powershell
     Start-Process powershell -ArgumentList "-File `"$PWD\run_bot_forever.ps1`"" -WindowStyle Hidden
     ```

3. **Mantener la PC encendida:**
   - Ve a: Panel de Control → Opciones de energía
   - Selecciona "Alto rendimiento"
   - Configura "Suspender equipo" en "Nunca"

**✅ Pros:** Gratis, control total  
**❌ Contras:** Debes dejar tu PC encendida, consume electricidad

---

### Método B: Servicio de Windows (Recomendado para PC)

1. **Ejecuta como Administrador:**
   ```powershell
   .\install_service.ps1
   ```

2. **El bot se instalará como servicio y:**
   - Iniciará automáticamente al encender Windows
   - Se reiniciará automáticamente si falla
   - Se ejecutará en segundo plano

3. **Gestionar el servicio:**
   ```powershell
   # Ver estado
   .\nssm.exe status TelegramEmailBot

   # Detener
   .\nssm.exe stop TelegramEmailBot

   # Iniciar
   .\nssm.exe start TelegramEmailBot

   # Reiniciar
   .\nssm.exe restart TelegramEmailBot
   ```

4. **Ver en Servicios de Windows:**
   - Presiona `Win + R`
   - Escribe `services.msc`
   - Busca "Telegram Email Bot"

**✅ Pros:** Profesional, auto-inicio, auto-reinicio  
**❌ Contras:** Requiere PC encendida

---

## ☁️ OPCIÓN 2: Hosting en la Nube (24/7 Real)

### A. PythonAnywhere (Gratis hasta 1 bot)

1. **Crear cuenta:**
   - Ve a: https://www.pythonanywhere.com
   - Crea cuenta gratuita

2. **Subir archivos:**
   - Files → Upload → Sube todos tus archivos .py
   - Sube requirements.txt
   - Crea archivo .env con tus variables

3. **Instalar dependencias:**
   - En consola Bash:
     ```bash
     pip3 install --user -r requirements.txt
     ```

4. **Ejecutar bot:**
   - Tasks → Add a new scheduled task
   - Comando: `python3 /home/tuusuario/bot.py`
   - Schedule: @daily (se ejecuta cada día)

   **O mejor, usar Always-On task (plan pago):**
   - Necesita plan Hacker ($5/mes)
   - Permite procesos continuos

**✅ Pros:** Gratis básico, fácil de usar  
**❌ Contras:** Plan gratuito tiene limitaciones, necesita plan pago para 24/7 real

---

### B. Railway.app (Fácil y con plan gratuito)

1. **Crear cuenta:**
   - Ve a: https://railway.app
   - Conecta con GitHub

2. **Crear Procfile:**
   ```
   worker: python bot.py
   ```

3. **Subir a GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/tuusuario/tu-repo.git
   git push -u origin main
   ```

4. **Deploy en Railway:**
   - New Project → Deploy from GitHub
   - Selecciona tu repositorio
   - Agrega variables de entorno (TELEGRAM_BOT_TOKEN, ADMIN_USER_ID)
   - Deploy automático

**✅ Pros:** Fácil, $5 gratis/mes, auto-deploy  
**❌ Contras:** Plan gratuito limitado a $5/mes de uso

---

### C. Render.com (Gratis con limitaciones)

1. **Crear cuenta en Render.com**

2. **Crear Procfile:**
   ```
   worker: python bot.py
   ```

3. **Deploy:**
   - New → Background Worker
   - Conecta GitHub
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
   - Agrega variables de entorno

**✅ Pros:** Gratis para servicios background  
**❌ Contras:** Se duerme después de 15 min de inactividad (no aplica a bots)

---

### D. Google Cloud Platform / AWS (Profesional)

**Google Cloud Run:**
- $300 créditos gratis
- Siempre gratuito hasta cierto uso
- Escalable

**AWS EC2:**
- 12 meses gratis (750 horas/mes)
- t2.micro instance

**DigitalOcean:**
- Droplet desde $4/mes
- VPS completo con control total

---

## 🐳 OPCIÓN 3: Docker (Portable)

1. **Crear Dockerfile:**
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["python", "bot.py"]
   ```

2. **Crear docker-compose.yml:**
   ```yaml
   version: '3.8'
   services:
     bot:
       build: .
       restart: always
       env_file:
         - .env
       volumes:
         - ./membership.db:/app/membership.db
   ```

3. **Ejecutar:**
   ```bash
   docker-compose up -d
   ```

**✅ Pros:** Portable, fácil de mover entre servidores  
**❌ Contras:** Requiere aprender Docker

---

## 📊 Comparación de Opciones

| Opción | Costo | Facilidad | Uptime | Recomendado Para |
|--------|-------|-----------|--------|------------------|
| PC Windows (Script) | Gratis | ⭐⭐⭐⭐⭐ | 🟨 Requiere PC encendida | Pruebas locales |
| PC Windows (Servicio) | Gratis | ⭐⭐⭐⭐ | 🟨 Requiere PC encendida | Uso personal |
| Railway.app | $5/mes gratis | ⭐⭐⭐⭐⭐ | 🟢 24/7 | **Mejor para empezar** |
| Render.com | Gratis | ⭐⭐⭐⭐⭐ | 🟢 24/7 | Bots con poco tráfico |
| PythonAnywhere | $5/mes | ⭐⭐⭐⭐ | 🟢 24/7 | Python específico |
| VPS (DigitalOcean) | $4/mes | ⭐⭐⭐ | 🟢 24/7 | Control total |
| Google Cloud / AWS | Variable | ⭐⭐ | 🟢 99.9% | Empresarial |

---

## 🎯 Mi Recomendación

**Para empezar AHORA (Gratis en tu PC):**
1. Ejecuta `.\run_bot_forever.ps1` para tenerlo funcionando inmediatamente
2. O instala como servicio con `.\install_service.ps1` (requiere admin)

**Para 24/7 real (en la nube):**
1. **Railway.app** - Más fácil y tiene $5 gratis al mes (suficiente para un bot)
2. Sube tu código a GitHub
3. Despliega en Railway en 5 minutos

---

## ⚡ Quick Start - Railway (5 minutos)

```bash
# 1. Crear Procfile
echo "worker: python bot.py" > Procfile

# 2. Crear .gitignore
echo "*.db
.env
__pycache__/
*.pyc" > .gitignore

# 3. Subir a GitHub
git init
git add .
git commit -m "Bot de Telegram"
git branch -M main
# Crea un repo en GitHub primero
git remote add origin https://github.com/tuusuario/telegram-bot.git
git push -u origin main

# 4. Ve a Railway.app
# - New Project → Deploy from GitHub
# - Selecciona el repo
# - Agrega variables: TELEGRAM_BOT_TOKEN, ADMIN_USER_ID
# - Deploy
```

---

¿Necesitas ayuda con alguna opción específica?
