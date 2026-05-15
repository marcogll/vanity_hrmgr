# Plan de Desarrollo - Sistema de Control de Permisos, Vacaciones e Inasistencias

## Fases del Proyecto

El proyecto se divide en 5 fases principales, cada una con tareas específicas que deben completarse en orden.

---

## Fase 1 — Base de Datos y Modelos

### 1.1 Configuración del Proyecto

- [ ] 1.1.1 Inicializar proyecto Django con estructura de apps
- [ ] 1.1.2 Configurar settings.py para PostgreSQL, Redis y logging
- [ ] 1.1.3 Configurar Docker y Docker Compose
- [ ] 1.1.4 Configurar variables de entorno (.env.example)
- [ ] 1.1.5 Configurar pytest y coverage para testing
- [ ] 1.1.6 Crear requirements.txt con todas las dependencias

### 1.2 Modelos ORM - Employees App

- [ ] 1.2.1 Crear modelo Branch (sucursal) con campos: name, address, active
- [ ] 1.2.2 Crear modelo Employee con campos:
  - user (OneToOne con Django User)
  - employee_number (único)
  - curp, rfc
  - tipo_contrato (choices: Laboral/Mercantil)
  - fecha_ingreso
  - saldo_vacaciones (Float)
  - branch (FK)
  - manager (FK)
  - status (choices: Activo/Baja/Suspendido)
- [ ] 1.2.3 Crear modelo EmployeeAudit para auditoría de cambios
- [ ] 1.2.4 Implementar señales para actualizar saldo en aniversario
- [ ] 1.2.5 Crear migraciones y ejecutar

### 1.3 Modelos ORM - Holidays App

- [ ] 1.3.1 Crear modelo Holiday con campos: fecha, descripcion, activo
- [ ] 1.3.2 Crear script de seed para feriados mexicanos estándar
- [ ] 1.3.3 Implementar método para verificar día festivo
- [ ] 1.3.4 Implementar método para calcular días hábiles entre fechas

### 1.4 Modelos ORM - Requests App

- [ ] 1.4.1 Crear modelo Request (vacaciones/permisos) con campos:
  - tipo (choices: Vacación/Permiso)
  - fecha_inicio, fecha_fin
  - estatus (choices: Pendiente/Aprobado/Rechazado)
  - observaciones_sistema
  - comentario_admin
  - empleado (FK)
  - created_at, updated_at
- [ ] 1.4.2 Crear modelo RequestComment para historial de comentarios

### 1.5 Modelos ORM - Absences App

- [ ] 1.5.1 Crear modelo Absence con campos:
  - empleado (FK)
  - fecha
  - sucursal (FK)
  - tipo (choices: Injustificada/Enfermedad/Suspensión/Retardo/Permiso sin goce/Otro)
  - motivo
  - registrado_por (FK)
  - created_at
- [ ] 1.5.2 Crear modelo AbsenceAudit para auditoría

### 1.6 Modelos ORM - Catálogos

- [ ] 1.6.1 Crear modelo Configuration para configuraciones globales
- [ ] 1.6.2 Crear modelo NotificationLog para logs de Telegram

---

## Fase 2 — Motor de Solicitudes

### 2.1 Lógica de Vacaciones (LFT Art. 76)

- [ ] 2.1.1 Implementar cálculo de antigüedad por fecha de ingreso
- [ ] 2.1.2 Implementar tabla de días por antigüedad:
  - 1 año: 6 días
  - 2 años: 8 días
  - 3 años: 10 días
  - 4 años: 12 días
  - 5-9 años: 14 días
  - 10-14 años: 16 días
  - 15-19 años: 18 días
  - 20+ años: 20 días
- [ ] 2.1.3 Implementar renovación automática en fecha de aniversario
- [ ] 2.1.4 Implementar exclusión de días festivos del descuento
- [ ] 2.1.5 Validar que saldo no quede negativo

### 2.2 Lógica de Permisos

- [ ] 2.2.1 Validar máximo de 3 días hábiles
- [ ] 2.2.2 Validar anticipación de 24-48 horas
- [ ] 2.2.3 Implementar etiqueta "FUERA DE CONDICIONES / RIESGO DE ABANDONO"
- [ ] 2.2.4 Permitir envío con bandera cuando rompe reglas
- [ ] 2.2.5 Validar que no haya traslapes de solicitudes

### 2.3 API REST - Endpoints

- [ ] 2.3.1 Configurar Django REST Framework
- [ ] 2.3.2 Crear endpoints para Solicitudes:
  - GET /api/requests/ (listar del usuario)
  - POST /api/requests/ (crear solicitud)
  - GET /api/requests/{id}/ (detalle)
  - PATCH /api/requests/{id}/ (actualizar si está pendiente)
  - DELETE /api/requests/{id}/ (cancelar si está pendiente)
- [ ] 2.3.3 Crear endpoints para Empleados:
  - GET /api/employees/ (listar - solo Admin/Manager)
  - GET /api/employees/{id}/ (detalle)
  - GET /api/employees/me/ (datos propios)
- [ ] 2.3.4 Crear endpoints para Sucursales:
  - GET /api/branches/
  - GET /api/branches/{id}/employees/
- [ ] 2.3.5 Crear endpoint de dashboard para Admin/Manager

### 2.4 Serializer y Validaciones

- [ ] 2.4.1 Crear RequestSerializer con validaciones
- [ ] 2.4.2 Crear EmployeeSerializer
- [ ] 2.4.3 Crear AbsenceSerializer
- [ ] 2.4.4 Implementar validaciones personalizadas en serializers

### 2.5 Permisos y Autenticación

- [ ] 2.5.1 Configurar Django Auth
- [ ] 2.5.2 Crear CustomPermission classes para RBAC
- [ ] 2.5.3 Implementar JWT authentication (djangorestframework-simplejwt)
- [ ] 2.5.4 Configurar autenticación por sesión para templates

---

## Fase 3 — Telegram Bot

### 3.1 Configuración del Bot

- [ ] 3.1.1 Crear app TelegramBot con python-telegram-bot
- [ ] 3.1.2 Configurar webhook o polling mode
- [ ] 3.1.3 Implementar manejo de comandos /start, /help
- [ ] 3.1.4 Crear gestión de estados del conversation handler

### 3.2 Notificaciones

- [ ] 3.2.1 Implementar callback para nueva solicitud
- [ ] 3.2.2 Enviar notificación con detalles de solicitud
- [ ] 3.2.3 Crear Inline Keyboard con botones [Aprobar] [Rechazar]
- [ ] 3.2.4 Implementar manejo de callbacks para aprobación/rechazo
- [ ] 3.2.5 Solicitar comentario opcional tras acción
- [ ] 3.2.6 Guardar comentario en Request y actualizar estatus

### 3.3 Integración con Sistema

- [ ] 3.3.1 Crear función para obtener admin_id de configuración
- [ ] 3.3.2 Crear función para enviar notificación asíncrona
- [ ] 3.3.3 Integrar Celery para tareas asíncronas del bot
- [ ] 3.3.4 Implementar respuesta automática al colaborador

### 3.4 Pruebas del Bot

- [ ] 3.4.1 Probar notificaciones en entorno local
- [ ] 3.4.2 Probar flujo completo de aprobación
- [ ] 3.4.3 Probar manejo de errores y reintentos
- [ ] 3.4.4 Configurar logging de bot

---

## Fase 4 — Dashboard Web

### 4.1 Templates Base

- [ ] 4.1.1 Crear base.html con estructura responsive
- [ ] 4.1.2 Implementar navbar con menú según rol
- [ ] 4.1.3 Crear sistema de mensajes flash
- [ ] 4.1.4 Configurar static files (CSS, JS, imágenes)

### 4.2 Vistas de Empleado

- [ ] 4.2.1 Crear vista de perfil del empleado
- [ ] 4.2.2 Crear formulario de solicitud de vacaciones
- [ ] 4.2.3 Crear formulario de solicitud de permiso
- [ ] 4.2.4 Crear historial de solicitudes del empleado
- [ ] 4.2.5 Mostrar saldo de vacaciones y próxima renovación
- [ ] 4.2.6 Mostrar comentarios administrativos

### 4.3 Dashboard Admin/Manager

- [ ] 4.3.1 Crear calendario maestro con FullCalendar
- [ ] 4.3.2 Implementar filtros por sucursal
- [ ] 4.3.3 Implementar filtros por tipo de ausencia
- [ ] 4.3.4 Mostrar solicitudes pendientes con colores
- [ ] 4.3.5 Crear panel de aprobación rápida

### 4.4 Búsqueda de Socios

- [ ] 4.4.1 Crear formulario de búsqueda global
- [ ] 4.4.2 Buscar por nombre, número de empleado, CURP
- [ ] 4.4.3 Filtrar por estatus laboral y sucursal
- [ ] 4.4.4 Mostrar resultados en tabla paginada

### 4.5 Panel de Transparencia

- [ ] 4.5.1 Mostrar historial completo de solicitudes
- [ ] 4.5.2 Mostrar comentarios administrativos
- [ ] 4.5.3 Mostrar estatus actual y saldo disponible
- [ ] 4.5.4 Mostrar próxima fecha de renovación

---

## Fase 5 — Inasistencias y Reportes

### 5.1 Registro de Inasistencias

- [x] 5.1.1 Crear formulario de registro de falta
- [x] 5.1.2 Validar que solo Manager/Admin puedan registrar
- [x] 5.1.3 Implementar selección de empleado por sucursal
- [x] 5.1.4 Guardar usuario responsable y timestamp

### 5.2 Historial de Inasistencias

- [x] 5.1.5 Crear vista de historial por empleado
- [x] 5.1.6 Crear vista de historial por sucursal
- [x] 5.1.7 Implementar filtros por fecha y tipo

### 5.3 Reportes

- [x] 5.3.1 Crear reporte de vacaciones por sucursal
- [x] 5.3.2 Crear reporte de permisos por periodo
- [x] 5.3.3 Crear reporte de inasistencias
- [x] 5.3.4 Implementar exportación a Excel/CSV

### 5.4 Métricas

- [x] 5.4.1 Dashboard de métricas operativas
- [x] 5.4.2 Gráficos de solicitudes por mes
- [x] 5.4.3 Gráficos de inasistencias por tipo
- [x] 5.4.4 Indicadores de aprobación/rechazo

### 5.5 Auditoría

- [x] 5.5.1 Crear log de todas las acciones críticas
- [x] 5.5.2 Implementar historial de cambios en solicitudes
- [x] 5.5.3 Crear vista de auditoría para Admin

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
- [ ] Crear文档 de despliegue
- [ ] Crear manual de usuario
- [ ] Documentar variables de entorno

### Seguridad

- [ ] Configurar CORS para frontend
- [ ] Implementar rate limiting en API
- [ ] Configurar CSRF protection
- [ ] Implementar logging de seguridad
- [ ] Revisión de seguridad OWASP

### Despliegue

- [ ] Crear docker-compose.yml para producción
- [ ] Configurar nginx con gunicorn
- [ ] Configurarcelery como servicio
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