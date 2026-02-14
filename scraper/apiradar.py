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

    def navigate_to_leaks(self, save_debug=True):
        """Navega a la sección de leaks (/explore)."""
        from config.settings import DATA_DIR, APIRADAR_URL

        url = f"{APIRADAR_URL}/explore"
        print(f"   Navegando a {url}...")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        # Extra wait for Next.js CSR to render cards
        self.page.wait_for_timeout(3000)

        if save_debug:
            debug_path = DATA_DIR / "debug_page.html"
            html = self.page.content()
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"   Debug HTML guardado en: {debug_path}")
            print(f"   URL actual: {self.page.url}")
            print(f"   Título: {self.page.title()}")

    def extract_leaks(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Extrae la lista de leaks visibles usando page.evaluate()
        para mayor eficiencia con el DOM de APIRadar.
        """
        leaks = self.page.evaluate("""(limit) => {
            const grid = document.querySelector('.grid.grid-cols-1');
            if (!grid) return [];

            const cards = grid.querySelectorAll(':scope > div.relative');
            const results = [];

            for (let i = 0; i < cards.length; i++) {
                if (limit && i >= limit) break;

                const card = cards[i];
                try {
                    // Key preview (desktop version with more chars)
                    const keyEl = card.querySelector('code span.hidden.sm\\\\:inline')
                               || card.querySelector('code span');
                    const keyPreview = keyEl ? keyEl.textContent.trim() : '';

                    // Provider badge
                    const providerEl = card.querySelector('.inline-flex.items-center.rounded-sm');
                    const provider = providerEl ? providerEl.textContent.trim() : '';

                    // Repository link (first github link)
                    const repoLink = card.querySelector('a[href*="github.com"][href*="/blob/"]');
                    const sourceUrl = repoLink ? repoLink.href : '';
                    const repoName = repoLink ? repoLink.querySelector('span.truncate')?.textContent.trim() : '';

                    // Owner/user (second github link)
                    const userLink = card.querySelector('a[href*="github.com"]:not([href*="/blob/"])');
                    const owner = userLink ? userLink.textContent.trim() : '';

                    // Full repository path
                    const repository = owner && repoName ? owner + '/' + repoName : repoName;

                    // File path from code element with title attribute
                    const filePathEl = card.querySelector('code[title]');
                    const filePath = filePathEl ? filePathEl.getAttribute('title') : '';

                    // Dates - look for spans after "Added:" and "Detected:"
                    let addedAt = '';
                    let detectedAt = '';
                    const dateSpans = card.querySelectorAll('span.text-muted-foreground\\\\/70');
                    dateSpans.forEach(span => {
                        const label = span.textContent.trim();
                        const valueEl = span.nextElementSibling;
                        if (valueEl) {
                            if (label === 'Added:') addedAt = valueEl.textContent.trim();
                            if (label === 'Detected:') detectedAt = valueEl.textContent.trim();
                        }
                    });

                    if (keyPreview || provider) {
                        results.push({
                            provider,
                            key_preview: keyPreview,
                            repository,
                            owner,
                            file_path: filePath,
                            source_url: sourceUrl,
                            added_at: addedAt,
                            detected_at: detectedAt,
                            extracted_at: new Date().toISOString()
                        });
                    }
                } catch (e) {
                    // Skip cards that fail to parse
                }
            }
            return results;
        }""", limit)

        self.data = leaks
        return leaks

    def load_more(self) -> bool:
        """Intenta scroll para cargar más (infinite scroll con IntersectionObserver)."""
        try:
            prev_count = len(self.page.locator(".grid.grid-cols-1 > div.relative").all())

            # Scroll al fondo y esperar que el IntersectionObserver dispare la carga
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(2500)

            # Segundo scroll por si el observer necesita más margen
            self.page.evaluate("""
                const sentinel = document.querySelector('.grid.grid-cols-1')?.lastElementChild;
                if (sentinel) sentinel.scrollIntoView({ behavior: 'smooth' });
            """)
            self.page.wait_for_timeout(1500)

            new_count = len(self.page.locator(".grid.grid-cols-1 > div.relative").all())
            return new_count > prev_count
        except Exception:
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
