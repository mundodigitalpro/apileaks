"""Manejo de autenticación con Google OAuth."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from config.settings import SESSION_FILE, APIRADAR_URL, TIMEOUT


class AuthManager:
    """Gestiona la autenticación y sesión."""
    
    def __init__(self):
        self.session_file = Path(SESSION_FILE)
    
    def has_valid_session(self) -> bool:
        """Verifica si existe una sesión guardada."""
        return self.session_file.exists()
    
    def save_session(self, context):
        """Guarda el estado de la sesión."""
        context.storage_state(path=str(self.session_file))
        print(f"✅ Sesión guardada en {self.session_file}")
    
    def load_session(self, browser):
        """Carga una sesión existente."""
        return browser.new_context(storage_state=str(self.session_file))
    
    def login(self, headless: bool = False) -> Page:
        """
        Inicia sesión en APIRadar.
        
        Si existe sesión guardada, la usa.
        Si no, abre navegador para login manual con Google.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            
            if self.has_valid_session():
                print("🔑 Usando sesión guardada...")
                context = self.load_session(browser)
                page = context.new_page()
            else:
                print("🌐 No hay sesión. Abriendo navegador para login...")
                context = browser.new_context()
                page = context.new_page()
                
                # Ir a la página y hacer login
                page.goto(APIRADAR_URL)
                print("\n👉 Por favor:")
                print("   1. Haz clic en 'Sign in with Google'")
                print("   2. Completa el login con tus credenciales")
                print("   3. Espera a que cargue el dashboard")
                print("   4. Presiona ENTER aquí cuando estés logueado\n")
                
                input("Presiona ENTER cuando el login esté completo...")
                
                # Guardar sesión para futuras ejecuciones
                self.save_session(context)
            
            return page, browser, context
