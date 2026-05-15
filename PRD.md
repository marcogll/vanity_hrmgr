# PRD: Sistema de Control de Permisos, Vacaciones e Inasistencias

## 1. Visión General

Desarrollar una plataforma web centralizada con integración a Telegram para gestionar el capital humano de diversas sucursales. El sistema automatiza el cálculo de prestaciones por antigüedad, filtra solicitudes bajo reglas de contrato (Mercantil vs. Laboral) y permite un control administrativo transparente.

---

## 2. Roles y Permisos

| Rol | Capacidades |
|---|---|
| **Admin** | Acceso total. Aprueba/Rechaza vía Telegram. Ve todas las sucursales. Gestiona catálogos. |
| **Manager** | Vista exclusiva de sus sucursales asignadas. Búsqueda de socios. Registro de inasistencias. |
| **User (Colaborador)** | Solicita vacaciones/permisos. Consulta su saldo de días y estatus de solicitudes. |

---

## 3. Especificaciones Funcionales

### A. Gestión de Vacaciones (Lógica LFT Art. 76)

- **Actualización:** El saldo se incrementa automáticamente en la fecha de aniversario del empleado (**Opción A**).
- **Cómputo:** Se descuentan los días solicitados del saldo actual, excluyendo días festivos registrados en la tabla de feriados.
- **Restricción:** No se permiten solicitudes con fechas pasadas (bloqueo en formulario).

### B. Gestión de Permisos (Reglas Mercantiles)

- **Condiciones:** Solicitudes de máximo 3 días hábiles.
- **Antelación:** Validación de 24-48 horas previas a la fecha de inicio.
- **Flexibilidad:** Si la solicitud rompe las reglas (ej. más de 3 días o poca antelación), el sistema permite el envío pero marca la solicitud con una etiqueta de **"FUERA DE CONDICIONES / RIESGO DE ABANDONO"** para el Admin.

### C. Sistema de Alertas (Telegram Bot)

- **Notificación Central:** Cada nueva solicitud genera un mensaje al Admin.
- **Interacción:** Botones integrados (Inline Keyboard) para **[Aprobar]** o **[Rechazar]**.
- **Feedback:** Al accionar, el bot solicita un comentario opcional que se refleja instantáneamente en el portal del empleado.

### D. Registro de Inasistencias

Módulo dedicado para que Managers o Admins capturen faltas.

**Campos requeridos:**

- Fecha
- Sucursal
- Colaborador
- Motivo
- Tipo:
  - Injustificada
  - Enfermedad
  - Suspensión
  - Retardo
  - Permiso sin goce
  - Otro

---

## 4. Arquitectura de Datos (Modelos Clave)

### Empleado

| Campo | Tipo | Descripción |
|---|---|---|
| tipo_contrato | Enum | Laboral / Mercantil |
| fecha_ingreso | Date | Base para cálculo de antigüedad |
| saldo_vacaciones | Float | Días disponibles |
| sucursal_id | FK | Relación de sucursal |
| manager_id | FK | Responsable asignado |
| status | Enum | Activo / Baja / Suspendido |

### Solicitud

| Campo | Tipo | Descripción |
|---|---|---|
| tipo | Enum | Vacación / Permiso |
| fecha_inicio | Date | Inicio de solicitud |
| fecha_fin | Date | Fin de solicitud |
| estatus | Enum | Pendiente / Aprobado / Rechazado |
| observaciones_sistema | Text | Resultado de validaciones |
| comentario_admin | Text | Retroalimentación administrativa |
| empleado_id | FK | Relación con empleado |

### Inasistencia

| Campo | Tipo | Descripción |
|---|---|---|
| empleado_id | FK | Colaborador relacionado |
| fecha | Date | Fecha de la falta |
| sucursal_id | FK | Sucursal |
| tipo | Enum | Tipo de inasistencia |
| motivo | Text | Observaciones |
| registrado_por | FK | Usuario que registró |

### Feriados

| Campo | Tipo | Descripción |
|---|---|---|
| fecha | Date | Día festivo |
| descripcion | String | Nombre del feriado |
| activo | Boolean | Considerar en cálculos |

---

## 5. Requerimientos de Interfaz (Dashboard)

### 1. Calendario Maestro

Vista mensual con:

- Filtros por sucursal
- Filtros por tipo de ausencia
- Colores diferenciados por categoría
- Vista rápida de aprobaciones pendientes

### 2. Búsqueda de Socios

Buscador global con:

- Nombre
- Número de empleado
- CURP
- Estatus laboral
- Sucursal

### 3. Panel de Transparencia

Sección donde el empleado puede visualizar:

- Historial de solicitudes
- Comentarios administrativos
- Estatus actual
- Saldo disponible
- Próxima fecha de renovación de vacaciones

---

## 6. Reglas de Negocio

### Vacaciones

- El cálculo se realiza automáticamente según antigüedad.
- Los días festivos no descuentan saldo.
- No se permiten traslapes de solicitudes.
- El saldo nunca puede quedar negativo.

### Permisos

- Máximo 3 días hábiles.
- Validación de anticipación mínima.
- Solicitudes fuera de regla generan bandera administrativa.

### Inasistencias

- Solo Managers y Admins pueden registrar faltas.
- Toda inasistencia queda auditada.
- Debe registrarse usuario responsable y timestamp.

---

## 7. Integración Telegram

### Funcionalidades

- Notificación automática de solicitudes nuevas.
- Aprobación/Rechazo desde Telegram.
- Registro de comentarios administrativos.
- Confirmación automática al colaborador.

### Flujo

1. Usuario crea solicitud.
2. Sistema valida reglas.
3. Telegram envía alerta al Admin.
4. Admin responde desde botones inline.
5. Sistema actualiza estatus en tiempo real.
6. Usuario recibe actualización.

---

## 8. Stack Tecnológico Sugerido

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework Web | Django |
| API | Django REST Framework |
| Bot | python-telegram-bot |
| Base de Datos | PostgreSQL |
| Frontend | Django Templates o React |
| Tareas Asíncronas | Celery + Redis |
| Autenticación | Django Auth + JWT |
| Infraestructura | Docker + Docker Compose |

---

## 9. Roadmap de Desarrollo

### Fase 1 — Base de Datos y Modelos

- Diseño ORM
- Migraciones
- Seeds iniciales
- Reglas de antigüedad

### Fase 2 — Motor de Solicitudes

- CRUD de solicitudes
- Validaciones automáticas
- Cálculo de vacaciones

### Fase 3 — Telegram Bot

- Integración bot
- Aprobaciones inline
- Notificaciones automáticas

### Fase 4 — Dashboard Web

- Calendario
- Panel administrativo
- Búsqueda global

### Fase 5 — Inasistencias y Reportes

- Registro de faltas
- Exportación
- Métricas
- Auditoría

---

## 10. Consideraciones Técnicas

- Arquitectura multi-sucursal.
- Soporte para escalamiento futuro multiempresa.
- Auditoría completa de acciones críticas.
- Preparado para RBAC granular.
- Compatibilidad futura con app móvil.
- API-first para integraciones externas.

---

## 11. Objetivo Final

Centralizar y automatizar el control operativo de colaboradores, permisos, vacaciones e incidencias mediante un sistema administrable, auditable y conectado con Telegram para reducir carga operativa y aumentar transparencia.
