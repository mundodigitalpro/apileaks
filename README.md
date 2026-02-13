# API Leaks Scraper

Scraper para extraer datos de [APIRadar](https://apiradar.live) usando autenticación OAuth de Google.

## Estructura

```
apileaks/
├── config/           # Configuración
├── scraper/          # Módulos de scraping
├── data/             # Datos extraídos
├── main.py           # Entry point
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Uso

```bash
python main.py
```

Primera ejecución: abrirá navegador para login con Google (headless=False).
Las siguientes: usa sesión guardada (headless=True).
