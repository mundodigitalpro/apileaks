# 🔍 APILeaks

Scraper automatizado para extraer datos de fugas de API keys desde [APIRadar](https://apiradar.live).

[![Node.js](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-blue.svg)](https://playwright.dev/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## 📋 Descripción

APIRadar es un servicio que detecta fugas de claves API en repositorios públicos de GitHub en tiempo real. Este proyecto automatiza la extracción de esos datos para análisis, alertas o integraciones.

### Características

- ✅ Autenticación OAuth con Google (login automático)
- ✅ Persistencia de sesión (no requiere login cada vez)
- ✅ Extracción de datos estructurados (provider, repo, timestamp, etc.)
- ✅ Exportación a JSON
- ✅ Ejecución headless (sin interfaz gráfica)
- ✅ Automatizable con cron/systemd

---

## 🚀 Requisitos

- **Node.js** 20.x o superior
- **Chromium/Chrome** (instalado automáticamente por Playwright)
- **Sistema operativo:** Linux, macOS, o Windows

> ⚠️ **Nota importante:** Este proyecto **NO** funciona en Android/Termux directamente porque Playwright requiere un entorno de escritorio completo. Ver [opciones de despliegue](#despliegue).

---

## 📦 Instalación

### 1. Clonar repositorio

```bash
git clone git@github.com:mundodigitalpro/apileaks.git
cd apileaks
```

### 2. Instalar dependencias

```bash
npm install
```

### 3. Instalar navegador

```bash
npx playwright install chromium
```

---

## 🎯 Uso

### Primera ejecución (autenticación)

La primera vez necesitas iniciar sesión manualmente con tu cuenta de Google:

```bash
node main.js
```

Esto abrirá una ventana del navegador. Sigue estos pasos:
1. Haz clic en **"Sign in with Google"**
2. Ingresa tus credenciales
3. Espera a que cargue el dashboard de APIRadar
4. Presiona **ENTER** en la terminal

La sesión se guardará automáticamente para futuras ejecuciones.

### Ejecuciones posteriores (automático)

```bash
# Modo headless (sin ventana)
node main.js --headless

# Limitar número de resultados
node main.js --limit 50

# Especificar archivo de salida
node main.js --output mis_leaks.json
```

### Opciones disponibles

| Opción | Descripción |
|--------|-------------|
| `--headless` | Ejecutar sin interfaz gráfica |
| `--limit N` | Limitar a N resultados |
| `--output FILE` | Nombre del archivo de salida |
| `--load-more` | Cargar más resultados automáticamente |

---

## 📁 Estructura del proyecto

```
apileaks/
├── main.js              # Entry point
├── config/
│   └── settings.js      # Configuración
├── scraper/
│   ├── auth.js          # Gestión de autenticación
│   └── apiradar.js      # Lógica de scraping
├── data/                # Datos extraídos (gitignored)
├── session/             # Sesiones guardadas (gitignored)
├── package.json
└── README.md
```

---

## 🖥️ Despliegue

### Opción 1: VPS (Recomendado)

Para ejecución 24/7 y automatización con cron:

Ver [`DEPLOYMENT_PLAN.md`](DEPLOYMENT_PLAN.md) para guía completa de despliegue en VPS.

**Resumen rápido:**
```bash
# En tu VPS Ubuntu/Debian
git clone git@github.com:mundodigitalpro/apileaks.git
cd apileaks
npm install
npx playwright install chromium
xvfb-run node main.js  # Primera vez (login)
```

### Opción 2: PC Local

Ejecutar manualmente cuando necesites datos actualizados.

### Opción 3: Docker (Próximamente)

```bash
docker build -t apileaks .
docker run -v $(pwd)/data:/app/data apileaks
```

---

## 📊 Formato de salida

Los datos se exportan en JSON:

```json
[
  {
    "provider": "OpenAI",
    "key_preview": "sk-...4f2a",
    "repository": "usuario/repo-ejemplo",
    "file_path": "src/config.js",
    "detected_at": "2026-02-13T18:30:00Z",
    "source_url": "https://github.com/.../commit/abc123",
    "extracted_at": "2026-02-13T19:00:00.123Z"
  }
]
```

---

## ⚙️ Configuración

Variables de entorno opcionales:

```bash
# .env
HEADLESS=true
TIMEOUT=30
```

---

## 🛠️ Troubleshooting

### Error: "Executable doesn't exist"
```bash
npx playwright install chromium
```

### Error: "Failed to launch browser"
En Linux sin display gráfico:
```bash
sudo apt install xvfb
xvfb-run node main.js
```

### Sesión expirada
```bash
rm session/apiradar_session.json
node main.js  # Volver a autenticar
```

---

## 📝 Notas

- **Responsabilidad:** Este tool es para fines educativos y de seguridad. No uses las credenciales expuestas.
- **Rate limiting:** APIRadar puede tener límites de peticiones. No abuses del servicio.
- **Privacidad:** Las sesiones se guardan localmente en `session/apiradar_session.json`.

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

## 🔗 Enlaces

- [APIRadar](https://apiradar.live)
- [Playwright Docs](https://playwright.dev/)
- [Reportar issue](https://github.com/mundodigitalpro/apileaks/issues)

---

*Creado con 🤖 por BotdropBot*
