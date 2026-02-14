# APILeaks Project Memory

## API interna de APIRadar
- **Endpoint principal:** `GET /api/leaks?page=N&limit=50&provider=X&sortBy=newest&timeRange=30d`
- **Con auth (cookies de sesión):** `planLimits.maxLeaks: null` = sin límite, paginación completa
- **Sin auth:** max 4 leaks, `hasMore: false` siempre
- **Auth setup:** cookies de Playwright storage_state + `GET /api/auth/session` para `backendToken`
- **Endpoints públicos:** `/api/leaderboard`, `/api/leaderboard/activity`, `/api/leaderboard/top-leakers`
- **DB:** MongoDB (ObjectIDs). Framework: Next.js App Router + NextAuth.js Google OAuth
- **Rate limit:** 429 con `retryAfter` en response

## Arquitectura del scraper
- **Modo API** (`--api`): usa `scraper/api_client.py`, solo HTTP con `requests`
- **Modo scraper** (default): usa Playwright para navegador con CSS selectors
- La sesión de auth se guarda en `session/apiradar_session.json` (Playwright storage_state)
- URL correcta de leaks: `/explore` (no `/leaks`)

## Proveedores válidos
openai, anthropic, google, groq, deepseek, mistral, xai, cerebras
