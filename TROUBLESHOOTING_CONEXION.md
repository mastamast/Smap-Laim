# 🔧 Solución de Problemas: "Conexión Cerrada Inesperadamente"

**Error Reportado:**
```
❌ Error inesperado
Detalle: Conexión cerrada inesperadamente
```

---

## 📋 Causas Potenciales

### 1. **Problemas de Configuración SMTP** (Más Común)

#### 1.1 Puerto Incorrecto o Bloqueado
- **Causa:** El puerto configurado no coincide con el protocolo TLS/SSL del servidor
- **Detalles:**
  - Puerto 587: Requiere TLS (STARTTLS)
  - Puerto 465: Requiere SSL/TLS directo
  - Puerto 25: Sin cifrado (bloqueado por la mayoría de ISPs)
  - Firewall o antivirus bloqueando conexiones salientes

#### 1.2 Configuración TLS/SSL Incorrecta
- **Causa:** Incompatibilidad entre el modo de cifrado configurado y el esperado por el servidor
- **Detalles:**
  - Servidor espera TLS pero está deshabilitado en la configuración
  - Intento de usar STARTTLS en puerto SSL directo (465)
  - Certificados SSL expirados o inválidos

#### 1.3 Servidor SMTP Inaccesible
- **Causa:** El servidor no está disponible o rechaza la conexión
- **Detalles:**
  - Servidor en mantenimiento
  - Límites de tasa alcanzados (rate limiting)
  - IP bloqueada por intentos fallidos previos
  - Servidor requiere autenticación especial

### 2. **Problemas de Red y Conectividad**

#### 2.1 Firewall o Proxy Corporativo
- **Causa:** Red corporativa o firewall bloqueando conexiones SMTP salientes
- **Detalles:**
  - Puertos 587/465 bloqueados
  - Deep packet inspection interfiriendo con TLS
  - Proxy SMTP no configurado

#### 2.2 Timeout de Conexión
- **Causa:** El servidor tarda demasiado en responder
- **Detalles:**
  - Conexión lenta o inestable
  - Servidor sobrecargado
  - Timeout configurado muy bajo (actual: 10 segundos)

#### 2.3 DNS o Resolución de Nombres
- **Causa:** No se puede resolver el nombre del servidor SMTP
- **Detalles:**
  - DNS caído o mal configurado
  - Nombre de servidor incorrecto

### 3. **Problemas con Proveedores Específicos**

#### 3.1 Gmail
- **Causa:** Restricciones de seguridad de Google
- **Detalles:**
  - "Acceso de apps menos seguras" deshabilitado (ya no disponible)
  - Contraseña de aplicación no generada o incorrecta
  - Verificación en dos pasos no activada
  - IP sospechosa detectada por Google

#### 3.2 Outlook/Hotmail
- **Causa:** Políticas de seguridad de Microsoft
- **Detalles:**
  - Autenticación moderna (OAuth) requerida
  - Cuenta bloqueada por actividad sospechosa
  - Configuración de seguridad restrictiva

#### 3.3 Yahoo
- **Causa:** Configuración de seguridad de Yahoo
- **Detalles:**
  - "Acceso de apps menos seguras" deshabilitado
  - Contraseña de aplicación requerida

### 4. **Problemas del Sistema/Bot**

#### 4.1 Recursos del Sistema
- **Causa:** Recursos insuficientes en el servidor donde corre el bot
- **Detalles:**
  - Memoria RAM insuficiente
  - CPU sobrecargado
  - Demasiadas conexiones simultáneas

#### 4.2 Versiones de Bibliotecas
- **Causa:** Bibliotecas Python desactualizadas o incompatibles
- **Detalles:**
  - `smtplib` con bugs conocidos
  - Conflictos de versiones SSL/TLS
  - Python 3.13 con problemas de compatibilidad

#### 4.3 Antivirus o Software de Seguridad
- **Causa:** Software de seguridad interfiriendo con conexiones
- **Detalles:**
  - Antivirus bloqueando Python
  - Firewall de Windows bloqueando puertos
  - Software de monitoreo SSL interceptando conexiones

### 5. **Errores de Implementación**

#### 5.1 Credenciales Incorrectas
- **Causa:** Usuario o contraseña mal configurados
- **Detalles:**
  - Espacios adicionales al copiar/pegar
  - Contraseña de aplicación vs contraseña normal
  - Usuario incorrecto (debe ser email completo)

#### 5.2 Datos de Configuración Corruptos
- **Causa:** Base de datos con información inconsistente
- **Detalles:**
  - Caracteres especiales mal codificados
  - Null values en campos requeridos
  - Formato de datos incorrecto

---

## 🛠️ Pasos de Solución de Problemas y Verificación de Configuración

### **Fase 1: Verificación Básica**

#### Paso 1.1: Verificar Estado Actual del Bot
```bash
# Verificar que el bot esté ejecutándose
# En PowerShell:
Get-Process python

# Ver logs del bot
# Revisar el output de la terminal donde corre python bot.py
```

**Qué buscar:**
- ✅ Bot iniciado correctamente
- ✅ Sin errores en los logs
- ❌ Errores de conexión repetidos

#### Paso 1.2: Verificar Configuración SMTP Almacenada
```
En Telegram:
/smtpstatus
```

**Verificar:**
- ✅ Servidor SMTP correcto
- ✅ Puerto correcto
- ✅ Usuario (email) completo
- ✅ TLS activado/desactivado según corresponda

**Valores Correctos por Proveedor:**

| Proveedor | Servidor | Puerto | TLS |
|-----------|----------|--------|-----|
| Gmail | smtp.gmail.com | 587 | Activado |
| Outlook/Hotmail | smtp.office365.com | 587 | Activado |
| Yahoo | smtp.mail.yahoo.com | 587 | Activado |
| SendGrid | smtp.sendgrid.net | 587 | Activado |

#### Paso 1.3: Probar Conexión Desde el Bot
```
En Telegram:
/start
→ Email Tranzas
→ Config Email
→ 🧪 Probar Conexión
```

**Resultado Esperado:**
- ✅ "Conexión Exitosa" = Configuración correcta
- ❌ "Error de Autenticación" = Ir a Fase 2
- ❌ "Error de Conexión" = Ir a Fase 3
- ❌ "Error Inesperado" = Continuar con pasos siguientes

---

### **Fase 2: Verificación de Credenciales**

#### Paso 2.1: Verificar Contraseña de Aplicación (Gmail)

**Si usas Gmail:**

1. **Verificar Verificación en 2 Pasos:**
   - Ve a: https://myaccount.google.com/security
   - Busca "Verificación en dos pasos"
   - Debe estar **ACTIVADA**

2. **Generar Nueva Contraseña de Aplicación:**
   - Ve a: https://myaccount.google.com/apppasswords
   - Selecciona "Correo" y "Otro (nombre personalizado)"
   - Escribe: "Bot Telegram Tranzas"
   - Click en "Generar"
   - **Copia la contraseña de 16 caracteres** (sin espacios)

3. **Reconfigurar en el Bot:**
   ```
   /setsmtp smtp.gmail.com 587 tu@gmail.com CONTRASEÑA_16_CARACTERES tu@gmail.com "Tu Nombre"
   ```

#### Paso 2.2: Verificar Contraseña de Aplicación (Outlook)

**Si usas Outlook/Hotmail:**

1. Ve a: https://account.microsoft.com/security
2. "Opciones de seguridad avanzadas"
3. "Contraseñas de aplicación"
4. Crear nueva contraseña
5. Reconfigurar en el bot

#### Paso 2.3: Verificar Formato de Credenciales

**Errores Comunes:**
```bash
# ❌ INCORRECTO:
Usuario:  miusuario          # Falta @dominio.com
Email:    email @gmail.com   # Espacio extra
Password: mi contraseña      # Espacios en la contraseña

# ✅ CORRECTO:
Usuario:  miusuario@gmail.com
Email:    email@gmail.com
Password: abcd1234efgh5678   # Sin espacios
```

---

### **Fase 3: Verificación de Red y Conectividad**

#### Paso 3.1: Probar Conexión al Servidor SMTP

**En PowerShell (como Administrador):**

```powershell
# Test 1: Verificar resolución DNS
nslookup smtp.gmail.com

# Test 2: Verificar conectividad al puerto
Test-NetConnection -ComputerName smtp.gmail.com -Port 587

# Test 3: Verificar firewall
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Python*"}
```

**Resultado Esperado:**
```
Test 1: Debe mostrar IP del servidor
Test 2: TcpTestSucceeded debe ser True
Test 3: Debe mostrar reglas permitiendo Python
```

#### Paso 3.2: Verificar Firewall de Windows

1. Abrir "Firewall de Windows Defender"
2. "Permitir una aplicación a través del Firewall"
3. Buscar "Python" o "python.exe"
4. Asegurarse que esté **permitido en Privada y Pública**

**Si no aparece:**
```powershell
# Agregar regla para Python (como Administrador)
New-NetFirewallRule -DisplayName "Python Bot SMTP" -Direction Outbound -Program "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_*\python.exe" -Action Allow -Protocol TCP -LocalPort Any -RemotePort 587,465
```

#### Paso 3.3: Verificar Antivirus

**Pasos:**
1. Abre tu antivirus (Windows Defender, Avast, etc.)
2. Ve a configuración de "Protección de red" o "Firewall"
3. Agrega excepción para:
   - `python.exe`
   - Carpeta del proyecto: `C:\Users\AXELm\OneDrive\Desktop\proyectos\spammailk`
4. Reinicia el bot

#### Paso 3.4: Probar con VPN/Otra Red

**Si estás en red corporativa o universitaria:**
- Intenta conectarte a una red móvil (hotspot del celular)
- Usa una VPN
- Prueba desde otra ubicación

---

### **Fase 4: Verificación de Configuración del Bot**

#### Paso 4.1: Verificar Base de Datos

**Verificar integridad de la configuración SMTP:**

```powershell
# Abrir la base de datos
sqlite3 membership.db

# Ver configuración actual
SELECT * FROM smtp_config;

# Salir
.quit
```

**Qué buscar:**
- Todos los campos deben tener valores
- No debe haber NULL en campos críticos
- Contraseña debe estar presente (aunque encriptada)

#### Paso 4.2: Limpiar y Reconfigurar

**Opción 1: Reconfigurar desde el bot**
```
/start → Email Tranzas → Config Email → 🔄 Reconfigurar
```

**Opción 2: Limpiar base de datos (⚠️ Cuidado)**
```sql
-- Solo si es necesario
DELETE FROM smtp_config;
```

Luego reconfigurar:
```
/setsmtp smtp.gmail.com 587 tu@gmail.com tu_contraseña tu@gmail.com "Tu Nombre"
```

#### Paso 4.3: Aumentar Timeout

**Editar `enhanced_callback_handlers.py` línea 43:**

```python
# Antes:
with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=10) as server:

# Después (aumentar a 30 segundos):
with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=30) as server:
```

**Reiniciar el bot:**
```powershell
# En la terminal donde corre el bot: Ctrl+C
# Luego:
python bot.py
```

---

### **Fase 5: Pruebas Específicas por Proveedor**

#### Gmail - Lista de Verificación Completa

**☑️ Pre-requisitos:**
- [ ] Cuenta de Gmail válida
- [ ] Verificación en 2 pasos ACTIVADA
- [ ] Contraseña de aplicación generada

**☑️ Configuración:**
```
Servidor: smtp.gmail.com
Puerto: 587
TLS: Activado
Usuario: tu_email@gmail.com (email completo)
Password: contraseña de 16 caracteres SIN espacios
```

**☑️ Verificaciones Adicionales:**
1. Revisar actividad reciente en: https://myaccount.google.com/notifications
2. Si hay "Intento de inicio de sesión bloqueado", aprobar el dispositivo
3. Desactivar temporalmente "Protección avanzada" si está activa

#### Outlook/Hotmail - Lista de Verificación

**☑️ Pre-requisitos:**
- [ ] Cuenta de Outlook/Hotmail/Live válida
- [ ] Contraseña de aplicación generada (si está habilitado 2FA)

**☑️ Configuración:**
```
Servidor: smtp.office365.com
Puerto: 587
TLS: Activado
Usuario: tu_email@outlook.com
Password: tu_contraseña o contraseña_de_aplicación
```

**☑️ Verificaciones Adicionales:**
1. Ve a: https://account.microsoft.com/activity
2. Revisa actividades recientes
3. Desbloquea tu cuenta si es necesario

#### Yahoo - Lista de Verificación

**☑️ Configuración:**
```
Servidor: smtp.mail.yahoo.com
Puerto: 587
TLS: Activado
Usuario: tu_email@yahoo.com
Password: contraseña_de_aplicación (NO contraseña normal)
```

**☑️ Generar Contraseña de Aplicación:**
1. Ve a: https://login.yahoo.com/account/security
2. "Generar contraseña de aplicación"
3. Selecciona "Otra app"
4. Nombra: "Bot Telegram"
5. Usa la contraseña generada

---

### **Fase 6: Diagnóstico Avanzado**

#### Paso 6.1: Capturar Logs Detallados

**Modificar temporalmente `enhanced_callback_handlers.py`:**

```python
# Línea 40-46, agregar logging:
try:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    context_ssl = ssl.create_default_context()
    with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=10) as server:
        server.set_debuglevel(2)  # ← AGREGAR ESTA LÍNEA
        if config['use_tls']:
            server.starttls(context=context_ssl)
        server.login(config['smtp_username'], config['smtp_password'])
```

**Reiniciar el bot y probar conexión:**
- Los logs aparecerán en la consola
- Buscar el mensaje exacto del error
- Compartir con administrador si es necesario

#### Paso 6.2: Prueba Manual con Python

**Crear archivo `test_smtp.py`:**

```python
import smtplib
import ssl

# TUS DATOS AQUÍ
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USERNAME = "tu@gmail.com"
PASSWORD = "tu_contraseña_de_aplicacion"

try:
    print("🔄 Conectando...")
    context_ssl = ssl.create_default_context()
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
        server.set_debuglevel(2)
        print("✅ Conexión establecida")
        
        print("🔒 Iniciando TLS...")
        server.starttls(context=context_ssl)
        print("✅ TLS establecido")
        
        print("🔑 Autenticando...")
        server.login(USERNAME, PASSWORD)
        print("✅ Autenticación exitosa")
        
    print("\n🎉 TODO CORRECTO")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Detalle: {str(e)}")
```

**Ejecutar:**
```powershell
python test_smtp.py
```

**Analizar resultado:**
- Si funciona aquí pero no en el bot → Problema del bot
- Si falla aquí → Problema de red/configuración/credenciales

#### Paso 6.3: Verificar Versiones de Software

```powershell
# Verificar versión de Python
python --version

# Verificar bibliotecas instaladas
pip list | Select-String "telegram|smtp"

# Actualizar python-telegram-bot si es necesario
pip install --upgrade python-telegram-bot
```

---

### **Fase 7: Soluciones Alternativas**

#### Opción 1: Usar Otro Servidor SMTP

**SendGrid (Gratis hasta 100 emails/día):**

1. Registrarse en: https://sendgrid.com/
2. Crear API Key
3. Configurar:
   ```
   Servidor: smtp.sendgrid.net
   Puerto: 587
   Usuario: apikey (literal "apikey")
   Password: TU_API_KEY
   ```

#### Opción 2: Usar Servicio SMTP Dedicado

**Mailgun, Amazon SES, etc.:**
- Más confiables para envíos masivos
- Menos restricciones
- Mejor deliverability

#### Opción 3: Configurar Relay SMTP Local

**Para redes corporativas:**
- Configurar relay SMTP interno
- Usar servidor SMTP de la empresa
- Consultar con IT

---

### **Fase 8: Verificación Post-Solución**

#### Checklist Final

**Una vez resuelto el problema:**

1. **✅ Probar Conexión:**
   ```
   /start → Email Tranzas → Config Email → 🧪 Probar Conexión
   ```
   Resultado: "✅ ¡Conexión Exitosa!"

2. **✅ Enviar Email de Prueba:**
   - Crear lista de prueba
   - Agregar tu propio email
   - Crear plantilla simple
   - Enviar campaña de prueba

3. **✅ Verificar Recepción:**
   - Revisar inbox
   - Revisar spam
   - Confirmar que llegó

4. **✅ Documentar Solución:**
   - Anotar qué funcionó
   - Guardar configuración correcta
   - Crear backup de configuración

---

## 📊 Matriz de Diagnóstico Rápido

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| Error solo con Gmail | Contraseña incorrecta | Usar contraseña de aplicación |
| Error en red corporativa | Firewall bloqueando | Usar VPN o red móvil |
| Error intermitente | Timeout | Aumentar timeout a 30s |
| Error después de actualizar | Versión incompatible | Actualizar bibliotecas |
| Error con todos los proveedores | Firewall de Windows | Agregar excepción Python |
| Error específico de un servidor | Servidor caído | Probar otro proveedor |

---

## 🆘 Cuándo Contactar Soporte

**Contacta al administrador del bot si:**
- ✅ Completaste todas las fases sin éxito
- ✅ El test manual de Python funciona pero el bot no
- ✅ Tienes logs de error detallados para compartir
- ✅ Has probado con múltiples proveedores SMTP

**Información a proporcionar:**
1. Proveedor SMTP usado (Gmail, Outlook, etc.)
2. Logs completos del error
3. Resultado del test manual (test_smtp.py)
4. Configuración de red (corporativa/doméstica)
5. Capturas de pantalla del error

---

## 📚 Recursos Adicionales

**Documentación Oficial:**
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- Outlook SMTP: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353
- Python smtplib: https://docs.python.org/3/library/smtplib.html

**Herramientas de Diagnóstico:**
- Test de puerto SMTP: https://www.gmass.co/smtp-test
- Test de conectividad: https://mxtoolbox.com/

**Contacto:**
- Issues del proyecto (si está en GitHub)
- Email del administrador
- Documentación interna: README_EMAIL_TRANZAS.md

---

**Actualizado:** 2026-01-20  
**Versión:** 1.0  
**Sistema:** Bot de Telegram con Email Tranzas
