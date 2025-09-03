#!/usr/bin/env python3
"""
CLI interface for CloudflareBypass
"""
import argparse
import json
import sys
from typing import Optional, Dict, Any

from .core import CloudflareBypasser
from .config import BypassConfig, BypassMode, CaptchaService


def create_config_from_args(args: argparse.Namespace) -> BypassConfig:
    """Create BypassConfig from command line arguments."""
    return BypassConfig(
        mode=BypassMode(args.mode) if args.mode else BypassMode.AUTO,
        headless=args.headless,
        simulate_human=args.simulate_human,
        enable_fingerprint_spoofing=args.fingerprint_spoofing,
        captcha_service=CaptchaService(args.captcha_service) if args.captcha_service else None,
        api_key=args.api_key,
        timeout=args.timeout,
        max_retries=args.max_retries,
        proxy=args.proxy,
        proxy_auth=json.loads(args.proxy_auth) if args.proxy_auth else None,
        user_agent=args.user_agent,
        window_size=tuple(map(int, args.window_size.split('x'))) if args.window_size else None
    )


def bypass_command(args: argparse.Namespace) -> int:
    """Execute bypass command."""
    config = create_config_from_args(args)
    
    try:
        with CloudflareBypasser(config=config) as bypasser:
            print(f"🚀 Iniciando bypass para: {args.url}")
            
            success = bypasser.bypass_url(args.url)
            
            if success:
                print("✅ Bypass exitoso!")
                print(f"📄 Título: {bypasser.get_title()}")
                print(f"🌐 URL final: {bypasser.get_current_url()}")
                
                if args.output:
                    print(f"💾 Guardando contenido en: {args.output}")
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(bypasser.get_page_source())
                
                if args.screenshot:
                    print(f"📸 Guardando screenshot en: {args.screenshot}")
                    bypasser.save_screenshot(args.screenshot)
                
                return 0
            else:
                print("❌ Bypass falló")
                return 1
                
    except Exception as e:
        print(f"💥 Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def test_command(args: argparse.Namespace) -> int:
    """Execute test command."""
    config = create_config_from_args(args)
    
    test_urls = [
        "https://httpbin.org/status/200",
        "https://example.com",
        args.url if args.url else None
    ]
    
    test_urls = [url for url in test_urls if url]
    
    try:
        with CloudflareBypasser(config=config) as bypasser:
            for i, url in enumerate(test_urls, 1):
                print(f"🧪 Test {i}/{len(test_urls)}: {url}")
                
                success = bypasser.bypass_url(url)
                
                if success:
                    print(f"✅ Test {i} exitoso")
                else:
                    print(f"❌ Test {i} falló")
                    
        print("🏁 Tests completados")
        return 0
        
    except Exception as e:
        print(f"💥 Error en tests: {e}")
        return 1


def info_command(args: argparse.Namespace) -> int:
    """Show package information."""
    from . import __version__
    
    info = {
        "version": __version__,
        "author": "CloudflareBypass Team",
        "description": "Paquete profesional para bypass de Cloudflare",
        "supported_modes": [mode.value for mode in BypassMode],
        "supported_services": [service.value for service in CaptchaService],
        "features": [
            "Bypass gratuito sin servicios externos",
            "Soporte para APIs de captcha",
            "Simulación de comportamiento humano",
            "Spoofing de fingerprints",
            "Múltiples estrategias de bypass"
        ]
    }
    
    print("📦 CloudflareBypass - Información del Paquete")
    print("=" * 50)
    for key, value in info.items():
        if isinstance(value, list):
            print(f"{key.title()}:")
            for item in value:
                print(f"  • {item}")
        else:
            print(f"{key.title()}: {value}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="cloudflare-bypass",
        description="🚀 CloudflareBypass - Paquete profesional para bypass de Cloudflare"
    )
    
    # Global arguments
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--version", action="version", version="cloudflare-bypass 1.0.0")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Bypass command
    bypass_parser = subparsers.add_parser("bypass", help="Ejecutar bypass en una URL")
    bypass_parser.add_argument("url", help="URL a procesar")
    bypass_parser.add_argument("--output", "-o", help="Archivo donde guardar el HTML")
    bypass_parser.add_argument("--screenshot", "-s", help="Archivo donde guardar screenshot")
    
    # Test command  
    test_parser = subparsers.add_parser("test", help="Ejecutar tests del sistema")
    test_parser.add_argument("--url", help="URL adicional para testear")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Mostrar información del paquete")
    
    # Common configuration arguments for bypass and test
    for subparser in [bypass_parser, test_parser]:
        # Mode options
        subparser.add_argument("--mode", choices=[m.value for m in BypassMode], 
                             help="Modo de bypass")
        subparser.add_argument("--headless", action="store_true", 
                             help="Ejecutar en modo headless")
        subparser.add_argument("--simulate-human", action="store_true", default=True,
                             help="Simular comportamiento humano")
        subparser.add_argument("--fingerprint-spoofing", action="store_true", default=True,
                             help="Habilitar spoofing de fingerprints")
        
        # Captcha options
        subparser.add_argument("--captcha-service", 
                             choices=[s.value for s in CaptchaService],
                             help="Servicio de captcha a usar")
        subparser.add_argument("--api-key", help="API key para servicio de captcha")
        
        # Performance options
        subparser.add_argument("--timeout", type=int, default=60, 
                             help="Timeout en segundos")
        subparser.add_argument("--max-retries", type=int, default=3,
                             help="Número máximo de reintentos")
        
        # Network options
        subparser.add_argument("--proxy", help="Proxy a usar (http://host:port)")
        subparser.add_argument("--proxy-auth", help='Auth proxy JSON {"username":"user","password":"pass"}')
        subparser.add_argument("--user-agent", help="User agent personalizado")
        subparser.add_argument("--window-size", help="Tamaño ventana (ej: 1920x1080)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == "bypass":
        return bypass_command(args)
    elif args.command == "test":
        return test_command(args)
    elif args.command == "info":
        return info_command(args)
    else:
        print(f"❌ Comando desconocido: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
