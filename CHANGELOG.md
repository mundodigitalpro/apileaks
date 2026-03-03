# Changelog

Todos los cambios notables en el proyecto APILeaks.

## [Unreleased]

### Próximos pasos
- [ ] Despliegue en VPS
- [ ] Configuración de cron para ejecución automatizada

---

## 2026-03-03

### Changed
- **Eliminado stack Node.js** — `main.js`, `package.json`, `package-lock.json`, `node_modules/` eliminados. Stack único: Python.
- **`DEPLOYMENT_PLAN.md` y `SETUP_LOCAL.md` actualizados** — migrados de Node.js a Python (venv, pip, playwright).
- **`MEMORY.md` eliminado** — contenido absorbido en `CLAUDE.md`.
- **`AGENTS.md` eliminado** — coding style, testing y commit guidelines fusionados en `CLAUDE.md`.
- **`.claude/` añadido al `.gitignore`**.

---

## 2026-02-14

### Descubierto
- **API interna de APIRadar** en `GET /api/leaks`:
  - Parámetros: `page`, `limit`, `provider`, `sortBy`, `timeRange`
  - Headers auth: `x-user-id`, `x-user-email`, `x-user-authenticated`, `Authorization: Bearer {token}`
  - Sin auth: máximo 4 leaks por plan gratuito (`planLimits.maxLeaks: 4`)
  - Con auth: paginación completa (19,750+ leaks disponibles)
  - Filtros funcionales: `provider=anthropic` (495 resultados), `sortBy=oldest/newest`, `timeRange=30d`
- **No Supabase** — el backend usa NextAuth.js con Google OAuth, base de datos MongoDB (IDs tipo ObjectID)
- **Infinite scroll** implementado con IntersectionObserver (margen 600px)
- **Endpoints adicionales descubiertos** (sin auth requerida):
  - `GET /api/leaderboard` → `{totalReposScanned: 68238, totalLeaksFound: 19750, leaksFoundToday: 194}`
  - `GET /api/leaderboard/activity` → actividad semanal `[{date: "Sun", count: 490}, ...]`
  - `GET /api/leaderboard/top-leakers` → top 10 usuarios con más leaks
  - `GET /api/auth/session` → sesión NextAuth con `backendToken` (JWT)
  - No encontrados: `/api/stats`, `/api/providers` (404)
- **Cache client-side**: key = `leaks:${provider}:${timeRange}:${sortBy}:${page}:${limit}:${userId}`, TTL 500ms
- **`NEXT_PUBLIC_BACKEND_URL`** declarado pero no usado — todas las llamadas son a paths relativos

### Added
- **`scraper/api_client.py`** — Cliente HTTP directo para `/api/leaks`:
  - Extrae cookies del `storage_state` de Playwright para autenticación
  - Paginación automática (itera páginas hasta `hasMore=false`)
  - Soporte de filtros: provider, sortBy, timeRange
  - Delay configurable entre peticiones (anti rate-limit)
  - Export a JSON con estadísticas
  - Soporte de endpoints adicionales: leaderboard, activity, top-leakers
  - Auto-setup de auth headers desde sesión NextAuth (`backendToken`)
- **Flag `--api`** en `main.py` — Modo API directo (sin navegador, mucho más rápido)
- **Flags de filtro**: `--provider`, `--sort-by`, `--time-range`
- **Flag `--max-pages`** — Límite de scrolls en modo scraper

### Changed
- **`main.py`** refactorizado: separado en `run_api_mode()` y `run_scraper_mode()`
- **`--load-more` mejorado** — Ya no se detiene tras 20 scrolls:
  - Scroll infinito real: continúa hasta que no aparezcan más cards
  - Detección de "stale" (3 intentos sin nuevos datos = fin)
  - Segundo scroll al sentinel element para activar IntersectionObserver
  - Respeta `--limit` y `--max-pages`

### Sesión anterior (sin commitear)
- **Migración Python funcional** — Scraper Python operativo con Playwright
- **`scraper/auth.py`** — AuthManager con stealth mode (anti-detección Google):
  - `--disable-blink-features=AutomationControlled`
  - `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`
  - User-Agent simulado Chrome 120
- **`scraper/apiradar.py`** — Extracción vía `page.evaluate()` (JS en navegador):
  - Selectores CSS calibrados contra DOM real de APIRadar
  - Campos: provider, key_preview, repository, owner, file_path, source_url, dates
- **URL corregida**: `/explore` en lugar de `/leaks`
- **`requirements.txt`** actualizado: playwright, python-dotenv, pydantic, requests
- **Debug HTML**: guarda snapshot del DOM en `data/debug_page.html`

---

## 2026-02-13

### Added
- **README.md completo** - Documentación del proyecto con instalación, uso, y troubleshooting
- **DEPLOYMENT_PLAN.md** - Plan detallado para despliegue en VPS (Ubuntu/Debian)
- **SETUP_LOCAL.md** - Instrucciones para setup local con OAuth
- **CHANGELOG.md** - Historial del proyecto
- **Estructura base del scraper**:
  - `main.js` - Entry point Node.js con CLI args (--headless, --limit, --output)
  - `scraper/auth.js` - Gestión de autenticación OAuth con persistencia de sesión
  - `scraper/apiradar.js` - Lógica de extracción de datos
  - `config/settings.js` - Configuración centralizada
- **package.json** - Dependencias (Playwright)
- **.gitignore** - Exclusiones para datos sensibles y node_modules

### Changed
- Migración de **Python** a **Node.js** tras descubrir que pip no estaba disponible en Termux
- Adaptación del scraper para usar Playwright en lugar de Selenium

### Descubierto
- **Playwright NO soporta Android** - Error: "Unsupported platform: android"
- APIRadar usa **Next.js/React** con CSR - requiere navegador real
- El VPS será el entorno de despliegue final

### Infraestructura
- **GitHub**: Repo configurado con SSH key
- **SSH key generada** para acceso al VPS (pendiente de configurar)

---

## Estructura actual del repositorio

```
apileaks/
├── README.md                 # Documentación principal
├── SETUP_LOCAL.md            # Guía de setup local
├── DEPLOYMENT_PLAN.md        # Guía de despliegue VPS
├── CHANGELOG.md              # Este archivo
├── CLAUDE.md                 # Instrucciones para agentes AI
├── main.py                   # Entry point Python
├── requirements.txt          # Dependencias Python
├── config/
│   └── settings.py           # Configuración Python
├── scraper/
│   ├── auth.py               # Autenticación OAuth (Python)
│   ├── apiradar.py           # Scraping con Playwright (Python)
│   └── api_client.py         # Cliente API directo (Python)
├── prompts/                  # Prompts de configuración
├── data/                     # Datos extraídos (gitignored)
└── session/                  # Sesiones guardadas (gitignored)
```

---

## API interna descubierta

### Leaks (requiere auth para paginación)
```
GET /api/leaks?page=1&limit=50&provider=openai&sortBy=newest&timeRange=30d

Headers (autenticado):
  x-user-id: <id>
  x-user-email: <email>
  x-user-authenticated: true
  Authorization: Bearer <session.backendToken>

Respuesta: { leaks: [...], total: 19750, hasMore: bool, planLimits: { maxLeaks: N } }
Providers: openai, anthropic, google, groq, deepseek, mistral, xai, cerebras
Sin auth: max 4 leaks. Con auth: paginación completa.
```

### Leaderboard (público, sin auth)
```
GET /api/leaderboard
  → { totalReposScanned, totalLeaksFound, leaksFoundToday }

GET /api/leaderboard/activity
  → [{ date: "Sun", count: 490 }, ...]

GET /api/leaderboard/top-leakers
  → [{ rank, username, avatar_url, html_url, total_leaks, repos_count }, ...]
```

### Auth (NextAuth.js)
```
GET /api/auth/session   → { user: { id, email }, backendToken: "JWT..." }
GET /api/auth/providers → { google: { signinUrl, callbackUrl } }
GET /api/auth/csrf      → { csrfToken: "..." }
```

---

## Commits

- `f0c5827` - Add SETUP_LOCAL.md with OAuth login instructions for local setup
- `d0e1fa4` - Add CHANGELOG with project history
- `0bede4e` - Update README with complete documentation
- `9cdcb09` - Add deployment plan for VPS
- `162039f` - Update README: documentar limitaciones de entorno
- `3293969` - Initial commit: APIRadar scraper con auth OAuth

---

## Recursos

- **Repositorio**: https://github.com/mundodigitalpro/apileaks
- **Target**: https://apiradar.live
- **Stack**: Python 3 + Playwright + requests
