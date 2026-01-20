# 🚨 Guía Rápida: Error "Conexión Cerrada Inesperadamente"

**⏱️ Tiempo estimado de solución: 5-15 minutos**

---

## 🎯 Solución Rápida (90% de los casos)

### Para Usuarios de **Gmail** (MÁS COMÚN):

1. **Ve a:** https://myaccount.google.com/apppasswords
2. **Genera** una contraseña de aplicación
3. **Copia** la contraseña de 16 caracteres
4. **En el bot, escribe:**
   ```
   /setsmtp smtp.gmail.com 587 tu@gmail.com CONTRASEÑA_16_CARACTERES tu@gmail.com "Tu Nombre"
   ```
5. **Prueba la conexión:**
   ```
   /start → Email Tranzas → Config Email → 🧪 Probar Conexión
   ```

**✅ Si sale "Conexión Exitosa" = ¡Listo!**

---

### Para Usuarios de **Outlook/Hotmail**:

1. **Usa esta configuración:**
   ```
   /setsmtp smtp.office365.com 587 tu@outlook.com TU_CONTRASEÑA tu@outlook.com "Tu Nombre"
   ```

---

### Para Usuarios de **Yahoo**:

1. **Genera contraseña de aplicación:** https://login.yahoo.com/account/security
2. **Usa esta configuración:**
   ```
   /setsmtp smtp.mail.yahoo.com 587 tu@yahoo.com CONTRASEÑA_APP tu@yahoo.com "Tu Nombre"
   ```

---

## 🔧 Si Aún No Funciona

### Opción 1: Ejecutar Diagnóstico Automático

```powershell
python diagnostico_smtp.py
```

**Sigue las instrucciones en pantalla.** El script te dirá exactamente qué está fallando.

---

### Opción 2: Verificar Firewall (Windows)

1. **Abrir PowerShell como Administrador**
2. **Ejecutar:**
   ```powershell
   Test-NetConnection -ComputerName smtp.gmail.com -Port 587
   ```
3. **Debe decir:** `TcpTestSucceeded : True`
4. **Si dice False:**
   ```powershell
   # Agregar regla de firewall
   New-NetFirewallRule -DisplayName "Python SMTP" -Direction Outbound -Action Allow -Protocol TCP -RemotePort 587,465
   ```

---

### Opción 3: Probar con Otra Red

**Si estás en red corporativa/universidad:**
- 📱 Usa hotspot del celular
- 🌐 Usa una VPN
- 🏠 Prueba desde casa

**Las redes corporativas a menudo bloquean puertos SMTP.**

---

## 📋 Checklist de 2 Minutos

- [ ] ¿Usas Gmail? → ¿Generaste contraseña de aplicación?
- [ ] ¿El servidor es correcto? (smtp.gmail.com para Gmail)
- [ ] ¿El puerto es 587?
- [ ] ¿Escribiste el email completo? (usuario@gmail.com)
- [ ] ¿La contraseña NO tiene espacios?
- [ ] ¿Probaste desde otra red?

---

## 🆘 Ayuda Adicional

**Documentación Completa:**
- 📖 [TROUBLESHOOTING_CONEXION.md](./TROUBLESHOOTING_CONEXION.md) - Guía paso a paso detallada
- 📖 [README_EMAIL_TRANZAS.md](./README_EMAIL_TRANZAS.md) - Manual completo del sistema

**Herramientas:**
- 🔧 `python diagnostico_smtp.py` - Diagnóstico automático
- 🧪 Dentro del bot: `/start` → `Email Tranzas` → `Config Email` → `🧪 Probar Conexión`

---

## 💡 Causas Más Comunes

| # | Causa | Solución |
|---|-------|----------|
| 1 | Contraseña normal en vez de contraseña de aplicación | Generar contraseña de aplicación |
| 2 | Firewall bloqueando puerto 587 | Agregar excepción en firewall |
| 3 | Red corporativa bloqueando SMTP | Usar red móvil o VPN |
| 4 | Puerto incorrecto | Usar 587 con TLS |
| 5 | Espacios en la contraseña | Copiar sin espacios |

---

**🕐 Última actualización:** 2026-01-20
