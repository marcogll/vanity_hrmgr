# Sistema de Control de Permisos, Vacaciones e Inasistencias

Plataforma web centralizada para la gestión de colaboradores, vacaciones, permisos e incidencias con integración directa a Telegram para aprobaciones administrativas en tiempo real.

---

# Características Principales

- Gestión de vacaciones basada en antigüedad.
- Control de permisos con validaciones automáticas.
- Registro administrativo de inasistencias.
- Integración con Telegram Bot.
- Dashboard multi-sucursal.
- Sistema de roles y permisos.
- Auditoría de movimientos y solicitudes.
- Arquitectura preparada para escalamiento.

---

# Objetivo

Automatizar los procesos operativos relacionados con recursos humanos y administración de personal, reduciendo tiempos de respuesta y centralizando la información en una sola plataforma.

---

# Roles del Sistema

| Rol | Funciones |
|---|---|
| Admin | Control total del sistema y aprobaciones |
| Manager | Gestión operativa por sucursal |
| User | Solicitud y consulta de permisos/vacaciones |

---

# Funcionalidades

## Vacaciones

- Cálculo automático por antigüedad.
- Renovación automática en aniversario laboral.
- Exclusión automática de días festivos.
- Validación de saldo disponible.

## Permisos

- Validación de máximo de días permitidos.
- Reglas de anticipación.
- Etiquetado automático de riesgos administrativos.

## Telegram Bot

- Notificaciones instantáneas.
- Aprobación/Rechazo inline.
- Comentarios administrativos sincronizados.

## Inasistencias

- Registro de faltas e incidencias.
- Clasificación por tipo.
- Historial administrativo.

---

# Stack Tecnológico

| Área | Tecnología |
|---|---|
| Backend | Python 3.11+ |
| Framework | Django |
| API | Django REST Framework |
| Base de Datos | PostgreSQL |
| Bot | python-telegram-bot |
| Queue/Tasks | Celery + Redis |
| Infraestructura | Docker |
| Frontend | Django Templates / React |

---

# Arquitectura General

```text
Frontend
   │
   ▼
Django API
   │
   ├── PostgreSQL
   ├── Redis
   ├── Celery Workers
   └── Telegram Bot
```

---

# Estructura del Proyecto

```text
project/
├── apps/
│   ├── employees/
│   ├── requests/
│   ├── absences/
│   ├── holidays/
│   └── telegram_bot/
├── config/
├── requirements/
├── docker/
├── scripts/
├── manage.py
└── README.md
```

---

# Variables de Entorno

```env
DEBUG=True

SECRET_KEY=your_secret_key

DB_NAME=app_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0

TELEGRAM_BOT_TOKEN=your_bot_token

ALLOWED_HOSTS=*
```

---

# Instalación Local

## 1. Clonar repositorio

```bash
git clone https://github.com/your-org/project.git
cd project
```

## 2. Crear entorno virtual

```bash
python -m venv venv
```

## 3. Activar entorno

### Linux/macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 5. Ejecutar migraciones

```bash
python manage.py migrate
```

## 6. Crear superusuario

```bash
python manage.py createsuperuser
```

## 7. Iniciar servidor

```bash
python manage.py runserver
```

---

# Docker

## Levantar servicios

```bash
docker compose up --build
```

## Ejecutar migraciones

```bash
docker compose exec web python manage.py migrate
```

## Crear superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

---

# Roadmap

## Fase 1

- Modelos ORM
- Sistema de usuarios
- Roles y permisos

## Fase 2

- Motor de solicitudes
- Validaciones automáticas
- Lógica de vacaciones

## Fase 3

- Integración Telegram
- Workflow de aprobaciones

## Fase 4

- Dashboard administrativo
- Calendario maestro

## Fase 5

- Reportes
- Exportaciones
- Métricas operativas

---

# Seguridad

- Roles RBAC.
- Validaciones server-side.
- Auditoría de acciones.
- Protección CSRF.
- JWT/Auth Session.
- Logs administrativos.

---

# Futuras Expansiones

- Multiempresa.
- Firma digital.
- Aplicación móvil.
- Integración biométrica.
- Nómina.
- Reportes PDF/Excel.
- Integración SAT/IMSS.

---

# Licencia

Uso privado y propietario.
Todos los derechos reservados.
