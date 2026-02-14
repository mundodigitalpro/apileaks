"""Manejo de autenticación con Google OAuth."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from config.settings import SESSION_FILE, APIRADAR_URL, TIMEOUT


class AuthManager:
    """Gestiona la autenticación y sesión."""
    
    def __init__(self):
        self.session_file = Path(SESSION_FILE)
        self.playwright = None
    
    def has_valid_session(self) -> bool:
        """Verifica si existe una sesión guardada."""
        return self.session_file.exists()
    
    def save_session(self, context):
        """Guarda el estado de la sesión."""
        context.storage_state(path=str(self.session_file))
        print(f"✅ Sesión guardada en {self.session_file}")
    
    def load_session(self, browser):
        """Carga una sesión existente."""
        return browser.new_context(
            storage_state=str(self.session_file),
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    def login(self, headless: bool = False):
        """
        Inicia sesión en APIRadar.
        """
        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        
        # Lanzar con stealth para evitar detección de Google
        browser = self.playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        if self.has_valid_session():
            print("🔑 Usando sesión guardada...")
            context = self.load_session(browser)
            page = context.new_page()
        else:
            print("🌐 No hay sesión. Abriendo navegador para login...")
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            
            # Script para ocultar automation
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
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
        
        return page, browser, self.playwright
