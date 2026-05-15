# AGENTS.md - Definición de Agentes para el Proyecto

Este documento define los agentes especializados y roles dentro del sistema de desarrollo del proyecto HR Manager.

---

## Agentes del Sistema (Roles en la Aplicación)

### Admin

**Descripción:** Usuario con acceso total al sistema.

**Responsabilidades:**
- Aprobación y rechazo de solicitudes de vacaciones y permisos
- Gestión de catálogos (sucursales, empleados, feriados)
- Vista de todas las sucursales
- Registro de inasistencias
- Configuración del sistema
- Generación de reportes

**Permisos:**
- CRUD completo en todos los módulos
- Acceso a panel de auditoría
- Gestión de usuarios y roles

**Comandos Telegram:**
- Recibe notificaciones de nuevas solicitudes
- Aprueba/Rechaza desde botones inline

---

### Manager

**Descripción:** Usuario responsable de una o más sucursales.

**Responsabilidades:**
- Vista exclusiva de sus sucursales asignadas
- Búsqueda de empleados en sus sucursales
- Registro de inasistencias
- Aprobación nivel 1 (si aplica)

**Permisos:**
- Lectura de empleados de sus sucursales
- Escritura en módulo de inasistencias
- Vista de dashboard de su sucursal

**Acceso Dashboard:**
- Solo ve empleados de sus sucursales asignadas
- Puede filtrar calendario por sucursal

---

### User (Colaborador)

**Descripción:** Empleado que solicita vacaciones/permisos.

**Responsabilidades:**
- Solicitar vacaciones y permisos
- Consultar saldo de días disponibles
- Ver estatus de solicitudes
- Consultar historial personal

**Permisos:**
- Solo lectura de sus propios datos
- Crear solicitudes propias
- Cancelar solicitudes pendientes

**Acceso Dashboard:**
- Panel de transparencia personal
- Formulario de solicitudes
- Historial de movimientos

---

## Agentes de Desarrollo

### Database Agent

**Responsabilidades:**
- Diseño y creación de modelos ORM
- Migraciones de base de datos
- Optimización de queries
- Gestión deseeds y datos de prueba

**Herramientas:**
- Django ORM
- PostgreSQL
- SQLAlchemy (si aplica)

**Tareas relacionadas:**
- Fase 1.2 - Modelos Employees
- Fase 1.3 - Modelos Holidays
- Fase 1.4 - Modelos Requests
- Fase 1.5 - Modelos Absences
- Fase 1.6 - Catálogos

---

### Backend Agent

**Responsabilidades:**
- Desarrollo de lógica de negocio
- Implementación de reglas de validación
- Creación de APIs REST
- Integración con servicios externos

**Herramientas:**
- Django
- Django REST Framework
- Celery + Redis
- Python 3.11+

**Tareas relacionadas:**
- Fase 2 - Motor de Solicitudes
- Validaciones LFT Art. 76
- Reglas de permisos mercantiles

---

### Telegram Bot Agent

**Responsabilidades:**
- Implementación del bot de Telegram
- Manejo de webhooks y callbacks
- Integración con sistema de solicitudes
- Envío de notificaciones

**Herramientas:**
- python-telegram-bot
- Celery
- Redis

**Tareas relacionadas:**
- Fase 3 - Telegram Bot
- Integración con sistema de aprobación

---

### Frontend Agent

**Responsabilidades:**
- Desarrollo de interfaces de usuario
- Implementación de dashboards
- Creación de formularios
- Integración con API REST

**Herramientas:**
- Django Templates
- HTMX (opcional)
- JavaScript vanilla
- FullCalendar
- Bootstrap/Tailwind

**Tareas relacionadas:**
- Fase 4 - Dashboard Web
- Todas las vistas de usuario

---

### DevOps Agent

**Responsabilidades:**
- Configuración de Docker
- Despliegue de servicios
- Configuración de nginx
- Gestión de certificados
- Backups y monitoreo

**Herramientas:**
- Docker
- Docker Compose
- Nginx
- Gunicorn
- Celery

**Tareas relacionadas:**
- Testing
- Despliegue
- Seguridad

---

### QA Agent

**Responsabilidades:**
- Creación de tests unitarios
- Tests de integración
- Testing de regresión
- Validación de flujos de usuario

**Herramientas:**
- pytest
- Coverage
- Selenium (si aplica)

**Tareas relacionadas:**
- Testing en todas las fases
- Validaciones

---

## Flujo de Trabajo

```
1. Nueva Solicitud (User)
       ↓
2. Validación Automática (Backend Agent)
       ↓
3. Notificación a Admin (Telegram Bot Agent)
       ↓
4. Aprobación/Rechazo (Admin via Telegram)
       ↓
5. Actualización de Estatus (Backend Agent)
       ↓
6. Notificación al Usuario (Telegram Bot Agent)
       ↓
7. Registro en Dashboard (Frontend Agent)
```

---

## Comunicación entre Agentes

| De | A | Mensaje |
|----|---|----------|
| User | Backend | Nueva solicitud |
| Backend | Telegram Bot | Notificación de solicitud |
| Telegram Bot | Backend | Aprobación/Rechazo |
| Backend | User | Actualización de estatus |
| Manager | Backend | Registro de inasistencia |
| Admin | Backend | Configuración del sistema |

---

## Configuración de Agentes para opencode

Para ejecutar tareas específicas, usar el agente apropiado:

```bash
# Modelos y base de datos
opencode --agent database

# API y lógica de negocio
opencode --agent backend

# Bot de Telegram
opencode --agent telegram-bot

# Interfaces web
opencode --agent frontend

# Testing
opencode --agent qa
```