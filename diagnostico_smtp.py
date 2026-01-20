"""
Script de Diagnóstico SMTP para Bot de Telegram
Verifica la configuración y conectividad del servidor SMTP
"""

import smtplib
import ssl
import socket
import sys
from datetime import datetime

# COLORES PARA CONSOLA
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# CONFIGURACIONES PREDEFINIDAS
SMTP_CONFIGS = {
    '1': {
        'name': 'Gmail',
        'server': 'smtp.gmail.com',
        'port': 587,
        'tls': True
    },
    '2': {
        'name': 'Outlook/Hotmail',
        'server': 'smtp.office365.com',
        'port': 587,
        'tls': True
    },
    '3': {
        'name': 'Yahoo',
        'server': 'smtp.mail.yahoo.com',
        'port': 587,
        'tls': True
    },
    '4': {
        'name': 'SendGrid',
        'server': 'smtp.sendgrid.net',
        'port': 587,
        'tls': True
    },
    '5': {
        'name': 'Personalizado',
        'server': None,
        'port': None,
        'tls': None
    }
}

def test_dns_resolution(server):
    """Prueba 1: Resolución DNS"""
    print_info(f"Resolviendo DNS para {server}...")
    try:
        ip = socket.gethostbyname(server)
        print_success(f"DNS resuelto correctamente: {server} → {ip}")
        return True
    except socket.gaierror:
        print_error(f"No se pudo resolver el nombre del servidor: {server}")
        print_warning("Verifica que el nombre del servidor sea correcto")
        return False

def test_port_connectivity(server, port):
    """Prueba 2: Conectividad al Puerto"""
    print_info(f"Probando conectividad a {server}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((server, port))
        sock.close()
        
        if result == 0:
            print_success(f"Puerto {port} accesible")
            return True
        else:
            print_error(f"Puerto {port} no accesible (código: {result})")
            print_warning("Posibles causas:")
            print_warning("  • Firewall bloqueando el puerto")
            print_warning("  • Puerto incorrecto")
            print_warning("  • Servidor caído")
            return False
    except Exception as e:
        print_error(f"Error al probar conectividad: {str(e)}")
        return False

def test_smtp_connection(server, port, use_tls, timeout=30):
    """Prueba 3: Conexión SMTP Básica"""
    print_info(f"Estableciendo conexión SMTP...")
    try:
        with smtplib.SMTP(server, port, timeout=timeout) as smtp:
            smtp.set_debuglevel(0)
            response = smtp.noop()
            print_success(f"Conexión SMTP establecida (código: {response[0]})")
            
            if use_tls:
                print_info("Iniciando TLS/STARTTLS...")
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                print_success("TLS establecido correctamente")
            
            return True
    except smtplib.SMTPConnectError as e:
        print_error(f"Error de conexión SMTP: {str(e)}")
        print_warning("El servidor rechazó la conexión")
        return False
    except smtplib.SMTPServerDisconnected:
        print_error("El servidor cerró la conexión inesperadamente")
        print_warning("Posibles causas:")
        print_warning("  • Timeout muy corto")
        print_warning("  • Servidor sobrecargado")
        print_warning("  • Puerto incorrecto para el tipo de cifrado")
        return False
    except ssl.SSLError as e:
        print_error(f"Error SSL/TLS: {str(e)}")
        print_warning("Posibles causas:")
        print_warning("  • Certificado expirado o inválido")
        print_warning("  • Versión SSL incompatible")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {type(e).__name__}: {str(e)}")
        return False

def test_authentication(server, port, username, password, use_tls, timeout=30):
    """Prueba 4: Autenticación"""
    print_info(f"Probando autenticación como {username}...")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(server, port, timeout=timeout) as smtp:
            smtp.set_debuglevel(0)
            
            if use_tls:
                smtp.starttls(context=context)
            
            smtp.login(username, password)
            print_success("Autenticación exitosa")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print_error(f"Error de autenticación: {str(e)}")
        print_warning("Posibles causas:")
        print_warning("  • Usuario o contraseña incorrectos")
        print_warning("  • Para Gmail: necesitas usar contraseña de aplicación")
        print_warning("  • Cuenta bloqueada o suspendida")
        return False
    except Exception as e:
        print_error(f"Error durante autenticación: {type(e).__name__}: {str(e)}")
        return False

def main():
    print_header("DIAGNÓSTICO SMTP - Bot de Telegram")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Seleccionar proveedor
    print("Selecciona tu proveedor SMTP:")
    for key, config in SMTP_CONFIGS.items():
        print(f"  {key}. {config['name']}")
    
    choice = input("\nOpción (1-5): ").strip()
    
    if choice not in SMTP_CONFIGS:
        print_error("Opción inválida")
        sys.exit(1)
    
    config = SMTP_CONFIGS[choice].copy()
    
    # Configuración personalizada
    if choice == '5':
        config['server'] = input("Servidor SMTP: ").strip()
        config['port'] = int(input("Puerto (587/465/25): ").strip())
        use_tls = input("¿Usar TLS? (s/n): ").strip().lower()
        config['tls'] = use_tls == 's'
    
    # Credenciales
    print(f"\n{Colors.BOLD}Configuración seleccionada:{Colors.END}")
    print(f"  Proveedor: {config['name']}")
    print(f"  Servidor:  {config['server']}")
    print(f"  Puerto:    {config['port']}")
    print(f"  TLS:       {'Activado' if config['tls'] else 'Desactivado'}")
    
    username = input("\nUsuario (email completo): ").strip()
    password = input("Contraseña/Contraseña de aplicación: ").strip()
    
    # EJECUTAR PRUEBAS
    print_header("EJECUTANDO PRUEBAS")
    
    results = []
    
    # Prueba 1: DNS
    print(f"\n{Colors.BOLD}[1/4] Prueba de Resolución DNS{Colors.END}")
    results.append(("DNS", test_dns_resolution(config['server'])))
    
    # Prueba 2: Puerto
    print(f"\n{Colors.BOLD}[2/4] Prueba de Conectividad al Puerto{Colors.END}")
    results.append(("Puerto", test_port_connectivity(config['server'], config['port'])))
    
    # Prueba 3: Conexión SMTP
    print(f"\n{Colors.BOLD}[3/4] Prueba de Conexión SMTP{Colors.END}")
    results.append(("Conexión SMTP", test_smtp_connection(config['server'], config['port'], config['tls'])))
    
    # Prueba 4: Autenticación
    print(f"\n{Colors.BOLD}[4/4] Prueba de Autenticación{Colors.END}")
    results.append(("Autenticación", test_authentication(config['server'], config['port'], username, password, config['tls'])))
    
    # RESUMEN
    print_header("RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASÓ")
        else:
            print_error(f"{test_name}: FALLÓ")
    
    print(f"\n{Colors.BOLD}Resultado Final: {passed}/{total} pruebas pasadas{Colors.END}")
    
    if passed == total:
        print_success("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print_success("Tu configuración SMTP está correcta.")
        print_info("\nPuedes usar esta configuración en el bot:")
        print(f"  /setsmtp {config['server']} {config['port']} {username} {password} {username} \"Tu Nombre\"")
    else:
        print_error("\n❌ ALGUNAS PRUEBAS FALLARON")
        print_warning("Revisa los errores anteriores y consulta:")
        print_warning("  → TROUBLESHOOTING_CONEXION.md")
        print_warning("  → README_EMAIL_TRANZAS.md")
    
    # Recomendaciones específicas
    print_header("RECOMENDACIONES")
    
    if not results[0][1]:  # DNS falló
        print_warning("• Verifica que el nombre del servidor sea correcto")
        print_warning("• Prueba hacer ping al servidor")
    
    if not results[1][1]:  # Puerto falló
        print_warning("• Verifica tu firewall de Windows")
        print_warning("• Prueba desactivar temporalmente el antivirus")
        print_warning("• Si estás en red corporativa, contacta a IT")
    
    if not results[2][1]:  # Conexión SMTP falló
        print_warning("• Verifica que el puerto sea correcto:")
        print_warning("    - 587: requiere STARTTLS")
        print_warning("    - 465: requiere SSL directo")
        print_warning("• Intenta aumentar el timeout")
    
    if results[2][1] and not results[3][1]:  # Autenticación falló
        if 'gmail' in config['server'].lower():
            print_warning("• Para Gmail:")
            print_warning("    1. Activa verificación en 2 pasos")
            print_warning("    2. Genera contraseña de aplicación en:")
            print_warning("       https://myaccount.google.com/apppasswords")
            print_warning("    3. Usa esa contraseña de 16 caracteres")
        elif 'office365' in config['server'].lower():
            print_warning("• Para Outlook:")
            print_warning("    1. Genera contraseña de aplicación en:")
            print_warning("       https://account.microsoft.com/security")
        else:
            print_warning("• Verifica usuario y contraseña")
            print_warning("• Algunos proveedores requieren contraseña de aplicación")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Diagnóstico cancelado por el usuario{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nError fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
