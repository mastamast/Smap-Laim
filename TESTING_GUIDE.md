# 🧪 Guía de Pruebas - Bot Funcional

## ✅ Verificación de Implementación

### 1. Verificar Archivos Nuevos
```
✅ enhanced_wizard_handlers.py (432 líneas)
✅ enhanced_callback_handlers.py (384 líneas)
✅ utils.py (285 líneas)
✅ logger.py (103 líneas)
✅ FUNCTIONAL_IMPROVEMENTS.md (documentación)
✅ TESTING_GUIDE.md (este archivo)
```

### 2. Verificar Modificaciones
```
✅ bot.py - Nuevos conversation handlers registrados
✅ callback_router.py - Todos los callbacks enrutados
```

---

## 🔬 Plan de Pruebas

### Prueba 1: Wizard de Plantillas ✅

**Objetivo:** Verificar que el wizard de plantillas funciona end-to-end

**Pasos:**
1. Enviar `/start`
2. Click en `📧 Email Marketing`
3. Click en `➕ Crear Plantilla` (o `wizard_template`)
4. Seguir los 4 pasos:
   - Paso 1: Nombre → `Prueba Newsletter`
   - Paso 2: Asunto → `¡Hola {name}, novedades del mes!`
   - Paso 3: Cuerpo → `<h1>Hola {name}</h1><p>Tenemos noticias para ti...</p>`
   - Paso 4: Confirmar

**Resultado Esperado:**
- ✅ Wizard completa sin errores
- ✅ Plantilla se crea en BD
- ✅ Mensaje de confirmación aparece
- ✅ Botones de siguiente acción disponibles

**Validaciones a Verificar:**
- Nombre mínimo 3 caracteres
- Detección de duplicados
- Asunto mínimo 5 caracteres
- Cuerpo mínimo 10 caracteres
- Vista previa truncada correctamente

---

### Prueba 2: Wizard de Campañas ✅

**Pre-requisitos:**
- SMTP configurado
- Al menos 1 lista con contactos
- Al menos 1 plantilla

**Pasos:**
1. Click en `🚀 Enviar Campaña`
2. Verificar prerequisitos
3. Seleccionar lista
4. Seleccionar plantilla
5. Nombre de campaña → `Campaña de Prueba`
6. Confirmar
7. Esperar envío

**Resultado Esperado:**
- ✅ Verificación de prerequisitos funciona
- ✅ Listas y plantillas se muestran correctamente
- ✅ Confirmación muestra resumen completo
- ✅ Envío ejecuta correctamente
- ✅ Estadísticas finales se muestran

**Casos de Error a Probar:**
- Sin SMTP → Redirige a configuración
- Sin listas → Redirige a crear lista
- Sin plantillas → Redirige a crear plantilla

---

### Prueba 3: Test de Conexión SMTP 🧪

**Pre-requisitos:**
- SMTP configurado (puede estar mal configurado para probar error)

**Pasos:**
1. `/start` → Email Marketing → Config Email
2. Click en `🧪 Probar Conexión`
3. Esperar resultado

**Resultado Esperado (Conexión OK):**
- ✅ Mensaje "Probando..."
- ✅ Conexión exitosa
- ✅ Muestra servidor y puerto
- ✅ Botón para enviar campaña

**Resultado Esperado (Error de Auth):**
- ✅ Mensaje específico de autenticación
- ✅ Ayuda para Gmail (contraseña de aplicación)
- ✅ Link a documentación
- ✅ Botón para reconfigurar

**Resultado Esperado (Error de Conexión):**
- ✅ Mensaje de error de servidor
- ✅ Muestra servidor/puerto intentados
- ✅ Sugerencias de solución

---

### Prueba 4: Vistas Detalladas 👁️

**a) Detalle de Plantilla:**
1. Ver Plantillas
2. Click en cualquier plantilla

**Verificar:**
- ✅ Nombre e ID
- ✅ Asunto completo
- ✅ Vista previa del cuerpo (max 300 chars)
- ✅ Fecha de creación
- ✅ Botones: Usar en campaña, Eliminar (admin)

**b) Detalle de Campaña:**
1. Ver Campañas
2. Click en cualquier campaña

**Verificar:**
- ✅ Nombre y estado con emoji
- ✅ Plantilla y lista usadas
- ✅ Estadísticas (enviados/total)
- ✅ Tasa de éxito calculada
- ✅ Fechas (creación, inicio, fin)

---

### Prueba 5: Gestión de Miembros 👥

**Pasos:**
1. `/start` → Usuarios (solo admin)
2. Click en `📋 Ver Todos los Miembros`
3. Click en cualquier miembro

**Verificar:**
- ✅ Lista con botones interactivos
- ✅ Máximo 10 miembros mostrados
- ✅ Click muestra detalle completo
- ✅ Información: nombre, ID, username, fecha

---

### Prueba 6: Ayuda Contextual ❓

**Temas a Probar:**
1. `/start` → Ayuda
2. Click en cada tema:
   - Email Marketing
   - Gestión de Listas
   - Crear Plantillas
   - Enviar Campañas
   - FAQ

**Verificar para cada tema:**
- ✅ Contenido relevante y claro
- ✅ Sin jerga técnica excesiva
- ✅ Pasos numerados cuando aplica
- ✅ Botón volver a ayuda

---

### Prueba 7: Logs de Actividad 📋

**Pasos:**
1. Realizar varias acciones (agregar/eliminar miembros)
2. `/start` → Usuarios → Ver Actividad

**Verificar:**
- ✅ Últimas 15 actividades
- ✅ Timestamp formateado
- ✅ Usuario y quien lo realizó
- ✅ Emojis correctos (➕/➖)
- ✅ Botón actualizar funciona

---

### Prueba 8: Validaciones 🛡️

**Email Validation:**
```python
# Probar en add_recipient
emails_validos = [
    "test@example.com",
    "user.name@domain.co.uk",
    "a+b@test.com"
]

emails_invalidos = [
    "invalido",
    "@example.com",
    "test@",
    "test..test@example.com",
    "test@example"
]
```

**Verificar:**
- ✅ Emails válidos aceptados
- ✅ Emails inválidos rechazados con mensaje claro

**SMTP Validation:**
- ✅ Servidor vacío → Rechazado
- ✅ Puerto fuera de rango → Rechazado
- ✅ Contraseña corta → Rechazado

---

### Prueba 9: Logging System 📝

**Verificar archivo bot.log:**
1. Ejecutar comandos
2. Revisar `bot.log`

**Debe contener:**
```
2026-01-20 14:30:15 - TelegramBot - INFO - [User 123] Comando ejecutado: /start
2026-01-20 14:32:20 - TelegramBot - INFO - [User 123] Campaña 1: 95/100 enviados (95.0%), 5 fallidos
2026-01-20 14:33:10 - TelegramBot - INFO - Test SMTP exitoso para servidor smtp.gmail.com
```

**Verificar:**
- ✅ Formato correcto
- ✅ Timestamp
- ✅ User ID cuando aplica
- ✅ Eventos importantes registrados

---

### Prueba 10: Manejo de Errores ⚠️

**Escenarios a Probar:**

**a) Wizard cancelado:**
1. Iniciar cualquier wizard
2. Click en Cancelar
- ✅ Mensaje de cancelación
- ✅ Datos temporales limpiados
- ✅ Vuelve al menú

**b) Timeout de SMTP:**
1. Configurar servidor inaccesible
2. Probar conexión
- ✅ Timeout después de 10s
- ✅ Mensaje de error claro

**c) Campaña sin destinatarios:**
1. Intentar enviar a lista vacía
- ✅ Validación previa
- ✅ No permite continuar

**d) HTML malicioso:**
```html
<script>alert('XSS')</script>
<p onclick="evil()">Click</p>
```
- ✅ Scripts eliminados
- ✅ Event handlers eliminados
- ✅ Solo tags seguros

---

## 📊 Checklist de Funcionalidad Completa

### Wizards
- [ ] Wizard SMTP (original) - 5 pasos
- [ ] Wizard Lista (original) - 3 pasos
- [ ] Wizard Plantilla (nuevo) - 4 pasos ⭐
- [ ] Wizard Campaña (nuevo) - 4 pasos ⭐

### Callbacks Críticos
- [ ] `test_smtp` - Test conexión ⭐
- [ ] `template_detail_{id}` - Detalle plantilla ⭐
- [ ] `campaign_detail_{id}` - Detalle campaña ⭐
- [ ] `list_all_members` - Lista miembros ⭐
- [ ] `member_info_{id}` - Info miembro ⭐
- [ ] `view_logs` - Logs actividad ⭐
- [ ] `help_*` - Ayuda contextual ⭐

### Validaciones
- [ ] Email validation
- [ ] SMTP config validation
- [ ] HTML sanitization
- [ ] Input length checks
- [ ] Duplicate detection

### Logging
- [ ] Console logging
- [ ] File logging (bot.log)
- [ ] Command logging
- [ ] Campaign logging
- [ ] Error logging

### Error Handling
- [ ] SMTP errors específicos
- [ ] Timeouts configurados
- [ ] Mensajes accionables
- [ ] Fallbacks en wizards

---

## 🚀 Comandos de Prueba Rápida

### Setup Inicial
```bash
# Reiniciar bot (si está corriendo)
Ctrl+C
python bot.py

# Verificar logs
Get-Content bot.log -Tail 20
```

### Prueba Secuencial Completa
```
1. /start
2. Email Marketing → Configurar Email → [Wizard SMTP]
3. Email Marketing → Crear Lista → [Wizard Lista]
4. Email Marketing → Crear Plantilla → [Wizard Plantilla] ⭐
5. Email Marketing → Enviar Campaña → [Wizard Campaña] ⭐
6. Config Email → Probar Conexión ⭐
7. Ver Plantillas → Click en plantilla ⭐
8. Ver Campañas → Click en campaña ⭐
9. Ayuda → Email Marketing ⭐
10. Usuarios → Ver Todos → Click en miembro ⭐
```

---

## 🐛 Problemas Conocidos y Soluciones

### Problema: "Module not found"
**Solución:** Reiniciar el bot para cargar nuevos módulos

### Problema: Callback "en desarrollo"
**Solución:** Verificar que callback_router.py tenga los imports

### Problema: Wizard no continúa
**Solución:** Verificar que ConversationHandler está registrado en bot.py

### Problema: Logs no se crean
**Solución:** Verificar permisos de escritura en directorio

---

## ✅ Criterios de Aceptación

El bot pasa las pruebas si:

1. ✅ Todos los wizards se completan sin errores
2. ✅ Todas las validaciones funcionan correctamente
3. ✅ Test SMTP detecta errores específicamente
4. ✅ Vistas detalladas muestran información completa
5. ✅ Ayuda contextual está disponible y es útil
6. ✅ Logs se generan correctamente
7. ✅ Errores muestran mensajes accionables
8. ✅ No hay callbacks "en desarrollo" críticos
9. ✅ HTML malicioso es sanitizado
10. ✅ Flujo end-to-end funciona sin intervención manual

---

## 📝 Reporte de Pruebas

Después de probar, documentar:

```markdown
## Pruebas Ejecutadas

**Fecha:** [Fecha]
**Versión:** 2.0

### Resultados:

| Funcionalidad | Estado | Notas |
|--------------|--------|-------|
| Wizard Plantilla | ✅/❌ | |
| Wizard Campaña | ✅/❌ | |
| Test SMTP | ✅/❌ | |
| Vistas Detalladas | ✅/❌ | |
| Validaciones | ✅/❌ | |
| Logging | ✅/❌ | |

### Bugs Encontrados:
1. [Descripción]
2. [Descripción]

### Mejoras Sugeridas:
1. [Sugerencia]
2. [Sugerencia]
```

---

**Estado:** Listo para Pruebas
**Última Actualización:** 2026-01-20
