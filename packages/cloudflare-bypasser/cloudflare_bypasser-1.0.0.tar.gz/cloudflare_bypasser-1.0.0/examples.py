#!/usr/bin/env python3
"""
Ejemplos de uso del paquete CloudflareBypass
"""

def example_basic_usage():
    """Ejemplo básico de uso gratuito"""
    print("🚀 Ejemplo 1: Uso básico gratuito")
    print("=" * 40)
    
    from cloudflare_bypass import CloudflareBypasser
    
    # Uso simple
    with CloudflareBypasser() as bypasser:
        url = "https://httpbin.org/status/200"  # URL de prueba
        print(f"Procesando: {url}")
        
        success = bypasser.bypass_url(url)
        if success:
            print("✅ Bypass exitoso!")
            print(f"Título: {bypasser.get_title()}")
            print(f"URL: {bypasser.get_current_url()}")
        else:
            print("❌ Bypass falló")


def example_with_api_key():
    """Ejemplo con API key"""
    print("\n🔑 Ejemplo 2: Con API key")
    print("=" * 40)
    
    from cloudflare_bypass import CloudflareBypasser
    
    # IMPORTANTE: Reemplaza con tu API key real
    api_key = "tu_api_key_aqui"
    
    if api_key == "tu_api_key_aqui":
        print("⚠️  Configura tu API key real para este ejemplo")
        return
    
    bypasser = CloudflareBypasser(
        captcha_service="2captcha",
        api_key=api_key
    )
    
    with bypasser:
        url = "https://example.com"
        print(f"Procesando con API: {url}")
        
        success = bypasser.bypass_url(url)
        if success:
            print("✅ Bypass con API exitoso!")
            # Hacer algo con la página
            page_source = bypasser.get_page_source()
            print(f"Tamaño del HTML: {len(page_source)} caracteres")


def example_advanced_config():
    """Ejemplo con configuración avanzada"""
    print("\n⚙️ Ejemplo 3: Configuración avanzada")
    print("=" * 40)
    
    from cloudflare_bypass import CloudflareBypasser, BypassConfig, BypassMode
    
    # Configuración personalizada
    config = BypassConfig(
        mode=BypassMode.STEALTH,
        headless=False,  # Mostrar navegador para ver el proceso
        simulate_human=True,
        enable_fingerprint_spoofing=True,
        timeout=90,
        max_retries=3,
        window_size=(1920, 1080),
        user_agent="Mozilla/5.0 (Custom Agent for Testing)"
    )
    
    with CloudflareBypasser(config=config) as bypasser:
        url = "https://httpbin.org/user-agent"
        print(f"Procesando con config avanzada: {url}")
        
        success = bypasser.bypass_url(url)
        if success:
            print("✅ Config avanzada funcionó!")
            print(f"User agent detectado en la página")


def example_multiple_urls():
    """Ejemplo procesando múltiples URLs"""
    print("\n🔄 Ejemplo 4: Múltiples URLs")
    print("=" * 40)
    
    from cloudflare_bypass import CloudflareBypasser
    
    urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/html",
        "https://example.com"
    ]
    
    with CloudflareBypasser() as bypasser:
        for i, url in enumerate(urls, 1):
            print(f"📄 Procesando {i}/{len(urls)}: {url}")
            
            success = bypasser.bypass_url(url)
            if success:
                title = bypasser.get_title()
                print(f"   ✅ Éxito - Título: {title[:50]}...")
            else:
                print(f"   ❌ Falló")


def example_error_handling():
    """Ejemplo con manejo de errores"""
    print("\n🚨 Ejemplo 5: Manejo de errores")
    print("=" * 40)
    
    from cloudflare_bypass import (
        CloudflareBypasser, 
        CloudflareBypassError, 
        DriverError,
        CaptchaError
    )
    
    try:
        with CloudflareBypasser() as bypasser:
            # Intentar con URL inválida para provocar error
            success = bypasser.bypass_url("invalid-url")
            
            if success:
                # Buscar elemento que no existe
                element = bypasser.find_element("css selector", ".elemento-inexistente")
                
    except DriverError as e:
        print(f"🚗 Error del driver: {e}")
    except CaptchaError as e:
        print(f"🧩 Error de captcha: {e}")
    except CloudflareBypassError as e:
        print(f"☁️ Error de bypass: {e}")
    except Exception as e:
        print(f"💥 Error general: {e}")


def example_predefined_configs():
    """Ejemplo con configuraciones predefinidas"""
    print("\n📋 Ejemplo 6: Configuraciones predefinidas")
    print("=" * 40)
    
    from cloudflare_bypass import CloudflareBypasser, STEALTH_CONFIG, FAST_CONFIG
    
    # Modo sigiloso
    print("🥷 Probando modo STEALTH...")
    with CloudflareBypasser(config=STEALTH_CONFIG) as bypasser:
        success = bypasser.bypass_url("https://httpbin.org/status/200")
        print(f"   Resultado: {'✅ Éxito' if success else '❌ Falló'}")
    
    # Modo rápido
    print("⚡ Probando modo FAST...")
    with CloudflareBypasser(config=FAST_CONFIG) as bypasser:
        success = bypasser.bypass_url("https://httpbin.org/status/200")
        print(f"   Resultado: {'✅ Éxito' if success else '❌ Falló'}")


def example_real_world_scenario():
    """Ejemplo de escenario real"""
    print("\n🌍 Ejemplo 7: Escenario real")
    print("=" * 40)
    
    from cloudflare_bypass import CloudflareBypasser, BypassConfig, BypassMode
    
    # Configuración para sitio real
    config = BypassConfig(
        mode=BypassMode.AUTO,
        headless=True,
        simulate_human=True,
        enable_fingerprint_spoofing=True,
        timeout=120,  # Más tiempo para sitios complejos
        max_retries=5
    )
    
    try:
        with CloudflareBypasser(config=config) as bypasser:
            # Usar un sitio real que sabemos que funciona
            url = "https://example.com"
            print(f"🎯 Procesando sitio real: {url}")
            
            success = bypasser.bypass_url(url)
            
            if success:
                print("✅ Sitio real procesado exitosamente!")
                
                # Hacer algo útil con la página
                title = bypasser.get_title()
                current_url = bypasser.get_current_url()
                
                print(f"📄 Título: {title}")
                print(f"🌐 URL final: {current_url}")
                
                # Buscar elementos específicos
                try:
                    # Buscar el elemento h1
                    h1_element = bypasser.find_element("tag name", "h1")
                    if h1_element:
                        print(f"📝 H1 encontrado: {h1_element.text}")
                except:
                    print("ℹ️  No se encontró elemento H1")
                
            else:
                print("❌ No se pudo procesar el sitio")
                
    except Exception as e:
        print(f"💥 Error en escenario real: {e}")


def main():
    """Ejecutar todos los ejemplos"""
    print("🚀 CloudflareBypass - Ejemplos de Uso")
    print("=" * 50)
    print("ℹ️  Estos ejemplos muestran diferentes formas de usar el paquete")
    print("ℹ️  Algunos requieren configuración adicional (API keys)")
    print()
    
    try:
        example_basic_usage()
        example_with_api_key()
        example_advanced_config()
        example_multiple_urls()
        example_error_handling()
        example_predefined_configs()
        example_real_world_scenario()
        
        print("\n🎉 Todos los ejemplos completados!")
        print("📚 Consulta el README.md para más información")
        
    except KeyboardInterrupt:
        print("\n⏹️  Ejemplos interrumpidos por el usuario")
    except Exception as e:
        print(f"\n💥 Error ejecutando ejemplos: {e}")


if __name__ == "__main__":
    main()
