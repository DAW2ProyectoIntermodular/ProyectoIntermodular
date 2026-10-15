# CONTEXTO OFICIAL DEL PROYECTO INTERMODULAR – IES RAMÓN ARCAS MECA (2026/2027)

> [!IMPORTANT]
> Este documento contiene la especificación completa extraída de los documentos oficiales del profesor.
> Es la fuente de verdad para todo el desarrollo. Consúltalo siempre antes de tomar decisiones de diseño.

---

## 1. DATOS GENERALES

- **Centro:** IES Ramón Arcas Meca (Totana, Murcia)
- **Curso:** 2026/2027
- **Ciclo:** 2º CFGS Desarrollo de Aplicaciones Web (DAW2)
- **Equipo:** 2 integrantes (reparto estricto 50/50 verificable en Git)
- **Objetivo de calificación:** 10 (Sobresaliente / Matrícula de Honor)

---

## 2. CALENDARIO DE ENTREGAS (DESARROLLO INCREMENTAL)

| Entrega | Fecha límite | Contenido |
|---------|-------------|-----------|
| **1ª** | 30 de octubre | Enlace a repo/org GitHub + Endpoints APIs completos (`openapi-intranet.yaml`, `openapi-web.yaml`) + web interactiva en GitHub Pages (Swagger/Redoc) + hoja visual de resumen + estructura base del repositorio |
| **2ª** | 30 de noviembre | Avance Memoria escrita + Avance funcional del código (Fase 1: Cimientos + parte de Fase 2: Núcleo funcional) |
| **3ª** | 22 de diciembre | 90% del proyecto y memoria terminados (Fases 2 y 3 completadas + tests automatizados) |
| **4ª** | Final (fecha por confirmar) | 100% terminado (Fase 4: Integraciones + pulido UI/UX + memoria completa + Docker) |

---

## 3. ARQUITECTURA GENERAL: DOS PRODUCTOS INDEPENDIENTES

El proyecto consta de **DOS productos digitales reales y totalmente independientes**:

1. **Proyecto 1: Intranet privada de gestión docente**
2. **Proyecto 2: Web pública e informativa del centro educativo**

### Regla de independencia
- No comparten base de datos, ni sesión, ni tokens de autenticación.
- Su único punto de unión es un botón/enlace de redirección ("Acceso intranet") en la web pública hacia la intranet.
- Si en el futuro la web necesitase mostrar algo de la intranet, se haría mediante una API puntual, nunca accediendo a la BD del otro sistema.

---

## 4. PROYECTO 1: INTRANET DE GESTIÓN DOCENTE (PRIVADA Y TRANSACCIONAL)

### 4.1 Stack Tecnológico Obligatorio

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python + **FastAPI**, versionado `/api/v1/...` |
| **Autenticación** | JWT (`access` + `refresh` tokens), control de roles con `Depends()` |
| **BD Principal** | **MongoDB** (NoSQL): usuarios, expedientes, horarios, guardias, ausencias, tickets, FEM, aulas, convivencia, auditoría |
| **BD Complementaria** | **Redis**: caché, sesiones, cola de tareas (nunca sustituto de MongoDB) |
| **Tareas en 2º plano** | `Background Tasks` de FastAPI (recomendado) o `Celery + Redis` |
| **PDF y Firma** | `WeasyPrint` o `ReportLab` + `Pillow` (firma manuscrita en canvas). AutoFirma como "mejor esfuerzo" |
| **Notificaciones** | `Web Push API` + `Service Worker` + `pywebpush`; correo con `fastapi-mail` o SMTP |
| **Mapas (FEM)** | `Leaflet` + `OpenStreetMap` + `Nominatim` |
| **Servicios Externos** | Google OAuth2, Google Calendar API, API de IA generativa |
| **Frontend** | PWA instalable con **React o Vue + TypeScript** |
| **Contenedores** | `Docker` + `docker-compose` |
| **Tests** | `pytest` (obligatorios en autenticación, roles y algoritmo de guardias) |

### 4.2 Frontend PWA – Paradigmas de Navegación

- **Escritorio:** Menú lateral izquierdo persistente (estilo Claude/ChatGPT/Gemini) + panel de contenido amplio.
- **Móvil:** Estilo iOS reciente, barra de navegación inferior (pestañas), tarjetas grandes, adaptación táctil.
- **Único código base**, sistema de diseño compartido, detección de dispositivo para cambiar paradigma.

### 4.3 Módulos Funcionales y Reglas de Negocio

#### 4.3.1 Comunicación Interna (5.2)

**Tablón de anuncios (5.2.1):**
- Feed segmentado por departamento didáctico, curso o ámbito (general/departamental).
- Campos: título, cuerpo, autor, fecha de publicación, fecha de caducidad opcional, opción de fijar como destacado.
- Los anuncios caducados dejan de mostrarse automáticamente sin borrarlos físicamente (borrado lógico).

**Notificaciones (5.2.2):**
- Web Push API (con PWA instalada) y correo electrónico alternativo.
- Eventos disparadores: anuncio destacado, asignación de guardia, cambios de horario, cambios de estado en tickets (RMI, compras, RRSS).

**Publicaciones en RRSS con IA (5.2.3):**
- Formulario: título de actividad, departamento responsable, imágenes adjuntas, descripción breve.
- Llama a modelo de IA generativa para producir borrador de texto.
- No publica automáticamente: registra un "ticket" para el admin de RRSS, quien copia el texto y descarga imágenes manualmente.

#### 4.3.2 Aula y Alumnado (5.3)

**Emplazamiento en el aula (5.3.1):**
- Diseños de aula configurables (distribución de pupitres y agrupaciones) asociables a una clase concreta (grupo + módulo).

**Gestión de retrasos (5.3.2):**
- El docente registra retraso de alumno (fecha, hora, módulo) y consulta histórico acumulado.
- Estadísticas agregadas (globales o por módulo) ocultas al profesorado, solo para Dashboard directivo.

**Aula de convivencia (5.3.3):**
- Jefatura de estudios registra derivación: motivo y trabajo académico asignado.
- Cada hueco horario se cubre con guardia con destino específico.
- El docente de guardia ve únicamente durante su hora a los alumnos derivados y su tarea.

#### 4.3.3 Horarios y Guardias (5.4)

**Horarios del profesorado (5.4.1):**
- Horario semanal individual con horas lectivas y reducciones horarias (bloques de no disponibilidad).
- **Comparador de horarios:** dados 2+ docentes, calcula intersección de huecos libres para proponer reuniones.

**Algoritmo de asignación de guardias por rondas (5.4.2) – REGLA ESTRICTA:**
1. En cada hueco horario puede haber más de un docente asignado.
2. Se organiza por rondas con contador de guardias realizadas por docente en cada hueco concreto.
3. Si hay empate, la selección es aleatoria.
4. La comparación del contador se hace SIEMPRE entre docentes disponibles en ese hueco concreto, nunca contra todo el claustro.
5. Si el docente asignado no puede, la cubre otro disponible aunque tenga más guardias; en rondas siguientes se da prioridad a quien tiene menos hasta reequilibrar.
6. **Modelo de datos obligatorio:** Distinguir `docente_asignado` (por ronda) y `docente_que_realiza` (quien la cubre).

**Tipos de ausencia (5.4.3):**
- **Genérica:** Requiere justificar motivo y adjuntar justificante pasada la guardia.
- **Administrativa:** Trámites propios.
- **Extraescolar:** Excursión/actividad: marca automáticamente como ausente al profesorado participante en esos días/horas.

#### 4.3.4 Flujo Completo de Ausencias y Firma (5.5)

Máquina de estados (reutilizada también en Comisiones de servicio):
1. El docente marca ausencia (día completo u horas concretas + tipo).
2. Si es genérica, pasada la guardia debe justificar motivo y subir justificante.
3. Autocompletado de datos personales desde Google OAuth o perfil.
4. Generación automática de PDF con toda la información.
5. Firma del PDF: manuscrita en pantalla (garantizada) o electrónica vía AutoFirma (mejor esfuerzo).

#### 4.3.5 Documentación y Recursos (5.6)

**Repositorio documental (5.6.1):**
- Organizado por departamento y proyecto del centro.
- Cada docente solo ve documentos de su departamento o proyectos en los que participa.

**Reserva de espacios y recursos (5.6.2):**
- Gestión de espacios (salón de actos, biblioteca, aulas TIC) y recursos (portátiles, proyectores).
- Detección e impedimento de solapamientos → error `409 Conflict`.

**Comisiones de servicio (5.6.3):**
- Solicitud de permiso para formaciones/reuniones de la Consejería.
- Genera PDF y usa el mismo flujo de firma del apartado 5.5.

#### 4.3.6 Entidad Genérica de Solicitudes / "Ticket" (5.7)

Entidad reutilizable para 3 flujos con creación, notificación email y cola de estados (`pendiente` → `en_curso` → `finalizado`):

1. **Incidencias RMI:** Título, descripción, dispositivo(s), aula → Email al responsable RMI.
2. **Gestión de compras:** Artículo(s), precio, checklist presupuesto → Email al secretario.
3. **Publicaciones RRSS (vista admin):** Texto IA + imágenes → Cola para admin RRSS.

Atributos mínimos: `tipo`, `solicitante`, `responsable_asignado`, `estado`, `datos_especificos` (objeto flexible), `acciones_disponibles` según tipo.

#### 4.3.7 Seguimiento FEM (5.8)

- Válido para todos los ciclos formativos; cada docente ve solo la FEM de sus ciclos.
- Vista de mapa con Leaflet + OSM + Nominatim (empresas activas/inactivas).
- Vista de listado: alumno, empresa, estado del seguimiento.
- Indicador de % de horas cursadas sobre **500 horas** previstas.

#### 4.3.8 Administración, Seguridad y Dashboard (5.9 - 5.11)

**Roles y permisos (5.9.1):**
- Perfil estándar (profesorado), administrador (acceso total), perfiles por competencias (jefatura de estudios, secretaría, responsable RMI, admin RRSS).

**Auditoría (5.9.1):**
- Registro consultable de toda acción relevante: `usuario`, `accion`, `fecha_hora`.

**Acceso OAuth (5.9.2):**
- Login con Google sin restricción de dominio.
- Alta: manual por admin, o autorregistro OAuth con estado `"Pendiente de confirmación"` hasta aprobación.

**RGPD (5.9.3):**
- Gestión de consentimientos, derechos de acceso/rectificación, trazabilidad de accesos a datos sensibles de menores.

**Primeros pasos / Onboarding (5.10):**
- Guía de bienvenida para nuevos docentes con instrucciones y vídeos cortos por módulo.

**Dashboard del equipo directivo (5.11):**
Restringido por rol. 9 KPIs obligatorios:
1. Tasa de abandono por curso
2. Rendimiento académico por grupo
3. Retrasos por grupo (umbral configurable, listado de estudiantes que lo superan)
4. Ausencias del profesorado
5. FEM: % de empresas activas vs registradas (por municipio y ciclo)
6. FEM: % de horas cursadas sobre 500h
7. Publicaciones RRSS por departamento y % publicado
8. Uso del aula de convivencia
9. Comisiones de servicio gestionadas

### 4.4 Fases Oficiales de Desarrollo de la Intranet (5.14)

| Fase | Contenido |
|------|-----------|
| **Fase 1 (Cimientos)** | Esquema de datos, temporalización, autenticación básica, núcleo mínimo de roles y permisos |
| **Fase 2 (Núcleo funcional)** | Tablón, FEM, RRSS con IA, Retrasos, Emplazamiento aula, Roles completos, Primeros pasos, RMI y/o Compras |
| **Fase 3 (Guardias y firma)** | Guardias (con ausencias y firma), Aula convivencia, Comisiones (con firma), módulo restante RMI/Compras |
| **Fase 4 (Integraciones)** | OAuth completo, Google Calendar, Notificaciones (push y email), documentación técnica final |

---

## 5. PROYECTO 2: WEB PÚBLICA DEL CENTRO EDUCATIVO

### 5.1 Stack Técnico

| Capa | Tecnología |
|------|-----------|
| **Backend** | **PHP puro sin framework** (descartado Laravel). API REST en `/api/v1` (JSON) + Backoffice con sesión `PHPSESSID` |
| **BD** | **MySQL o MariaDB**, normalizada en 3FN mínimo, claves foráneas, relaciones N:M |
| **Frontend** | HTML5, CSS moderno (limpio/minimalista), **TypeScript** |
| **SEO** | URLs amigables (`slug`), `sitemap.xml`, WCAG |

### 5.2 Mapa de Secciones (6.2)

1. **Inicio:** Bienvenida, imagen, nombre, localización, logos de sellos/programas
2. **Organización:** Quiénes somos, Equipo directivo, Consejo escolar, Claustro, Documentos institucionales, CCP, Departamentos, Horarios, Calendario escolar
3. **Familias:** Documentos/enlaces, Criterios evaluación, Equipos docentes, Atención familias, Tutoriales, Buzón quejas/sugerencias, Guía convivencia, Rincón de pensar
4. **Enseñanzas:** ESO, Bachillerato, FP, Materias optativas
5. **Secretaría:** Cita previa, Trámites administrativos
6. **Programas:** 20+ planes categorizados (Plurilingüe, Erasmus+, BI, Plan Digital, Bienestar, Convivencia, Igualdad...)
7. **Noticias:** Blog de actualidad
8. **Contacto:** Datos de contacto y ubicación

### 5.3 Modelo de Datos Relacional Orientativo (6.3)

1. `paginas` / `secciones` – Árbol jerárquico del menú (`padre_id`)
2. `documentos` – Entidad reutilizable de documentos categorizados (`institucional`, `familias`, `programa`)
3. `departamentos` – Ficha de departamento (N:M con `programas`)
4. `programas` – Planes con categoría, descripción, documento adjunto (N:M con `departamentos`)
5. `noticias` – Blog con `slug`
6. `personas` – Equipo directivo, claustro, consejo escolar (campo `tipo`)
7. `ensenanzas` y `materias_optativas`
8. `configuracion_centro` – Tabla clave-valor
9. `solicitudes_secretaria` – Cita previa y trámites (estados: `pendiente` → `en_curso` → `finalizado`)

---

## 6. GUÍA DE ESTILO REST DEL PROFESOR

### Convenciones obligatorias

- **Rutas:** Sustantivos en plural, minúsculas, **en español**, con versión `/api/v1` en ambos proyectos.
- **Filtros/Paginación:** `?estado=pendiente&page=1&limit=10` (por defecto `page=1`, `limit=10`, máx `50`). Respuesta: `{"items": [...], "page": 1, "limit": 10, "total": N}`
- **Verbos HTTP:**
  - `GET`: Consultar (sin body)
  - `POST`: Crear recurso (sin ID del cliente; `201 Created` + `Location`) o ejecutar acción no CRUD como subrecurso
  - `PUT`: Sustituir recurso o lista completa
  - `PATCH`: Modificar parcialmente (estados, aprobaciones)
  - `DELETE`: Eliminar → `204 No Content`
- **Códigos de respuesta:** `200`, `201`, `204`, `401`, `403`, `404`, `409` (conflicto/solapamiento/transición inválida), `422`
- **Formato de error:** `{"detail": "..."}`
- **Contratos OpenAPI:** Dos ficheros YAML independientes

### Borrador inicial del compañero (base a corregir)

**Intranet (a traducir al español y completar):**
- `POST /api/v1/auth/login/google`, `POST /api/v1/auth/refresh`
- `GET /api/v1/users/me`, `GET /api/v1/users`, `PUT /api/v1/users/{id}`
- `GET & POST /api/v1/announcements`
- `POST /api/v1/notifications/push-subscribe`
- `POST /api/v1/rrss/generate-text`
- `GET /api/v1/schedules/me`, `POST /api/v1/schedules/compare`
- `GET /api/v1/guards/assignment`
- `POST /api/v1/absences`, `POST /api/v1/absences/{id}/sign`
- `GET & POST /api/v1/classrooms/{id}/layout`
- `POST /api/v1/delays`
- `GET & POST /api/v1/coexistence`
- `GET & POST /api/v1/tickets`, `PATCH /api/v1/tickets/{id}/status`
- `GET /api/v1/documents`
- `GET & POST /api/v1/reservations`
- `POST /api/v1/commissions`
- `GET /api/v1/fem/companies`, `GET /api/v1/fem/students`
- `GET /api/v1/dashboard/kpis`

**Web Pública (a corregir):**
- `GET /api/navigation/menu`, `GET /api/news`, `GET /api/news/{slug}`
- `GET /api/departments`, `GET /api/programs`, `GET /api/courses`
- `GET /api/documents`
- `POST /api/secretaria/appointments`
- `POST /api/contact/complaints`
- Backoffice: `POST /admin/api/login`, CRUD de news, documents, organization, requests

---

## 7. NORMAS DE LA MEMORIA ESCRITA

### Formato
- ~15 páginas por alumno (sin portada, índice ni anexos)
- Fuente Arial 11 pt, interlineado 1,5, márgenes 2,54 cm (4 lados)
- Texto justificado, páginas numeradas abajo-derecha (portada sin numerar)
- Antiplagio: <25% coincidencias, APA 7.ª edición

### Índice Oficial Obligatorio
1. Portada
2. Resumen (200-300 palabras + Abstract + palabras clave)
3. Introducción (3.1 Contexto y justificación, 3.2 Objetivos OE1..OEn en infinitivo, 3.3 Alcance y limitaciones)
4. Análisis empresas del sector (**Aportación individual**: 4.1 Integrante 1 / 4.2 Integrante 2, cada uno con: CNAE/DAFO/PESTEL, Productos y servicios, ODS, PRL Ley 31/1995 y RD 488/1997, Conclusiones)
5. Desarrollo del proyecto (5.1 Metodología ágil/Git/Jira/IA; 5.2 Temporalización/Gantt; 5.3 Actividades + tabla módulos DAW; 5.4 Recursos y stack con versiones)
6. Resultados y análisis (Tabla OE1..OEn, cobertura tests, rendimiento, WCAG, RGPD)
7. Conclusiones y recomendaciones (7.1 Conclusiones, 7.2 Recomendaciones futuras)
- Bibliografía APA 7.ª con sangría francesa (incluir herramientas de IA)
- Anexo I: Documentación técnica, diagramas, OpenAPI, tabla repos (licencia MIT)
- Anexo II: Evidencias multimedia con leyendas numeradas (CC/elaboración propia)
- Anexo III: Ficha autoevaluación (1-4)
- Anexo IV: Ficha coevaluación (1-4)

---

## 8. REGLAS DE TRABAJO EN GIT

- Reparto estricto 50/50 verificable por el profesor (autores, fechas, commits progresivos).
- Prohibido subir todo de golpe al final.
- Flujo de ramas, commits y Pull Requests que refleje trabajo cooperativo.
- Variables de entorno en `.env` (jamás subidas a Git).
- Licencia MIT en repositorios públicos.
