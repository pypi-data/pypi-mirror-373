"""
Configuración para CloudflareBypass
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum

class CaptchaService(Enum):
    """Servicios de captcha soportados"""
    NONE = "none"
    TWOCAPTCHA = "2captcha"
    ANTICAPTCHA = "anticaptcha"
    CAPMONSTER = "capmonster"
    DEATHBYCAPTCHA = "deathbycaptcha"

class BypassMode(Enum):
    """Modos de bypass"""
    AUTO = "auto"           # Detecta automáticamente el mejor método
    STEALTH = "stealth"     # Modo sigiloso con técnicas avanzadas
    AGGRESSIVE = "aggressive"  # Modo agresivo para casos difíciles
    MINIMAL = "minimal"     # Modo mínimo para casos simples

@dataclass
class BypassConfig:
    """Configuración para CloudflareBypass"""
    
    # Configuración de captcha
    captcha_service: CaptchaService = CaptchaService.NONE
    api_key: Optional[str] = None
    captcha_timeout: int = 120
    
    # Configuración del navegador
    headless: bool = False
    user_agent: Optional[str] = None
    window_size: tuple = (1366, 768)
    
    # Configuración de bypass
    mode: BypassMode = BypassMode.AUTO
    max_retries: int = 3
    retry_delay: int = 5
    timeout: int = 60
    
    # Configuración de comportamiento
    simulate_human: bool = True
    enable_stealth: bool = True
    enable_fingerprint_spoofing: bool = True
    
    # Configuración de proxy
    proxy: Optional[str] = None
    proxy_auth: Optional[Dict[str, str]] = None
    
    # Configuración avanzada
    chrome_version: Optional[int] = None
    custom_chrome_options: Optional[List[str]] = None
    debug: bool = False
    
    # URLs de servicios
    service_urls: Dict[str, Dict[str, str]] = None
    
    def __post_init__(self):
        """Inicializar URLs de servicios si no se proporcionaron"""
        if self.service_urls is None:
            self.service_urls = {
                "2captcha": {
                    "submit_url": "http://2captcha.com/in.php",
                    "result_url": "http://2captcha.com/res.php"
                },
                "anticaptcha": {
                    "submit_url": "https://api.anti-captcha.com/createTask",
                    "result_url": "https://api.anti-captcha.com/getTaskResult"
                },
                "capmonster": {
                    "submit_url": "https://api.capmonster.cloud/createTask",
                    "result_url": "https://api.capmonster.cloud/getTaskResult"
                },
                "deathbycaptcha": {
                    "submit_url": "http://api.dbcapi.me/api/captcha",
                    "result_url": "http://api.dbcapi.me/api/captcha/{captcha_id}"
                }
            }
    
    def validate(self) -> bool:
        """Valida la configuración"""
        if self.captcha_service != CaptchaService.NONE and not self.api_key:
            raise ValueError("API key requerida cuando se especifica un servicio de captcha")
        
        if self.captcha_timeout < 30:
            raise ValueError("Timeout de captcha debe ser al menos 30 segundos")
        
        if self.max_retries < 1:
            raise ValueError("max_retries debe ser al menos 1")
        
        return True

# Configuraciones predefinidas para casos comunes
DEFAULT_CONFIG = BypassConfig()

STEALTH_CONFIG = BypassConfig(
    mode=BypassMode.STEALTH,
    headless=True,
    simulate_human=True,
    enable_stealth=True,
    enable_fingerprint_spoofing=True,
    timeout=90
)

FAST_CONFIG = BypassConfig(
    mode=BypassMode.MINIMAL,
    headless=True,
    simulate_human=False,
    enable_stealth=False,
    enable_fingerprint_spoofing=False,
    timeout=30
)

AGGRESSIVE_CONFIG = BypassConfig(
    mode=BypassMode.AGGRESSIVE,
    headless=False,
    simulate_human=True,
    enable_stealth=True,
    enable_fingerprint_spoofing=True,
    max_retries=5,
    timeout=120
)
