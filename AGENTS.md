# Repository Guidelines

## Project Structure & Module Organization
Primary code is Python-first:
- `main.py`: CLI entry point for both API mode (`--api`) and browser scraper mode.
- `scraper/`: core modules (`auth.py`, `api_client.py`, `apiradar.py`).
- `config/settings.py`: environment-driven paths and runtime settings.
- `data/`: exported leak datasets (`.json`, gitignored except `data/.gitkeep`).
- `session/`: Playwright auth session state (sensitive, gitignored).

Docs and ops context:
- `README.md`, `SETUP_LOCAL.md`, `DEPLOYMENT_PLAN.md`, `CHANGELOG.md`.

## Build, Test, and Development Commands
- `pip install -r requirements.txt`: install Python dependencies.
- `playwright install chromium`: install browser runtime once.
- `python main.py`: interactive scraper login flow (first run) or scraper mode.
- `python main.py --api --limit 100`: fast API extraction mode.
- `python main.py --headless --load-more --max-pages 50`: headless scraper with pagination by scroll.

## Coding Style & Naming Conventions
- Follow existing Python style: 4-space indentation, `snake_case` for functions/variables, `UPPER_CASE` for constants (see `config/settings.py`).
- Keep modules focused: auth logic in `auth.py`, HTTP client logic in `api_client.py`, DOM extraction in `apiradar.py`.
- Prefer explicit CLI flags and clear help text when adding arguments in `main.py`.
- Use concise docstrings for public functions and classes.

## Testing Guidelines
- No formal automated test suite is configured yet.
- Before opening a PR, run smoke checks:
  - `python main.py --api --limit 5`
  - `python main.py --headless --limit 5` (with a valid session)
- Verify output files are generated in `data/` and avoid committing extracted sensitive data.

## Commit & Pull Request Guidelines
- Match project history style: short, imperative commit subjects (e.g., `Add retry logic to API client`, `Update README with CLI examples`).
- Keep commits scoped to one logical change.
- PRs should include:
  - What changed and why
  - How it was validated (commands + observed result)
  - Any auth/session impact or selector/API assumptions
  - Linked issue/task when applicable

## Security & Configuration Tips
- Never commit `.env`, `session/`, or extracted leak artifacts.
- Treat exported data and session cookies as sensitive credentials.
- Use environment variables (`HEADLESS`, `TIMEOUT`) for local runtime tuning.
