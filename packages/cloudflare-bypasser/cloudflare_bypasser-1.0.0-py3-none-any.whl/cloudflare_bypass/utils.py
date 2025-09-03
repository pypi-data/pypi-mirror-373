"""
Utilidades para simulación de comportamiento humano y spoofing
"""

import time
import random
from typing import Tuple, List
from selenium.webdriver.common.action_chains import ActionChains


class HumanBehaviorSimulator:
    """Simula comportamiento humano realista"""
    
    def __init__(self, driver):
        self.driver = driver
        self.last_mouse_pos = (random.randint(100, 500), random.randint(100, 500))
    
    def generate_human_mouse_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Genera una trayectoria de mouse humana entre dos puntos"""
        x1, y1 = start
        x2, y2 = end
        
        num_points = random.randint(10, 30)
        points = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Curva bezier simplificada
            control_x = (x1 + x2) / 2 + random.uniform(-50, 50)
            control_y = (y1 + y2) / 2 + random.uniform(-50, 50)
            
            # Interpolación cuadrática
            x = (1-t)**2 * x1 + 2*(1-t)*t * control_x + t**2 * x2
            y = (1-t)**2 * y1 + 2*(1-t)*t * control_y + t**2 * y2
            
            # Añadir ruido natural
            x += random.uniform(-2, 2)
            y += random.uniform(-2, 2)
            
            points.append((int(x), int(y)))
        
        return points
    
    def human_click(self, element):
        """Realiza un click humano con timing natural"""
        try:
            # Mover mouse de forma humana
            self.human_mouse_move(element)
            
            # Pausa antes del click
            time.sleep(random.uniform(0.1, 0.3))
            
            # Click
            actions = ActionChains(self.driver)
            actions.click(element).perform()
            
            # Pausa después del click
            time.sleep(random.uniform(0.05, 0.15))
            
        except Exception as e:
            # Fallback a click normal
            element.click()
    
    def human_mouse_move(self, element):
        """Mueve el mouse de forma humana hacia un elemento"""
        try:
            location = element.location
            size = element.size
            target_x = location['x'] + size['width'] // 2 + random.randint(-5, 5)
            target_y = location['y'] + size['height'] // 2 + random.randint(-5, 5)
            
            # Generar trayectoria humana
            path = self.generate_human_mouse_path(self.last_mouse_pos, (target_x, target_y))
            
            # Ejecutar movimiento
            actions = ActionChains(self.driver)
            
            for i, (x, y) in enumerate(path):
                if i == 0:
                    continue
                    
                prev_x, prev_y = path[i-1]
                offset_x = x - prev_x
                offset_y = y - prev_y
                
                actions.move_by_offset(offset_x, offset_y)
                
                if i % 5 == 0:
                    actions.pause(random.uniform(0.01, 0.05))
            
            actions.perform()
            self.last_mouse_pos = (target_x, target_y)
            
        except Exception:
            pass
    
    def simulate_reading_behavior(self):
        """Simula comportamiento de lectura humano"""
        try:
            # Scroll aleatorio
            scroll_amount = random.randint(-200, 200)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # Pausas de lectura
            time.sleep(random.uniform(0.5, 2.0))
            
            # Movimientos ocasionales de mouse
            if random.random() < 0.3:
                window_size = self.driver.get_window_size()
                random_x = random.randint(50, window_size['width'] - 50)
                random_y = random.randint(50, window_size['height'] - 50)
                
                actions = ActionChains(self.driver)
                actions.move_by_offset(random_x - 300, random_y - 300).perform()
                
        except Exception:
            pass


class CloudflareFingerprinting:
    """Manejo avanzado de fingerprinting de Cloudflare"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def spoof_webgl_fingerprint(self):
        """Falsifica el fingerprint de WebGL"""
        script = """
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris Pro OpenGL Engine';
            }
            if (parameter === 37447) {
                return 'OpenGL ES 2.0 Intel-14.7.8';
            }
            return getParameter.call(this, parameter);
        };
        """
        self.driver.execute_script(script)
    
    def spoof_canvas_fingerprint(self):
        """Falsifica el fingerprint de Canvas"""
        script = """
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        
        function addNoiseToImageData(imageData) {
            const data = imageData.data;
            for (let i = 0; i < data.length; i += 4) {
                if (Math.random() < 0.001) {
                    data[i] = Math.floor(Math.random() * 255);
                    data[i + 1] = Math.floor(Math.random() * 255); 
                    data[i + 2] = Math.floor(Math.random() * 255);
                }
            }
            return imageData;
        }
        
        HTMLCanvasElement.prototype.toDataURL = function() {
            const context = this.getContext('2d');
            if (context) {
                const imageData = context.getImageData(0, 0, this.width, this.height);
                addNoiseToImageData(imageData);
                context.putImageData(imageData, 0, 0);
            }
            return originalToDataURL.apply(this, arguments);
        };
        """
        self.driver.execute_script(script)
    
    def spoof_timezone_and_locale(self):
        """Falsifica timezone y configuraciones de localización"""
        script = """
        if (Intl && Intl.DateTimeFormat) {
            const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
            Intl.DateTimeFormat.prototype.resolvedOptions = function() {
                const options = originalResolvedOptions.call(this);
                options.timeZone = 'America/New_York';
                options.locale = 'en-US';
                return options;
            };
        }
        
        Object.defineProperty(navigator, 'language', {
            get: () => 'en-US',
            configurable: true
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
            configurable: true
        });
        """
        self.driver.execute_script(script)
    
    def apply_all_spoofing(self):
        """Aplica todas las técnicas de spoofing"""
        try:
            self.spoof_webgl_fingerprint()
            self.spoof_canvas_fingerprint()
            self.spoof_timezone_and_locale()
        except Exception:
            pass  # Fallar silenciosamente para no interrumpir el flujo
