"""
Módulo principal de CloudflareBypass
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import requests
import json
import hashlib
import secrets
import re
from typing import Optional, Dict, Any, List, Tuple

from .config import BypassConfig, CaptchaService, BypassMode
from .exceptions import DriverError, CaptchaError, TimeoutError, CloudflareBypassError
from .utils import HumanBehaviorSimulator, CloudflareFingerprinting
from .captcha import CaptchaResolver

class CloudflareBypasser:
    """
    Clase principal para bypass de Cloudflare
    
    Ejemplos:
        # Uso básico (gratis)
        bypasser = CloudflareBypasser()
        success = bypasser.bypass_url("https://example.com")
        
        # Con API key de servicio externo
        bypasser = CloudflareBypasser(
            captcha_service="2captcha",
            api_key="tu_api_key"
        )
        
        # Con configuración personalizada
        config = BypassConfig(
            headless=True,
            captcha_service=CaptchaService.ANTICAPTCHA,
            api_key="tu_api_key"
        )
        bypasser = CloudflareBypasser(config=config)
    """
    
    def __init__(self, 
                 config: Optional[BypassConfig] = None,
                 captcha_service: Optional[str] = None,
                 api_key: Optional[str] = None,
                 headless: bool = False,
                 debug: bool = False):
        """
        Inicializa CloudflareBypasser
        
        Args:
            config: Configuración personalizada
            captcha_service: Servicio de captcha ("2captcha", "anticaptcha", etc.)
            api_key: API key para el servicio de captcha
            headless: Ejecutar en modo headless
            debug: Habilitar logs de debug
        """
        
        # Configurar configuración
        if config is None:
            config = BypassConfig()
        
        # Override con parámetros directos si se proporcionan
        if captcha_service:
            config.captcha_service = CaptchaService(captcha_service)
        if api_key:
            config.api_key = api_key
        if headless is not None:
            config.headless = headless
        if debug is not None:
            config.debug = debug
        
        # Validar configuración
        config.validate()
        
        self.config = config
        self.driver = None
        self.wait = None
        self.captcha_resolver = None
        self.behavior_sim = None
        self.fingerprinting = None
        
        if self.config.debug:
            print(f"🔧 CloudflareBypasser inicializado con modo: {self.config.mode.value}")
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit()
    
    def start(self):
        """Inicia el driver y componentes"""
        try:
            if self.config.debug:
                print("🚀 Iniciando driver...")
            
            self.driver = self._create_driver()
            self.wait = WebDriverWait(self.driver, self.config.timeout)
            
            # Inicializar componentes
            self.behavior_sim = HumanBehaviorSimulator(self.driver)
            self.fingerprinting = CloudflareFingerprinting(self.driver)
            
            if self.config.captcha_service != CaptchaService.NONE:
                self.captcha_resolver = CaptchaResolver(
                    self.config.captcha_service.value,
                    self.config.api_key,
                    self.config.service_urls
                )
            
            if self.config.debug:
                print("✅ Driver y componentes iniciados")
                
        except Exception as e:
            raise DriverError(f"Error iniciando driver: {e}")
    
    def quit(self):
        """Cierra el driver"""
        if self.driver:
            try:
                self.driver.quit()
                if self.config.debug:
                    print("🔚 Driver cerrado")
            except:
                pass
    
    def bypass_url(self, url: str, max_wait: int = None) -> bool:
        """
        Realiza bypass de Cloudflare para una URL específica
        
        Args:
            url: URL objetivo
            max_wait: Tiempo máximo de espera (usa config.timeout por defecto)
            
        Returns:
            bool: True si el bypass fue exitoso
        """
        if not self.driver:
            self.start()
        
        if max_wait is None:
            max_wait = self.config.timeout
        
        try:
            if self.config.debug:
                print(f"🌐 Navegando a: {url}")
            
            # Navegación inteligente
            self._smart_navigation(url)
            
            # Detectar y bypasear Cloudflare
            return self._detect_and_bypass_cloudflare(max_wait)
            
        except Exception as e:
            if self.config.debug:
                print(f"❌ Error en bypass: {e}")
            raise CloudflareBypassError(f"Error en bypass de {url}: {e}")
    
    def get_page_source(self) -> str:
        """Obtiene el código fuente de la página actual"""
        if not self.driver:
            raise DriverError("Driver no iniciado")
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """Obtiene la URL actual"""
        if not self.driver:
            raise DriverError("Driver no iniciado")
        return self.driver.current_url
    
    def get_title(self) -> str:
        """Obtiene el título de la página actual"""
        if not self.driver:
            raise DriverError("Driver no iniciado")
        return self.driver.title
    
    def execute_script(self, script: str) -> Any:
        """Ejecuta JavaScript en la página"""
        if not self.driver:
            raise DriverError("Driver no iniciado")
        return self.driver.execute_script(script)
    
    def find_element(self, by: str, value: str):
        """Busca un elemento en la página"""
        if not self.driver:
            raise DriverError("Driver no iniciado")
        return self.driver.find_element(by, value)
    
    def find_elements(self, by: str, value: str):
        """Busca elementos en la página"""
        if not self.driver:
            raise DriverError("Driver no iniciado")
        return self.driver.find_elements(by, value)
    
    def _create_driver(self) -> uc.Chrome:
        """Crea el driver con configuración optimizada"""
        try:
            # Determinar versión de Chrome
            chrome_version = self.config.chrome_version
            if chrome_version is None:
                # Detectar automáticamente
                chrome_version = 139  # Versión actual común
            
            # Crear opciones básicas
            options = uc.ChromeOptions() if self.config.custom_chrome_options else None
            
            if self.config.custom_chrome_options and options:
                for option in self.config.custom_chrome_options:
                    options.add_argument(option)
            
            # Configurar proxy si se especificó
            if self.config.proxy and options:
                options.add_argument(f"--proxy-server={self.config.proxy}")
            
            # Crear driver
            driver = uc.Chrome(
                options=options,
                headless=self.config.headless,
                use_subprocess=True,
                version_main=chrome_version
            )
            
            # Configurar ventana
            driver.set_window_size(*self.config.window_size)
            
            # Aplicar técnicas anti-detección
            if self.config.enable_stealth:
                self._apply_stealth_techniques(driver)
            
            return driver
            
        except Exception as e:
            raise DriverError(f"Error creando driver: {e}")
    
    def _apply_stealth_techniques(self, driver):
        """Aplica técnicas de stealth al driver"""
        stealth_script = """
        // Eliminar propiedades de webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        delete navigator.__proto__.webdriver;
        
        // Simular plugins reales
        Object.defineProperty(navigator, 'plugins', {
            get: () => ({
                length: 4,
                'Chrome PDF Plugin': true,
                'Chrome PDF Viewer': true,
                'Native Client': true,
                'Shockwave Flash': true
            }),
        });
        
        // Simular lenguajes
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'es'],
        });
        
        console.log('Stealth techniques applied');
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_script
        })
    
    def _smart_navigation(self, url: str):
        """Navegación inteligente con simulación humana"""
        # Simular referrer
        if self.config.simulate_human:
            self.driver.execute_script("""
                Object.defineProperty(document, 'referrer', {
                    get: () => 'https://www.google.com/',
                    configurable: true
                });
            """)
        
        # Navegar
        self.driver.get(url)
        
        # Simular comportamiento humano
        if self.config.simulate_human:
            time.sleep(random.uniform(2, 4))
            self.driver.execute_script("window.scrollTo(0, 100);")
            time.sleep(random.uniform(0.5, 1.5))
    
    def _detect_and_bypass_cloudflare(self, max_wait: int) -> bool:
        """Detecta y bypasa protección de Cloudflare"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Verificar si hay challenge de Cloudflare
            if not self._has_cloudflare_challenge():
                if self.config.debug:
                    print("✅ No se detectó challenge de Cloudflare")
                return True
            
            if self.config.debug:
                print("⚠️ Challenge de Cloudflare detectado")
            
            # Aplicar fingerprint spoofing si está habilitado
            if self.config.enable_fingerprint_spoofing:
                self.fingerprinting.apply_all_spoofing()
            
            # Intentar bypass según el modo
            if self.config.mode == BypassMode.AUTO:
                success = self._auto_bypass()
            elif self.config.mode == BypassMode.STEALTH:
                success = self._stealth_bypass()
            elif self.config.mode == BypassMode.AGGRESSIVE:
                success = self._aggressive_bypass()
            else:  # MINIMAL
                success = self._minimal_bypass()
            
            if success:
                if self.config.debug:
                    print("✅ Bypass exitoso")
                return True
            
            # Esperar antes del siguiente intento
            time.sleep(self.config.retry_delay)
        
        if self.config.debug:
            print("❌ Timeout en bypass")
        return False
    
    def _has_cloudflare_challenge(self) -> bool:
        """Detecta si hay un challenge de Cloudflare activo"""
        indicators = [
            "Checking your browser before accessing",
            "Just a moment",
            "Please wait while we check your browser",
            "DDoS protection by Cloudflare",
            "This process is automatic"
        ]
        
        page_source = self.driver.page_source.lower()
        return any(indicator.lower() in page_source for indicator in indicators)
    
    def _auto_bypass(self) -> bool:
        """Bypass automático que intenta múltiples técnicas"""
        techniques = [
            self._wait_for_auto_resolve,
            self._attempt_manual_solve,
            self._attempt_captcha_service if self.captcha_resolver else None
        ]
        
        for technique in techniques:
            if technique and technique():
                return True
        
        return False
    
    def _stealth_bypass(self) -> bool:
        """Bypass sigiloso con técnicas avanzadas"""
        # Implementar técnicas sigilosas específicas
        return self._wait_for_auto_resolve(timeout=30)
    
    def _aggressive_bypass(self) -> bool:
        """Bypass agresivo para casos difíciles"""
        # Combinar todas las técnicas disponibles
        return self._auto_bypass()
    
    def _minimal_bypass(self) -> bool:
        """Bypass mínimo para casos simples"""
        return self._wait_for_auto_resolve(timeout=10)
    
    def _wait_for_auto_resolve(self, timeout: int = 30) -> bool:
        """Espera a que el challenge se resuelva automáticamente"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self._has_cloudflare_challenge():
                return True
            
            if self.config.simulate_human:
                self.behavior_sim.simulate_reading_behavior()
            
            time.sleep(random.uniform(1, 3))
        
        return False
    
    def _attempt_manual_solve(self) -> bool:
        """Intenta resolución manual de captcha"""
        try:
            # Buscar iframe de Turnstile
            iframe_selectors = [
                "iframe[src*='turnstile']",
                "iframe[src*='cloudflare']",
                ".cf-turnstile iframe"
            ]
            
            for selector in iframe_selectors:
                try:
                    iframe = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if not iframe.is_displayed():
                        continue
                    
                    # Cambiar al iframe
                    self.driver.switch_to.frame(iframe)
                    
                    # Buscar checkbox
                    checkbox_selectors = [
                        "input[type='checkbox']",
                        ".cb-i",
                        "[role='checkbox']"
                    ]
                    
                    for cb_selector in checkbox_selectors:
                        try:
                            checkbox = self.wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, cb_selector))
                            )
                            
                            if self.config.simulate_human:
                                self.behavior_sim.human_click(checkbox)
                            else:
                                checkbox.click()
                            
                            # Volver al contenido principal
                            self.driver.switch_to.default_content()
                            time.sleep(5)
                            
                            return not self._has_cloudflare_challenge()
                            
                        except TimeoutException:
                            continue
                    
                    # Volver al contenido principal
                    self.driver.switch_to.default_content()
                    
                except TimeoutException:
                    continue
            
            return False
            
        except Exception as e:
            if self.config.debug:
                print(f"Error en resolución manual: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def _attempt_captcha_service(self) -> bool:
        """Intenta resolver usando servicio de captcha externo"""
        if not self.captcha_resolver:
            return False
        
        try:
            # Extraer sitekey
            sitekey = self._extract_turnstile_sitekey()
            if not sitekey:
                return False
            
            # Resolver con servicio
            token = self.captcha_resolver.solve_turnstile(
                sitekey=sitekey,
                page_url=self.driver.current_url,
                timeout=self.config.captcha_timeout
            )
            
            if token:
                # Inyectar token
                return self._inject_turnstile_token(token)
            
            return False
            
        except Exception as e:
            if self.config.debug:
                print(f"Error con servicio de captcha: {e}")
            return False
    
    def _extract_turnstile_sitekey(self) -> Optional[str]:
        """Extrae el sitekey de Turnstile"""
        try:
            # Buscar en elementos con data-sitekey
            elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-sitekey]")
            for element in elements:
                sitekey = element.get_attribute("data-sitekey")
                if sitekey:
                    return sitekey
            
            # Buscar en scripts
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                content = script.get_attribute("innerHTML")
                if content and "sitekey" in content.lower():
                    match = re.search(r'["\']sitekey["\']\s*:\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    def _inject_turnstile_token(self, token: str) -> bool:
        """Inyecta token de Turnstile resuelto"""
        try:
            script = f"""
            if (window.turnstile && window.turnstile.getResponse) {{
                // Buscar widgets y actualizar
                const widgets = document.querySelectorAll('.cf-turnstile');
                for (let widget of widgets) {{
                    const callback = widget.getAttribute('data-callback');
                    if (callback && window[callback]) {{
                        window[callback]('{token}');
                        break;
                    }}
                }}
            }}
            """
            
            self.driver.execute_script(script)
            time.sleep(3)
            
            return not self._has_cloudflare_challenge()
            
        except Exception:
            return False
