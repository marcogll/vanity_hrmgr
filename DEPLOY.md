# Guía de Despliegue - HR Manager

## Requisitos del Sistema

- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+
- Redis 7+
- 2GB RAM mínimo
- 10GB disco mínimo

## Despliegue con Docker Compose

### 1. Clonar repositorio

```bash
git clone https://github.com/marcogll/vanity_hrmgr.git
cd vanity_hrmgr
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con valores de producción
```

### 3. Configurar SSL (opcional)

```bash
mkdir -p nginx/ssl
# Copiar certificados SSL a nginx/ssl/
```

### 4. Levantar servicios

```bash
docker compose up -d --build
```

### 5. Ejecutar migraciones

```bash
docker compose exec web python manage.py migrate
```

### 6. Crear superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

### 7. Cargar feriados

```bash
docker compose exec web python manage.py seed_holidays
```

### 8. Verificar servicios

```bash
docker compose ps
curl http://localhost:8000/admin/
```

## Configuración de Nginx

### nginx.conf

```nginx
upstream hrmgr {
    server web:8000;
}

server {
    listen 80;
    server_name hrmgr.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name hrmgr.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://hrmgr;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configuración de Celery

### celery.service (systemd)

```ini
[Unit]
Description=HR Manager Celery Worker
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/hrmgr
EnvironmentFile=/opt/hrmgr/.env
ExecStart=/opt/hrmgr/venv/bin/celery -A config worker -l info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### celery-beat.service (tareas programadas)

```ini
[Unit]
Description=HR Manager Celery Beat
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/hrmgr
EnvironmentFile=/opt/hrmgr/.env
ExecStart=/opt/hrmgr/venv/bin/celery -A config beat -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

## Backups de PostgreSQL

### Script de backup

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/hrmgr"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker compose exec db pg_dump -U postgres hrmgr_db > $BACKUP_DIR/hrmgr_$DATE.sql

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

### Cron job (diario a las 2am)

```bash
0 2 * * * /opt/hrmgr/scripts/backup.sh
```

### Restaurar backup

```bash
docker compose exec -T db psql -U postgres hrmgr_db < backup.sql
```

## Monitoreo

### Sentry

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

### Health Check

```bash
curl -f http://localhost:8000/admin/ || exit 1
```

## Variables de Entorno de Producción

```env
DEBUG=False
SECRET_KEY=<generar_con_django_get_random_secret_key>
ALLOWED_HOSTS=hrmgr.example.com,127.0.0.1

POSTGRES_DB=hrmgr_db
POSTGRES_USER=hrmgr_user
POSTGRES_PASSWORD=<contraseña_segura>
POSTGRES_HOST=db
POSTGRES_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_ADMIN_ID=<admin_chat_id>

SENTRY_DSN=<sentry_dsn>
```

## Comandos Útiles

```bash
# Ver logs
docker compose logs -f web
docker compose logs -f celery

# Reiniciar servicios
docker compose restart web celery

# Ejecutar tests
docker compose exec web python manage.py test

# Abrir shell
docker compose exec web python manage.py shell

# Recopilar archivos estáticos
docker compose exec web python manage.py collectstatic --noinput
```