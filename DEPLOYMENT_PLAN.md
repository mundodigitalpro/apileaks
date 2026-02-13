# Plan de Despliegue - APILeaks en VPS

## Resumen
Despliegue del scraper APIRadar en VPS para ejecución automatizada y persistente.

---

## Fase 1: Preparación del VPS

### 1.1 Requisitos del servidor
- **OS:** Ubuntu 22.04 LTS o Debian 12 (recomendado)
- **RAM:** Mínimo 2GB (4GB recomendado para Chrome)
- **Disco:** 10GB mínimo
- **Conexión:** Salida a internet para acceder a APIRadar

### 1.2 Instalación de dependencias base
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verificar instalación
node --version  # v20.x.x
npm --version   # 10.x.x

# Instalar dependencias para Playwright/Chromium
sudo apt install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxshmfence1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1
```

---

## Fase 2: Despliegue de la aplicación

### 2.1 Clonar repositorio
```bash
cd /opt
sudo git clone git@github.com:mundodigitalpro/apileaks.git
sudo chown -R $USER:$USER apileaks
cd apileaks
```

### 2.2 Instalar dependencias
```bash
npm install
npx playwright install chromium
```

### 2.3 Primera ejecución (login manual)
```bash
# Modo interactivo para autenticación
node main.js
```
> **Nota:** Requiere conexión SSH con forwarding de X11 o usar `xvfb` para entorno virtual.

Alternativa headless-first:
```bash
# Instalar display virtual
sudo apt install -y xvfb

# Ejecutar con display virtual
xvfb-run -a node main.js
```

---

## Fase 3: Configuración de ejecución automatizada

### 3.1 Script de ejecución
Crear `/opt/apileaks/run.sh`:
```bash
#!/bin/bash
cd /opt/apileaks
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 2
node main.js --headless
```

```bash
chmod +x /opt/apileaks/run.sh
```

### 3.2 Servicio systemd
Crear `/etc/systemd/system/apileaks.service`:
```ini
[Unit]
Description=APILeaks Scraper
After=network.target

[Service]
Type=oneshot
User=apileaks
WorkingDirectory=/opt/apileaks
ExecStart=/usr/bin/xvfb-run -a /usr/bin/node main.js --headless
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
```

```bash
# Crear usuario dedicado
sudo useradd -r -s /bin/false apileaks
sudo chown -R apileaks:apileaks /opt/apileaks

# Habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable apileaks
```

### 3.3 Cron para ejecución periódica
```bash
# Editar crontab
sudo crontab -e

# Ejecutar cada 6 horas
0 */6 * * * /opt/apileaks/run.sh >> /var/log/apileaks.log 2>&1
```

---

## Fase 4: Gestión de datos

### 4.1 Estructura de salida
```
/opt/apileaks/data/
├── leaks_20260213_120000.json
├── leaks_20260213_180000.json
└── archive/
    └── ...
```

### 4.2 Backup automático (opcional)
```bash
# Script de backup a S3/otro servidor
#!/bin/bash
aws s3 sync /opt/apileaks/data/ s3://tu-bucket/apileaks/
```

---

## Fase 5: Monitorización y logs

### 5.1 Logs
```bash
# Ver logs en tiempo real
tail -f /var/log/apileaks.log

# Logs de systemd
sudo journalctl -u apileaks -f
```

### 5.2 Health check simple
```bash
# Crear script de verificación
cat > /opt/apileaks/health.sh << 'EOF'
#!/bin/bash
if [ $(find /opt/apileaks/data -name "leaks_*.json" -mtime -1 | wc -l) -eq 0 ]; then
    echo "ERROR: No hay datos recientes"
    exit 1
fi
echo "OK"
EOF
chmod +x /opt/apileaks/health.sh
```

---

## Fase 6: Seguridad

### 6.1 Firewall (UFW)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

### 6.2 Variables de entorno sensibles
```bash
# Crear archivo de entorno
sudo touch /opt/apileaks/.env
sudo chmod 600 /opt/apileaks/.env
sudo chown apileaks:apileaks /opt/apileaks/.env
```

---

## Comandos rápidos de referencia

| Acción | Comando |
|--------|---------|
| Ejecutar manualmente | `cd /opt/apileaks && node main.js` |
| Ver estado servicio | `sudo systemctl status apileaks` |
| Reiniciar servicio | `sudo systemctl restart apileaks` |
| Ver logs | `tail -f /var/log/apileaks.log` |
| Actualizar código | `cd /opt/apileaks && git pull && npm install` |

---

## Troubleshooting

### Error: "browserType.launch: Executable doesn't exist"
```bash
npx playwright install chromium
```

### Error: "Cannot start X display"
```bash
sudo apt install xvfb
export DISPLAY=:99
Xvfb :99 &
```

### Sesión expirada
Borrar archivo de sesión y re-autenticar:
```bash
rm /opt/apileaks/session/apiradar_session.json
node main.js  # Login manual de nuevo
```

---

## Próximos pasos

1. [ ] Proporcionar credenciales SSH del VPS
2. [ ] Ejecutar Fase 1 y 2
3. [ ] Realizar primera autenticación en APIRadar
4. [ ] Configurar cron para ejecución automática
5. [ ] Verificar funcionamiento durante 24h

---

*Documento creado: 2026-02-13*
