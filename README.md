<p align="center">
  <img src="https://raw.githubusercontent.com/marcogll/mg_data_storage/refs/heads/main/soul23/logo/soul23_logo.svg" width="110" alt="Soul23">
</p>

<h1 align="center">HR Manager</h1>

<p align="center">
  Sistema de Control de Permisos, Vacaciones e Inasistencias
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python_3.11+-3a3a3a?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Django_6.0-3a3a3a?style=flat-square&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-3a3a3a?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-3a3a3a?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Telegram-3a3a3a?style=flat-square&logo=telegram&logoColor=white" alt="Telegram">
</p>

---

# Estado del Proyecto

| Fase | Estado |
|------|--------|
| Fase 1 - Base de Datos y Modelos | ✅ Completado |
| Fase 2 - Motor de Solicitudes (API REST) | ✅ Completado |
| Fase 3 - Telegram Bot + API Key Auth | ✅ Completado |
| Fase 4 - Dashboard Web | ✅ Completado |
| Fase 5 - Inasistencias y Reportes | ✅ Completado |

---

# Características Principales

- Gestión de vacaciones basada en antigüedad (LFT Art. 76)
- Control de permisos con validaciones automáticas
- Registro administrativo de inasistencias
- Integración con Telegram Bot para aprobaciones
- Dashboard web multi-sucursal con Bootstrap
- Sistema de roles: Admin, Manager, User
- Autenticación JWT + API Key + Sesión
- Auditoría completa de movimientos
- API REST con Django REST Framework

---

# Roles del Sistema

| Rol | Funciones |
|---|---|
| Admin | Control total, aprobaciones, reportes, configuración |
| Manager | Gestión operativa por sucursal asignada |
| User | Solicitud y consulta de permisos/vacaciones |

---

# Autenticación

El sistema soporta tres métodos de autenticación:

| Método | Uso |
|---|---|
| JWT Bearer | APIs REST (acceso con username/password) |
| API Key | Integraciones machine-to-machine |
| Sesión | Dashboard web |

## Generar API Key

```bash
POST /api/users/generate_api_key/
Authorization: Bearer <jwt_token>

# Respuesta:
{ "api_key": "sk_..." }
```

## Usar API Key

```bash
GET /api/requests/
Authorization: ApiKey <tu_api_key>
```

---

# API Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/users/` | GET, POST | Gestión de usuarios |
| `/api/users/me/` | GET | Datos del usuario actual |
| `/api/users/generate_api_key/` | POST | Generar API Key |
| `/api/users/revoke_api_key/` | DELETE | Revocar API Key |
| `/api/branches/` | GET | Sucursales |
| `/api/branches/{id}/empleados/` | GET | Empleados de sucursal |
| `/api/employees/` | GET, POST | Empleados |
| `/api/employees/me/` | GET | Datos propios |
| `/api/requests/` | GET, POST | Solicitudes |
| `/api/requests/{id}/aprobar/` | POST | Aprobar solicitud |
| `/api/requests/{id}/rechazar/` | POST | Rechazar solicitud |
| `/api/absences/` | GET, POST | Inasistencias |

---

# Stack Tecnológico

| Área | Tecnología |
|---|---|
| Backend | Python 3.14 / Django 6.0 |
| API | Django REST Framework + SimpleJWT |
| Base de Datos | PostgreSQL 15 |
| Cache/Queue | Redis 7 + Celery |
| Bot | python-telegram-bot 22 |
| Web | Django Templates + Bootstrap 5 + FullCalendar |
| Infraestructura | Docker + Docker Compose |

---

# Instalación Rápida

```bash
# 1. Clonar y configurar
git clone https://github.com/marcogll/vanity_hrmgr.git
cd vanity_hrmgr
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Migrar y seed
python manage.py migrate
python manage.py seed_holidays
python manage.py createsuperuser

# 3. Ejecutar
python manage.py runserver
```

---

# Docker

```bash
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_holidays
docker compose exec web python manage.py createsuperuser
```

---

# Estructura del Proyecto

```text
vanity_hrmgr/
├── config/              # Django settings
├── core/                # Catálogos y URLs API
├── employees/           # Users, Branches, Employees
├── holidays/            # Feriados mexicanos
├── requests/            # Solicitudes vacaciones/permisos
├── absences/            # Inasistencias
├── telegram_bot/        # Bot de Telegram
├── templates/           # Templates web
├── static/              # Archivos estáticos
├── manage.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

# Variables de Entorno

Ver `.env.example` para referencia completa.

---

# Licencia

Uso privado y propietario. Todos los derechos reservados.