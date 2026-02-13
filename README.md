# APIRadar Scraper

## El problema
APIRadar es una app React (Next.js) que carga datos dinámicamente. Necesita navegador real con JavaScript.

## Solución 1: Ejecutar en máquina con navegador

### Setup
```bash
# En tu PC/Mac/Linux con Node.js
npm install
npx playwright install chromium
```

### Uso
```bash
# Primera vez (login manual)
node main.js

# Luego (automatizado)
node main.js --headless
```

## Solución 2: SSH al old-phone
Si el old-phone (10.17.4.17) tiene entorno gráfico o puede correr browsers headless:

```bash
ssh -p 8022 u_a101@10.17.4.17
# Instalar node + playwright allí
```

## Solución 3: API alternativa
Revisar si APIRadar expone API REST pública. Probar:
- https://apiradar.live/api/leaks
- https://apiradar.live/api/explore
- Inspeccionar Network tab en DevTools

## Estado actual
- ✅ Código listo (Node.js + Playwright)
- ❌ No corre en Android/Termux (Playwright no soporta android)
- ⏳ Necesita entorno Linux/macOS/Windows

## Next steps
1. Probar en old-phone vía SSH
2. O ejecutar en PC local con `git clone`
