"""
Resolución de captcha usando servicios externos
"""

import requests
import time
import json
from typing import Optional, Dict, Any

from .exceptions import CaptchaError


class CaptchaResolver:
    """Resuelve captchas usando servicios externos"""
    
    def __init__(self, service: str, api_key: str, service_urls: Dict[str, Dict[str, str]]):
        self.service = service.lower()
        self.api_key = api_key
        self.service_urls = service_urls
        
        if self.service not in self.service_urls:
            raise CaptchaError(f"Servicio no soportado: {service}")
    
    def solve_turnstile(self, sitekey: str, page_url: str, timeout: int = 120) -> Optional[str]:
        """Resuelve captcha Turnstile"""
        if self.service == "2captcha":
            return self._solve_with_2captcha(sitekey, page_url, timeout)
        elif self.service == "anticaptcha":
            return self._solve_with_anticaptcha(sitekey, page_url, timeout)
        elif self.service == "capmonster":
            return self._solve_with_capmonster(sitekey, page_url, timeout)
        elif self.service == "deathbycaptcha":
            return self._solve_with_deathbycaptcha(sitekey, page_url, timeout)
        else:
            raise CaptchaError(f"Método no implementado para {self.service}")
    
    def _solve_with_2captcha(self, sitekey: str, page_url: str, timeout: int) -> Optional[str]:
        """Resuelve usando 2captcha"""
        try:
            # Enviar captcha
            submit_url = self.service_urls["2captcha"]["submit_url"]
            submit_data = {
                'key': self.api_key,
                'method': 'turnstile',
                'sitekey': sitekey,
                'pageurl': page_url,
                'json': 1
            }
            
            response = requests.post(submit_url, data=submit_data, timeout=30)
            result = response.json()
            
            if result.get('status') != 1:
                raise CaptchaError(f"Error enviando a 2captcha: {result}")
            
            captcha_id = result['request']
            
            # Esperar resultado
            result_url = self.service_urls["2captcha"]["result_url"]
            
            for _ in range(timeout // 5):
                time.sleep(5)
                
                result_data = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
                
                response = requests.get(result_url, params=result_data, timeout=30)
                result = response.json()
                
                if result.get('status') == 1:
                    return result['request']
                elif result.get('request') != 'CAPCHA_NOT_READY':
                    raise CaptchaError(f"Error obteniendo resultado: {result}")
            
            raise CaptchaError("Timeout esperando resultado de 2captcha")
            
        except requests.RequestException as e:
            raise CaptchaError(f"Error de red con 2captcha: {e}")
    
    def _solve_with_anticaptcha(self, sitekey: str, page_url: str, timeout: int) -> Optional[str]:
        """Resuelve usando anticaptcha"""
        try:
            # Crear tarea
            create_url = self.service_urls["anticaptcha"]["submit_url"]
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "TurnstileTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": sitekey
                }
            }
            
            response = requests.post(create_url, json=task_data, timeout=30)
            result = response.json()
            
            if result.get('errorId') != 0:
                raise CaptchaError(f"Error creando tarea en anticaptcha: {result}")
            
            task_id = result['taskId']
            
            # Esperar resultado
            result_url = self.service_urls["anticaptcha"]["result_url"]
            
            for _ in range(timeout // 5):
                time.sleep(5)
                
                result_data = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                response = requests.post(result_url, json=result_data, timeout=30)
                result = response.json()
                
                if result.get('status') == 'ready':
                    return result['solution']['token']
                elif result.get('status') != 'processing':
                    raise CaptchaError(f"Error obteniendo resultado: {result}")
            
            raise CaptchaError("Timeout esperando resultado de anticaptcha")
            
        except requests.RequestException as e:
            raise CaptchaError(f"Error de red con anticaptcha: {e}")
    
    def _solve_with_capmonster(self, sitekey: str, page_url: str, timeout: int) -> Optional[str]:
        """Resuelve usando capmonster"""
        try:
            # Crear tarea
            create_url = self.service_urls["capmonster"]["submit_url"]
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "TurnstileTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": sitekey
                }
            }
            
            response = requests.post(create_url, json=task_data, timeout=30)
            result = response.json()
            
            if result.get('errorId') != 0:
                raise CaptchaError(f"Error creando tarea en capmonster: {result}")
            
            task_id = result['taskId']
            
            # Esperar resultado
            result_url = self.service_urls["capmonster"]["result_url"]
            
            for _ in range(timeout // 5):
                time.sleep(5)
                
                result_data = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                response = requests.post(result_url, json=result_data, timeout=30)
                result = response.json()
                
                if result.get('status') == 'ready':
                    return result['solution']['token']
                elif result.get('status') != 'processing':
                    raise CaptchaError(f"Error obteniendo resultado: {result}")
            
            raise CaptchaError("Timeout esperando resultado de capmonster")
            
        except requests.RequestException as e:
            raise CaptchaError(f"Error de red con capmonster: {e}")
    
    def _solve_with_deathbycaptcha(self, sitekey: str, page_url: str, timeout: int) -> Optional[str]:
        """Resuelve usando deathbycaptcha"""
        try:
            # Implementación básica para deathbycaptcha
            submit_url = self.service_urls["deathbycaptcha"]["submit_url"]
            
            # DeathByCaptcha tiene API diferente, implementar según su documentación
            # Esta es una implementación de ejemplo
            submit_data = {
                'username': self.api_key.split(':')[0] if ':' in self.api_key else self.api_key,
                'password': self.api_key.split(':')[1] if ':' in self.api_key else '',
                'type': 'turnstile',
                'turnstile_params': json.dumps({
                    'sitekey': sitekey,
                    'pageurl': page_url
                })
            }
            
            response = requests.post(submit_url, data=submit_data, timeout=30)
            result = response.json()
            
            if not result.get('captcha'):
                raise CaptchaError(f"Error enviando a deathbycaptcha: {result}")
            
            captcha_id = result['captcha']
            
            # Esperar resultado
            for _ in range(timeout // 5):
                time.sleep(5)
                
                result_url = self.service_urls["deathbycaptcha"]["result_url"].format(captcha_id=captcha_id)
                response = requests.get(result_url, timeout=30)
                result = response.json()
                
                if result.get('is_correct') and result.get('text'):
                    return result['text']
            
            raise CaptchaError("Timeout esperando resultado de deathbycaptcha")
            
        except requests.RequestException as e:
            raise CaptchaError(f"Error de red con deathbycaptcha: {e}")
