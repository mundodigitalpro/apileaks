# Changelog

Todos los cambios notables en el proyecto APILeaks.

## [Unreleased]

### Próximos pasos
- [ ] Despliegue en VPS
- [ ] Primera autenticación en APIRadar
- [ ] Configuración de cron para ejecución automatizada
- [ ] Testing de extracción de datos real

---

## 2026-02-13

### Added
- **README.md completo** - Documentación del proyecto con instalación, uso, y troubleshooting
- **DEPLOYMENT_PLAN.md** - Plan detallado para despliegue en VPS (Ubuntu/Debian)
- **Estructura base del scraper**:
  - `main.js` - Entry point con CLI args (--headless, --limit, --output)
  - `scraper/auth.js` - Gestión de autenticación OAuth con persistencia de sesión
  - `scraper/apiradar.js` - Lógica de extracción de datos
  - `config/settings.js` - Configuración centralizada
- **package.json** - Dependencias (Playwright)
- **.gitignore** - Exclusiones para datos sensibles y node_modules
- **Documentación de memoria** - `memory/2026-02-13.md` con contexto del proyecto

### Changed
- Migración de **Python** a **Node.js** tras descubrir que pip no estaba disponible en el entorno
- Adaptación del scraper para usar Playwright en lugar de Selenium

### Descubierto
- **Playwright NO soporta Android** - Error: "Unsupported platform: android"
- APIRadar usa **Next.js/React** con CSR - requiere navegador real (no funciona con curl/http)
- El VPS será el entorno de despliegue final

### Infraestructura
- **GitHub**: Repo configurado con SSH key (`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMVzVke5B2wixKH09dalYkfp34y3vNBRXrXaY3prGMrM`)
- **SSH key generada** para acceso al VPS (pendiente de configurar)
- **old-phone** (10.17.4.17:8022) no accesible - timeout en conexión

### Notas técnicas
- Entorno actual: Android/Termux con Node.js v24.13.0
- Sin acceso a navegadores automatizados en este entorno
- Solución: despliegue en VPS con Ubuntu/Debian + Chromium

---

## Estructura actual del repositorio

```
apileaks/
├── README.md                 # Documentación principal
├── DEPLOYMENT_PLAN.md        # Guía de despliegue VPS
├── CHANGELOG.md             # Este archivo
├── package.json             # Dependencias Node.js
├── .gitignore               # Exclusiones Git
├── main.js                  # Entry point
├── config/
│   └── settings.js          # Configuración
├── scraper/
│   ├── auth.js              # Autenticación OAuth
│   ├── apiradar.js          # Lógica de scraping
│   └── __init__.py          # (obsoleto - Python)
├── data/                    # Datos extraídos (gitignored)
└── session/                 # Sesiones guardadas (gitignored)
```

---

## Commits

- `0bede4e` - Update README with complete documentation
- `9cdcb09` - Add deployment plan for VPS
- `162039f` - Update README: documentar limitaciones de entorno
- `3293969` - Initial commit: APIRadar scraper con auth OAuth

---

## Issues conocidos

1. **No ejecutable en Android** - Requiere VPS o PC con entorno gráfico
2. **Selectores CSS no validados** - Necesitan ajuste tras ver HTML real de APIRadar
3. **old-phone no accesible** - Posible solución alternativa de hardware

---

## Recursos

- **Repositorio**: https://github.com/mundodigitalpro/apileaks
- **Target**: https://apiradar.live
- **Stack**: Node.js 20+, Playwright, Chromium
