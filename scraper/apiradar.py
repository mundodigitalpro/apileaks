"""Scraper de APIRadar."""
import json
from datetime import datetime
from typing import List, Dict, Any
from playwright.sync_api import Page


class APIRadarScraper:
    """Extrae datos de fugas de API keys de APIRadar."""
    
    def __init__(self, page: Page):
        self.page = page
        self.data: List[Dict[str, Any]] = []
    
    def navigate_to_leaks(self):
        """Navega a la sección de leaks."""
        # Asumiendo que hay una ruta /leaks o similar
        # Ajustar según la estructura real de la web
        self.page.goto("https://apiradar.live/leaks")
        self.page.wait_for_load_state("networkidle")
    
    def extract_leaks(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Extrae la lista de leaks visibles.
        
        Args:
            limit: Máximo número de leaks a extraer (None = todos)
        """
        # Selectores CSS - ajustar tras inspeccionar la web
        # Estos son ejemplos, deben adaptarse al DOM real
        leak_cards = self.page.locator("[data-leak], .leak-card, tr.leak-row").all()
        
        leaks = []
        for i, card in enumerate(leak_cards):
            if limit and i >= limit:
                break
            
            try:
                leak = self._parse_leak_card(card)
                if leak:
                    leaks.append(leak)
            except Exception as e:
                print(f"⚠️ Error parseando leak {i}: {e}")
        
        self.data = leaks
        return leaks
    
    def _parse_leak_card(self, card) -> Dict[str, Any]:
        """Extrae datos de una tarjeta de leak individual."""
        # Ajustar selectores según el HTML real de apiradar.live
        leak = {
            "provider": self._safe_text(card, ".provider, [data-provider]"),
            "key_preview": self._safe_text(card, ".key-preview, [data-key]"),
            "repository": self._safe_text(card, ".repo, [data-repo]"),
            "file_path": self._safe_text(card, ".file-path, [data-file]"),
            "detected_at": self._safe_text(card, ".timestamp, [data-time]"),
            "source_url": self._safe_attr(card, "a[href*='/commit/'], [data-source]", "href"),
            "extracted_at": datetime.now().isoformat(),
        }
        return leak
    
    def _safe_text(self, element, selector: str) -> str:
        """Extrae texto de forma segura."""
        try:
            return element.locator(selector).first.inner_text(timeout=1000).strip()
        except:
            return ""
    
    def _safe_attr(self, element, selector: str, attr: str) -> str:
        """Extrae atributo de forma segura."""
        try:
            return element.locator(selector).first.get_attribute(attr, timeout=1000) or ""
        except:
            return ""
    
    def load_more(self) -> bool:
        """Carga más leaks si hay paginación o scroll infinito."""
        # Implementar según la UI de la web
        try:
            load_more_btn = self.page.locator("button:has-text('Load more'), .load-more").first
            if load_more_btn.is_visible(timeout=2000):
                load_more_btn.click()
                self.page.wait_for_timeout(1000)  # Esperar carga
                return True
        except:
            pass
        return False
    
    def export_to_json(self, filename: str = None) -> str:
        """Exporta los datos a JSON."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leaks_{timestamp}.json"
        
        from config.settings import DATA_DIR
        filepath = DATA_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Datos guardados en: {filepath}")
        return str(filepath)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas básicas de los datos extraídos."""
        if not self.data:
            return {"total": 0}
        
        providers = {}
        for leak in self.data:
            provider = leak.get("provider", "unknown")
            providers[provider] = providers.get(provider, 0) + 1
        
        return {
            "total": len(self.data),
            "by_provider": providers,
            "extracted_at": datetime.now().isoformat(),
        }
