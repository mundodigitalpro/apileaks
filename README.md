# APILeaks

Extractor automatizado de fugas de API keys desde [APIRadar](https://apiradar.live).

APIRadar detecta claves API expuestas en repositorios publicos de GitHub en tiempo real. Este proyecto extrae esos datos para analisis, alertas o integraciones.

---

## Modos de operacion

APILeaks ofrece dos modos de extraccion:

| Modo | Comando | Descripcion |
|------|---------|-------------|
| **API** | `python main.py --api` | Peticiones HTTP directas a la API interna de APIRadar. Rapido, sin navegador. |
| **Scraper** | `python main.py` | Automatizacion con Playwright (navegador). Usa CSS selectors contra el DOM real. |

Tambien existe una implementacion Node.js (`main.js`) como fallback de debug.

---

## Requisitos

- **Python** 3.10+
- **Chromium** (instalado via Playwright)
- **Sistema operativo:** Linux, macOS o Windows

---

## Instalacion

```bash
# Clonar repositorio
git clone git@github.com:mundodigitalpro/apileaks.git
cd apileaks

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar navegador (necesario una sola vez)
playwright install chromium
```

---

## Autenticacion (primera ejecucion)

La primera vez es necesario iniciar sesion manualmente con Google OAuth:

```bash
python main.py
```

Se abrira una ventana del navegador. Pasos:

1. Clic en **"Sign in with Google"**
2. Completar el login con tus credenciales
3. Esperar a que cargue el dashboard
4. Presionar **ENTER** en la terminal

La sesion se guarda en `session/apiradar_session.json` y se reutiliza automaticamente en ejecuciones posteriores.

Para renovar la sesion si expira:

```bash
rm session/apiradar_session.json
python main.py
```

---

## Uso

### Modo API (recomendado)

Usa la API interna de APIRadar directamente via HTTP. Requiere sesion guardada.

```bash
# Descargar todos los leaks disponibles
python main.py --api

# Filtrar por proveedor
python main.py --api --provider openai

# Limitar cantidad de resultados
python main.py --api --limit 100

# Ordenar por mas antiguos primero
python main.py --api --sort-by oldest

# Filtrar por rango de tiempo
python main.py --api --time-range 30d

# Combinaciones
python main.py --api --provider anthropic --limit 200 --time-range 7d
python main.py --api --provider google --sort-by oldest --output google_leaks.json
```

Proveedores disponibles: `openai`, `anthropic`, `google`, `groq`, `deepseek`, `mistral`, `xai`, `cerebras`

Rangos de tiempo validos: `7d`, `30d`, `90d`

### Modo Scraper

Usa Playwright para navegar el sitio web y extraer datos del DOM.

```bash
# Modo con ventana visible (primera vez o debug)
python main.py

# Modo headless (sin ventana, requiere sesion guardada)
python main.py --headless

# Cargar mas leaks via scroll infinito
python main.py --headless --load-more

# Limitar la cantidad de scrolls
python main.py --headless --load-more --max-pages 50

# Limitar resultados totales
python main.py --headless --limit 100
```

### Node.js (fallback)

Version simplificada para debug:

```bash
node main.js
```

---

## Referencia de opciones

| Opcion | Tipo | Default | Descripcion |
|--------|------|---------|-------------|
| `--api` | flag | - | Usar modo API directo (sin navegador) |
| `--provider` | string | todos | Filtrar por proveedor de API |
| `--limit` | int | sin limite | Numero maximo de leaks a extraer |
| `--sort-by` | string | `newest` | Orden: `newest` o `oldest` |
| `--time-range` | string | todos | Rango de tiempo: `7d`, `30d`, `90d` |
| `--output` | string | auto | Nombre del archivo de salida |
| `--headless` | flag | false | Ejecutar sin ventana (solo scraper) |
| `--load-more` | flag | false | Scroll infinito para mas resultados (solo scraper) |
| `--max-pages` | int | sin limite | Limite de scrolls (solo scraper) |

---

## Formato de salida

Los datos se exportan como JSON en el directorio `data/`:

**Modo API** genera archivos `leaks_api_YYYYMMDD_HHMMSS.json`:

```json
[
  {
    "provider": "openai",
    "keyPreview": "sk-proj-...4f2a",
    "repoUrl": "https://github.com/usuario/repo",
    "filePath": "src/config.js",
    "owner": "usuario",
    "addedAt": "2026-02-13T18:30:00Z",
    "detectedAt": "2026-02-13T17:00:00Z",
    "fileUrl": "https://github.com/usuario/repo/blob/HEAD/src/config.js"
  }
]
```

**Modo Scraper** genera archivos `leaks_YYYYMMDD_HHMMSS.json`:

```json
[
  {
    "provider": "openai",
    "key_preview": "sk-proj-...4f2a",
    "repository": "usuario/repo",
    "owner": "usuario",
    "file_path": "src/config.js",
    "source_url": "https://github.com/usuario/repo/blob/.../src/config.js",
    "added_at": "2 hours ago",
    "detected_at": "3 hours ago",
    "extracted_at": "2026-02-13T19:00:00.123Z"
  }
]
```

---

## Estructura del proyecto

```
apileaks/
├── main.py              # Entry point Python (API + scraper)
├── main.js              # Entry point Node.js (fallback)
├── requirements.txt     # Dependencias Python
├── config/
│   └── settings.py      # Configuracion central (URLs, paths, env vars)
├── scraper/
│   ├── auth.py          # AuthManager — OAuth login, sesion
│   ├── apiradar.py      # APIRadarScraper — Playwright, CSS selectors
│   └── api_client.py    # APIRadarClient — HTTP directo a /api/leaks
├── session/             # Sesion OAuth guardada (gitignored)
├── data/                # Archivos JSON de salida (gitignored)
└── .env                 # Variables de entorno opcionales (gitignored)
```

---

## Configuracion

Variables de entorno opcionales (archivo `.env`):

```bash
HEADLESS=true    # Ejecutar sin ventana por defecto
TIMEOUT=30       # Timeout en segundos para navegacion
```

---

## Troubleshooting

### Error: "Executable doesn't exist"
```bash
playwright install chromium
```

### Error: "Failed to launch browser" (Linux sin display)
```bash
sudo apt install xvfb
xvfb-run python main.py
```

### Sesion expirada / login falla
```bash
rm session/apiradar_session.json
python main.py   # Login manual de nuevo
```

### Rate limit (error 429)
El modo API maneja automaticamente los errores 429 esperando el tiempo indicado por el servidor. Si ocurren frecuentemente, reduce la velocidad de extraccion.

---

## Notas

- **Responsabilidad:** Herramienta para fines educativos y de seguridad. No uses las credenciales expuestas.
- **Rate limiting:** APIRadar puede limitar peticiones. No abuses del servicio.
- **Privacidad:** Las sesiones se guardan localmente y estan excluidas del repositorio.

---

## Licencia

MIT License
