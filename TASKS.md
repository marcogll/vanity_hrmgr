# Plan de Desarrollo - Sistema de Control de Permisos, Vacaciones e Inasistencias

## Fases del Proyecto

El proyecto se divide en 5 fases principales, cada una con tareas específicas que deben completarse en orden.

---

## Fase 1 — Base de Datos y Modelos

### 1.1 Configuración del Proyecto

- [x] 1.1.1 Inicializar proyecto Django con estructura de apps
- [x] 1.1.2 Configurar settings.py para PostgreSQL, Redis y logging
- [x] 1.1.3 Configurar Docker y Docker Compose
- [x] 1.1.4 Configurar variables de entorno (.env.example)
- [x] 1.1.5 Configurar pytest y coverage para testing
- [x] 1.1.6 Crear requirements.txt con todas las dependencias

### 1.2 Modelos ORM - Employees App

- [x] 1.2.1 Crear modelo Branch (sucursal) con campos: name, address, active
- [x] 1.2.2 Crear modelo Employee con campos:
  - user (OneToOne con Django User)
  - employee_number (único)
  - curp, rfc
  - tipo_contrato (choices: Laboral/Mercantil)
  - fecha_ingreso
  - saldo_vacaciones (Float)
  - branch (FK)
  - manager (FK)
  - status (choices: Activo/Baja/Suspendido)
- [x] 1.2.3 Crear modelo EmployeeAudit para auditoría de cambios
- [x] 1.2.4 Implementar señales para actualizar saldo en aniversario
- [x] 1.2.5 Crear migraciones y ejecutar

### 1.3 Modelos ORM - Holidays App

- [x] 1.3.1 Crear modelo Holiday con campos: fecha, descripcion, activo
- [x] 1.3.2 Crear script de seed para feriados mexicanos estándar
- [x] 1.3.3 Implementar método para verificar día festivo
- [x] 1.3.4 Implementar método para calcular días hábiles entre fechas

### 1.4 Modelos ORM - Requests App

- [x] 1.4.1 Crear modelo Request (vacaciones/permisos) con campos:
  - tipo (choices: Vacación/Permiso)
  - fecha_inicio, fecha_fin
  - estatus (choices: Pendiente/Aprobado/Rechazado)
  - observaciones_sistema
  - comentario_admin
  - empleado (FK)
  - created_at, updated_at
- [x] 1.4.2 Crear modelo RequestComment para historial de comentarios

### 1.5 Modelos ORM - Absences App

- [x] 1.5.1 Crear modelo Absence con campos:
  - empleado (FK)
  - fecha
  - sucursal (FK)
  - tipo (choices: Injustificada/Enfermedad/Suspensión/Retardo/Permiso sin goce/Otro)
  - motivo
  - registrado_por (FK)
  - created_at
- [x] 1.5.2 Crear modelo AbsenceAudit para auditoría

### 1.6 Modelos ORM - Catálogos

- [x] 1.6.1 Crear modelo Configuration para configuraciones globales
- [x] 1.6.2 Crear modelo NotificationLog para logs de Telegram

---

## Fase 2 — Motor de Solicitudes

### 2.1 Lógica de Vacaciones (LFT Art. 76)

- [x] 2.1.1 Implementar cálculo de antigüedad por fecha de ingreso
- [x] 2.1.2 Implementar tabla de días por antigüedad:
  - 1 año: 6 días
  - 2 años: 8 días
  - 3 años: 10 días
  - 4 años: 12 días
  - 5-9 años: 14 días
  - 10-14 años: 16 días
  - 15-19 años: 18 días
  - 20+ años: 20 días
- [x] 2.1.3 Implementar renovación automática en fecha de aniversario
- [x] 2.1.4 Implementar exclusión de días festivos del descuento
- [x] 2.1.5 Validar que saldo no quede negativo

### 2.2 Lógica de Permisos

- [x] 2.2.1 Validar máximo de 3 días hábiles
- [x] 2.2.2 Validar anticipación de 24-48 horas
- [x] 2.2.3 Implementar etiqueta "FUERA DE CONDICIONES / RIESGO DE ABANDONO"
- [x] 2.2.4 Permitir envío con bandera cuando rompe reglas
- [x] 2.2.5 Validar que no haya traslapes de solicitudes

### 2.3 API REST - Endpoints

- [x] 2.3.1 Configurar Django REST Framework
- [x] 2.3.2 Crear endpoints para Solicitudes:
  - GET /api/requests/ (listar del usuario)
  - POST /api/requests/ (crear solicitud)
  - GET /api/requests/{id}/ (detalle)
  - PATCH /api/requests/{id}/ (actualizar si está pendiente)
  - DELETE /api/requests/{id}/ (cancelar si está pendiente)
- [x] 2.3.3 Crear endpoints para Empleados:
  - GET /api/employees/ (listar - solo Admin/Manager)
  - GET /api/employees/{id}/ (detalle)
  - GET /api/employees/me/ (datos propios)
- [x] 2.3.4 Crear endpoints para Sucursales:
  - GET /api/branches/
  - GET /api/branches/{id}/employees/
- [x] 2.3.5 Crear endpoint de dashboard para Admin/Manager

### 2.4 Serializer y Validaciones

- [x] 2.4.1 Crear RequestSerializer con validaciones
- [x] 2.4.2 Crear EmployeeSerializer
- [x] 2.4.3 Crear AbsenceSerializer
- [x] 2.4.4 Implementar validaciones personalizadas en serializers

### 2.5 Permisos y Autenticación

- [x] 2.5.1 Configurar Django Auth
- [x] 2.5.2 Crear CustomPermission classes para RBAC
- [x] 2.5.3 Implementar JWT authentication (djangorestframework-simplejwt)
- [x] 2.5.4 Configurar autenticación por sesión para templates
- [x] 2.5.5 Implementar API Key authentication

---

## Fase 3 — Telegram Bot

### 3.1 Configuración del Bot

- [x] 3.1.1 Crear app TelegramBot con python-telegram-bot
- [x] 3.1.2 Configurar webhook o polling mode
- [x] 3.1.3 Implementar manejo de comandos /start, /help
- [x] 3.1.4 Crear gestión de estados del conversation handler

### 3.2 Notificaciones

- [x] 3.2.1 Implementar callback para nueva solicitud
- [x] 3.2.2 Enviar notificación con detalles de solicitud
- [x] 3.2.3 Crear Inline Keyboard con botones [Aprobar] [Rechazar]
- [x] 3.2.4 Implementar manejo de callbacks para aprobación/rechazo
- [x] 3.2.5 Solicitar comentario opcional tras acción
- [x] 3.2.6 Guardar comentario en Request y actualizar estatus

### 3.3 Integración con Sistema

- [x] 3.3.1 Crear función para obtener admin_id de configuración
- [x] 3.3.2 Crear función para enviar notificación asíncrona
- [x] 3.3.3 Integrar Celery para tareas asíncronas del bot
- [x] 3.3.4 Implementar respuesta automática al colaborador

### 3.4 Pruebas del Bot

- [x] 3.4.1 Probar notificaciones en entorno local
- [x] 3.4.2 Probar flujo completo de aprobación
- [x] 3.4.3 Probar manejo de errores y reintentos
- [x] 3.4.4 Configurar logging de bot

---

## Fase 4 — Dashboard Web

### 4.1 Templates Base

- [x] 4.1.1 Crear base.html con estructura responsive
- [x] 4.1.2 Implementar navbar con menú según rol
- [x] 4.1.3 Crear sistema de mensajes flash
- [x] 4.1.4 Configurar static files (CSS, JS, imágenes)

### 4.2 Vistas de Empleado

- [x] 4.2.1 Crear vista de perfil del empleado
- [x] 4.2.2 Crear formulario de solicitud de vacaciones
- [x] 4.2.3 Crear formulario de solicitud de permiso
- [x] 4.2.4 Crear historial de solicitudes del empleado
- [x] 4.2.5 Mostrar saldo de vacaciones y próxima renovación
- [x] 4.2.6 Mostrar comentarios administrativos

### 4.3 Dashboard Admin/Manager

- [x] 4.3.1 Crear calendario maestro con FullCalendar
- [x] 4.3.2 Implementar filtros por sucursal
- [x] 4.3.3 Implementar filtros por tipo de ausencia
- [x] 4.3.4 Mostrar solicitudes pendientes con colores
- [x] 4.3.5 Crear panel de aprobación rápida

### 4.4 Búsqueda de Socios

- [x] 4.4.1 Crear formulario de búsqueda global
- [x] 4.4.2 Buscar por nombre, número de empleado, CURP
- [x] 4.4.3 Filtrar por estatus laboral y sucursal
- [ ] 4.4.4 Mostrar resultados en tabla paginada

### 4.5 Panel de Transparencia

- [x] 4.5.1 Mostrar historial completo de solicitudes
- [x] 4.5.2 Mostrar comentarios administrativos
- [x] 4.5.3 Mostrar estatus actual y saldo disponible
- [x] 4.5.4 Mostrar próxima fecha de renovación

---

## Fase 5 — Inasistencias y Reportes

### 5.1 Registro de Inasistencias

- [x] 5.1.1 Crear formulario de registro de falta
- [x] 5.1.2 Validar que solo Manager/Admin puedan registrar
- [x] 5.1.3 Implementar selección de empleado por sucursal
- [x] 5.1.4 Guardar usuario responsable y timestamp

### 5.2 Historial de Inasistencias

- [x] 5.2.1 Crear vista de historial por empleado
- [x] 5.2.2 Crear vista de historial por sucursal
- [x] 5.2.3 Implementar filtros por fecha y tipo

### 5.3 Reportes

- [x] 5.3.1 Crear reporte de vacaciones por sucursal
- [x] 5.3.2 Crear reporte de permisos por periodo
- [x] 5.3.3 Crear reporte de inasistencias
- [x] 5.3.4 Implementar exportación a Excel/CSV

### 5.4 Métricas

- [x] 5.4.1 Dashboard de métricas operativas
- [ ] 5.4.2 Gráficos de solicitudes por mes
- [ ] 5.4.3 Gráficos de inasistencias por tipo
- [ ] 5.4.4 Indicadores de aprobación/rechazo

### 5.5 Auditoría

- [x] 5.5.1 Crear log de todas las acciones críticas
- [ ] 5.5.2 Implementar historial de cambios en solicitudes
- [ ] 5.5.3 Crear vista de auditoría para Admin

---

## Tareas Transversales

### Testing

- [ ] Crear fixtures para datos de prueba
- [ ] Escribir tests unitarios para modelos
- [ ] Escribir tests para serializers y validaciones
- [ ] Escribir tests de integración para API
- [ ] Configurar CI/CD pipeline

### Documentación

- [ ] Documentar API con DRF-spectacular (OpenAPI)
- [ ] Crear docs de despliegue
- [ ] Crear manual de usuario
- [ ] Documentar variables de entorno

### Seguridad

- [x] Configurar CORS para frontend
- [ ] Implementar rate limiting en API
- [x] Configurar CSRF protection
- [x] Implementar logging de seguridad
- [ ] Revisión de seguridad OWASP

### Despliegue

- [x] Crear docker-compose.yml para producción
- [ ] Configurar nginx con gunicorn
- [ ] Configurar celery como servicio
- [ ] Configurar backups de PostgreSQL
- [ ] Configurar monitoreo (Sentry/NewRelic)

---

## Dependencias Entre Tareas

```
Fase 1 (Completa) → Fase 2
Fase 2 (2.1-2.2) → Fase 3
Fase 2 (2.3-2.5) → Fase 4
Fase 4 → Fase 5
```

---

## Estimación de Tiempo

| Fase | Duración Estimada |
|------|-------------------|
| Fase 1 | 2-3 semanas |
| Fase 2 | 2-3 semanas |
| Fase 3 | 1-2 semanas |
| Fase 4 | 2-3 semanas |
| Fase 5 | 1-2 semanas |

**Total estimado: 8-13 semanas**

---

## Resumen de Progreso

| Fase | Completadas | Totales | % |
|------|-------------|---------|---|
| Fase 1 | 20/20 | 20 | 100% |
| Fase 2 | 22/22 | 22 | 100% |
| Fase 3 | 16/16 | 16 | 100% |
| Fase 4 | 20/21 | 21 | 95% |
| Fase 5 | 10/15 | 15 | 67% |
| Transversales | 3/14 | 14 | 21% |
| **TOTAL** | **91/108** | **108** | **84%** |