# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

APILeaks extracts leaked API key data from [APIRadar](https://apiradar.live). Two extraction modes:

1. **API mode (`--api`)** — Direct HTTP calls to `/api/leaks` (fast, no browser needed)
2. **Scraper mode** (default) — Playwright browser automation with CSS selectors

APIRadar uses Next.js with CSR and has an internal REST API discovered via JS chunk analysis.

## Commands

```bash
# Install Python deps
pip install -r requirements.txt

# Install Playwright browsers (required once)
playwright install chromium

# First run: login (opens browser for Google OAuth)
python main.py

# API mode (fast, requires saved session)
python main.py --api                              # all leaks
python main.py --api --provider openai --limit 100
python main.py --api --sort-by oldest --time-range 30d

# Scraper mode
python main.py --headless                         # headless (requires saved session)
python main.py --headless --load-more             # infinite scroll (no page limit)
python main.py --headless --load-more --max-pages 50
```

No test suite or linter is configured yet.

## Architecture

```
main.py                  # Python CLI entry point (api + scraper modes)
config/settings.py       # Central config (paths, URLs, env vars)
scraper/
  auth.py                # AuthManager — OAuth login, session save/load
  apiradar.py            # APIRadarScraper — Playwright navigation, extraction, export
  api_client.py          # APIRadarClient — Direct HTTP client for /api/leaks
session/                 # Playwright storage_state JSON (gitignored)
data/                    # JSON output files (gitignored)
```

### Authentication flow
1. `AuthManager.has_valid_session()` checks if `session/apiradar_session.json` exists.
2. If no session: launches visible browser, user manually completes Google OAuth, presses ENTER, session is saved via `context.storage_state()`.
3. If session exists: restores it with `browser.new_context(storage_state=...)` and runs headless.

### API mode flow (--api)
1. `APIRadarClient` loads cookies from the saved Playwright `storage_state` JSON.
2. Makes GET requests to `https://apiradar.live/api/leaks` with query params: `page`, `limit`, `provider`, `sortBy`, `timeRange`.
3. Paginates automatically until `hasMore=false` or `--limit` reached.
4. Exports to timestamped JSON.

### Scraper mode flow (default)
1. Navigate to `apiradar.live/explore`, wait for `networkidle`.
2. Extract leak cards via `page.evaluate()` with CSS selectors against the real DOM.
3. If `--load-more`: infinite scroll via `scrollIntoView` triggering the IntersectionObserver.
4. Export to timestamped JSON in `data/`.

### API endpoint details
```
GET /api/leaks?page=1&limit=50&provider=openai&sortBy=newest&timeRange=30d

Auth headers: x-user-id, x-user-email, x-user-authenticated, Authorization: Bearer {token}
Response: { leaks: [...], total: 19750, hasMore: bool, planLimits: { maxLeaks: N } }

Without auth: max 4 leaks (free plan). With auth: full pagination.
```

### Key design notes
- CSS selectors in `scraper/apiradar.py` are calibrated against the real APIRadar DOM (grid > div.relative cards).
- The `login()` method in `auth.py` starts `sync_playwright()` and returns page/browser/playwright — caller must close.
- The API client reuses cookies from the Playwright session file — no separate auth needed.

## Sensitive files (gitignored)

- `session/` — OAuth tokens
- `data/*.json` — extracted leak data with partial API keys
- `.env` — environment config
