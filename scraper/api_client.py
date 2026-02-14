"""Cliente directo para la API interna de APIRadar."""
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests

from config.settings import SESSION_FILE, APIRADAR_URL, DATA_DIR


class APIRadarClient:
    """Accede a /api/leaks directamente vía HTTP, sin navegador."""

    BASE_URL = APIRADAR_URL
    LEAKS_ENDPOINT = f"{BASE_URL}/api/leaks"
    DEFAULT_LIMIT = 50

    def __init__(self, session_file: str = None):
        self.session_file = Path(session_file or SESSION_FILE)
        self.http = requests.Session()
        self.http.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": f"{self.BASE_URL}/explore",
        })
        self._load_cookies()
        self.all_leaks: List[Dict[str, Any]] = []

    def _load_cookies(self):
        """Carga cookies desde el storage_state de Playwright."""
        if not self.session_file.exists():
            print("⚠️  No hay sesión guardada. Ejecuta primero sin --api para login.")
            return

        with open(self.session_file, "r") as f:
            state = json.load(f)

        cookies = state.get("cookies", [])
        for cookie in cookies:
            self.http.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain", ""),
                path=cookie.get("path", "/"),
            )
        print(f"🔑 Cargadas {len(cookies)} cookies desde sesión.")

    def _set_auth_headers(self, user_id: str, user_email: str, backend_token: str = None):
        """Configura headers de autenticación para obtener más resultados."""
        self.http.headers.update({
            "x-user-id": user_id,
            "x-user-email": user_email,
            "x-user-authenticated": "true",
        })
        if backend_token:
            self.http.headers["Authorization"] = f"Bearer {backend_token}"

    def fetch_session_info(self) -> Dict[str, Any]:
        """Obtiene la sesión NextAuth (incluye backendToken si autenticado)."""
        resp = self.http.get(f"{self.BASE_URL}/api/auth/session")
        resp.raise_for_status()
        return resp.json()

    def setup_auth_from_session(self) -> bool:
        """Intenta configurar auth headers desde la sesión NextAuth."""
        session = self.fetch_session_info()
        user = session.get("user", {})
        if not user:
            print("⚠️  Sesión no autenticada. Solo se obtendrán 4 leaks (plan gratuito).")
            return False

        self._set_auth_headers(
            user_id=user.get("id", ""),
            user_email=user.get("email", ""),
            backend_token=session.get("backendToken"),
        )
        print(f"🔓 Autenticado como: {user.get('email', 'unknown')}")
        return True

    def fetch_leaderboard(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales: totalReposScanned, totalLeaksFound, leaksFoundToday."""
        resp = self.http.get(f"{self.BASE_URL}/api/leaderboard")
        resp.raise_for_status()
        return resp.json()

    def fetch_activity(self) -> List[Dict[str, Any]]:
        """Obtiene actividad semanal de leaks detectados."""
        resp = self.http.get(f"{self.BASE_URL}/api/leaderboard/activity")
        resp.raise_for_status()
        return resp.json()

    def fetch_top_leakers(self) -> List[Dict[str, Any]]:
        """Obtiene top 10 usuarios con más leaks."""
        resp = self.http.get(f"{self.BASE_URL}/api/leaderboard/top-leakers")
        resp.raise_for_status()
        return resp.json()

    def fetch_leaks(
        self,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
        provider: str = None,
        sort_by: str = "newest",
        time_range: str = None,
    ) -> Dict[str, Any]:
        """Hace una petición a /api/leaks y devuelve la respuesta."""
        params = {
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
        }
        if provider:
            params["provider"] = provider
        if time_range:
            params["timeRange"] = time_range

        for attempt in range(4):
            resp = self.http.get(self.LEAKS_ENDPOINT, params=params)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 10))
                print(f"   ⏳ Rate limit (429). Esperando {wait}s...")
                time.sleep(wait)
                continue
            if resp.status_code in (502, 503, 504) and attempt < 3:
                wait = 3 * (attempt + 1)
                print(f"   ⚠️  Error {resp.status_code}. Reintento en {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            self._enrich_leaks(data.get("leaks", []))
            return data
        resp.raise_for_status()
        data = resp.json()
        self._enrich_leaks(data.get("leaks", []))
        return data

    @staticmethod
    def _enrich_leaks(leaks: List[Dict[str, Any]]):
        """Añade fileUrl (enlace directo al archivo en GitHub) a cada leak."""
        for leak in leaks:
            repo = leak.get("repoUrl", "")
            fp = leak.get("filePath", "")
            if repo and fp:
                leak["fileUrl"] = f"{repo}/blob/HEAD/{fp}"

    def fetch_all_leaks(
        self,
        limit_per_page: int = DEFAULT_LIMIT,
        max_leaks: int = None,
        provider: str = None,
        sort_by: str = "newest",
        time_range: str = None,
        delay: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Pagina automáticamente por todos los leaks disponibles.

        Args:
            limit_per_page: leaks por página (max 50 recomendado)
            max_leaks: límite total de leaks a descargar (None = todos)
            provider: filtrar por proveedor (openai, anthropic, groq, etc.)
            sort_by: orden (newest, oldest)
            time_range: rango de tiempo (7d, 30d, 90d, etc.)
            delay: pausa entre peticiones (evitar rate-limit)
        """
        self.all_leaks = []
        page = 1

        # Primera petición para obtener total
        data = self.fetch_leaks(
            page=page,
            limit=limit_per_page,
            provider=provider,
            sort_by=sort_by,
            time_range=time_range,
        )

        leaks = data.get("leaks", [])
        total = data.get("total", 0)
        has_more = data.get("hasMore", False)
        plan_limits = data.get("planLimits", {})

        self.all_leaks.extend(leaks)
        print(f"📊 Total disponible: {total} leaks")
        if plan_limits.get("maxLeaks"):
            print(f"   Plan limits: {plan_limits['maxLeaks']} leaks por plan")
        print(f"   Página {page}: {len(leaks)} leaks descargados")

        # Truncar si ya se alcanzó el límite
        if max_leaks and len(self.all_leaks) >= max_leaks:
            self.all_leaks = self.all_leaks[:max_leaks]
            return self.all_leaks

        # Paginar mientras haya más
        try:
            while has_more:
                if max_leaks and len(self.all_leaks) >= max_leaks:
                    self.all_leaks = self.all_leaks[:max_leaks]
                    break

                page += 1
                time.sleep(delay)

                data = self.fetch_leaks(
                    page=page,
                    limit=limit_per_page,
                    provider=provider,
                    sort_by=sort_by,
                    time_range=time_range,
                )

                leaks = data.get("leaks", [])
                has_more = data.get("hasMore", False)

                if not leaks:
                    break

                self.all_leaks.extend(leaks)
                print(f"   Página {page}: +{len(leaks)} leaks (total: {len(self.all_leaks)})")

        except (KeyboardInterrupt, Exception) as e:
            if self.all_leaks:
                print(f"\n⚠️  Error en página {page}: {e}")
                print(f"   Guardando {len(self.all_leaks)} leaks descargados hasta ahora...")
                self.export_to_json()
            if isinstance(e, KeyboardInterrupt):
                raise
            raise

        return self.all_leaks

    def export_to_json(self, filename: str = None) -> str:
        """Exporta los datos a JSON."""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leaks_api_{timestamp}.json"

        filepath = DATA_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.all_leaks, f, indent=2, ensure_ascii=False)

        print(f"💾 Datos guardados en: {filepath}")
        return str(filepath)

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de los datos descargados."""
        if not self.all_leaks:
            return {"total": 0}

        providers = {}
        for leak in self.all_leaks:
            p = leak.get("provider", "unknown")
            providers[p] = providers.get(p, 0) + 1

        return {
            "total": len(self.all_leaks),
            "by_provider": providers,
        }
