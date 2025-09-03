"""
Excepciones personalizadas para CloudflareBypass
"""

class CloudflareBypassError(Exception):
    """Excepción base para errores de CloudflareBypass"""
    pass

class DriverError(CloudflareBypassError):
    """Error relacionado con el driver del navegador"""
    pass

class CaptchaError(CloudflareBypassError):
    """Error relacionado con resolución de captcha"""
    pass

class TimeoutError(CloudflareBypassError):
    """Error de timeout durante el bypass"""
    pass

class ConfigurationError(CloudflareBypassError):
    """Error de configuración"""
    pass

class NetworkError(CloudflareBypassError):
    """Error de red durante las operaciones"""
    pass
