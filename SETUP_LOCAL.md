# Setup Local - Autenticación OAuth

Guía para hacer el login en local y transferir la sesión al VPS.

## Objetivo

El scraper necesita autenticarse con Google OAuth una vez. Al no tener pantalla
gráfica el VPS, se hace el login en local y se copia la sesión.

---

## Paso 1 - Clonar e instalar

```bash
git clone https://github.com/mundodigitalpro/apileaks.git
cd apileaks
npm install
npx playwright install chromium
```

## Paso 2 - Login con Google

```bash
node main.js
```

Se abrirá Chrome automáticamente:

1. Haz clic en **"Sign in with Google"**
2. Completa el login con tu cuenta de Google
3. Espera a que cargue el dashboard de APIRadar
4. Vuelve a la terminal y pulsa **ENTER**

La sesión se guardará en `session/apiradar_session.json`.

## Paso 3 - Copiar sesión al VPS

```bash
# Crear directorio si no existe
ssh josejordan@<IP-VPS> "mkdir -p ~/apps/apileaks/session"

# Copiar sesión
scp session/apiradar_session.json josejordan@<IP-VPS>:~/apps/apileaks/session/apiradar_session.json
```

## Paso 4 - Verificar en el VPS

```bash
ssh josejordan@<IP-VPS>
cd ~/apps/apileaks
node main.js --headless
```

---

## Renovar sesión expirada

Si la sesión caduca, repetir desde el Paso 2:

```bash
# En local
rm session/apiradar_session.json
node main.js
# ... hacer login de nuevo ...
scp session/apiradar_session.json josejordan@<IP-VPS>:~/apps/apileaks/session/apiradar_session.json
```

---

## Requisitos

- Node.js 20+
- npm
- Acceso SSH al VPS
