"""
CloudflareBypass - Paquete profesional para bypass de Cloudflare
================================================================

Un paquete Python completo y robusto para bypasear protecciones de Cloudflare
sin depender de servicios externos pagos, con soporte opcional para APIs.

Características:
- 🆓 100% gratuito con técnicas propias
- 🔧 Soporte opcional para servicios externos (2captcha, anticaptcha, etc.)
- 🧠 Simulación avanzada de comportamiento humano
- 🎭 Spoofing de fingerprints
- ⚡ Múltiples técnicas de bypass
- 🔄 Sistema robusto con fallbacks

Uso básico:
    from cloudflare_bypass import CloudflareBypasser
    
    with CloudflareBypasser() as bypasser:
        success = bypasser.bypass_url("https://example.com")

Uso con API key:
    from cloudflare_bypass import CloudflareBypasser
    
    with CloudflareBypasser(captcha_service="2captcha", api_key="tu_api_key") as bypasser:
        success = bypasser.bypass_url("https://example.com")

Autor: CloudflareBypass Team
Licencia: MIT
Versión: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "CloudflareBypass Team"
__email__ = "support@cloudflarebypass.com"
__license__ = "MIT"

# Main imports
from .core import CloudflareBypasser
from .config import BypassConfig, BypassMode, CaptchaService
from .exceptions import (
    CloudflareBypassError,
    DriverError,
    CaptchaError,
    ConfigurationError,
    TimeoutError as BypassTimeoutError
)

# Predefined configurations  
STEALTH_CONFIG = BypassConfig(
    mode=BypassMode.STEALTH,
    headless=True,
    simulate_human=True,
    enable_fingerprint_spoofing=True,
    timeout=120,
    max_retries=5
)

FAST_CONFIG = BypassConfig(
    mode=BypassMode.MINIMAL,
    headless=True,
    simulate_human=False,
    enable_fingerprint_spoofing=False,
    timeout=30,
    max_retries=2
)

__all__ = [
    'CloudflareBypasser',
    'BypassConfig',
    'BypassMode', 
    'CaptchaService',
    'CloudflareBypassError',
    'DriverError',
    'CaptchaError',
    'ConfigurationError',
    'BypassTimeoutError',
    'STEALTH_CONFIG',
    'FAST_CONFIG'
]
