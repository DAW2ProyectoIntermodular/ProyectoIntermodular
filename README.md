# 🏫 Plataforma Digital — IES Ramón Arcas Meca

[![Validación OpenAPI](https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular/actions/workflows/lint-openapi.yml/badge.svg)](https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular/actions/workflows/lint-openapi.yml)
[![API Docs](https://img.shields.io/badge/API_Docs-GitHub_Pages-blue?logo=swagger)](https://daw2proyectointermodular.github.io/ProyectoIntermodular/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-green.svg)](./LICENSE)

Proyecto Intermodular de 2º del **CFGS Desarrollo de Aplicaciones Web (DAW)** del **IES Ramón Arcas Meca** (Lorca, Región de Murcia), curso 2026/2027.

La plataforma está formada por dos productos **independientes** (no comparten base de datos, sesión ni autenticación):

1. Una **intranet privada** para la gestión diaria del profesorado y del equipo directivo.
2. Una **web pública** del centro con un panel de administración (backoffice) para gestionar sus contenidos.

El único punto de unión entre ambos es el enlace «Acceso intranet» de la web pública.

---

## 🚦 Estado del proyecto

| Fase | Contenido | Estado |
|---|---|---|
| Diseño de las APIs | Contratos OpenAPI 3.1 de ambos productos, portal de documentación y hoja resumen | ✅ Terminado |
| Cimientos | Entorno con Docker, modelo de datos, autenticación y roles básicos | 🔄 En desarrollo |
| Núcleo funcional | Tablón, FEM, RRSS con IA, retrasos, aulas, tickets RMI/compras… | ⏳ Pendiente |
| Guardias y firma | Guardias por rondas, ausencias con firma, aula de convivencia, comisiones | ⏳ Pendiente |
| Integraciones | OAuth completo, Google Calendar, notificaciones push y email | ⏳ Pendiente |

---

## 📦 Productos

### 1. Intranet de gestión docente (privada)

- Asignación equitativa de guardias por rondas y tramos horarios.
- Registro y justificación de ausencias con generación de PDF y firma manuscrita.
- Tablón de anuncios, notificaciones y borradores de publicaciones para redes sociales con IA.
- Reservas de espacios, incidencias RMI, compras y seguimiento de la FEM con mapa (Leaflet).
- Panel de indicadores para el equipo directivo.

| Capa | Tecnologías |
|---|---|
| Backend | Python 3.12 · FastAPI · JWT (access + refresh) · login con Google OAuth2 · roles con `Depends()` |
| Bases de datos | MongoDB (datos) + Redis (caché, revocación de tokens y tareas en segundo plano) |
| Frontend | React + TypeScript · PWA (menú lateral en escritorio y barra inferior en móvil) |
| Documentos | WeasyPrint / ReportLab para PDF · Pillow para incrustar la firma |
| Pruebas | pytest (autenticación, roles y algoritmo de guardias) |

### 2. Web pública del centro

- Oferta educativa (ESO, Bachillerato y Formación Profesional) y materias optativas.
- Noticias, departamentos, planes y programas del centro.
- Secretaría: cita previa y trámites; buzón de quejas y sugerencias.
- Backoffice para que el centro gestione los contenidos sin tocar código.
- Accesibilidad (WCAG 2.1 AA), URLs amigables y `sitemap.xml`.

| Capa | Tecnologías |
|---|---|
| Backend | PHP 8.3 sin framework · API REST en `/api/v1` |
| Autenticación del backoffice | Sesión nativa de PHP (cookie `PHPSESSID`) |
| Base de datos | MySQL / MariaDB normalizada (3FN) con claves foráneas y relaciones N:M |
| Frontend | HTML5 semántico · CSS · TypeScript |

---

## 📊 Especificación de las APIs (OpenAPI 3.1)

| Producto | Contrato | Rutas | Operaciones | Módulos |
|---|---|---|---|---|
| Intranet | [`docs/api/openapi-intranet.yaml`](./docs/api/openapi-intranet.yaml) | 76 | 134 | 23 |
| Web pública + backoffice | [`docs/api/openapi-web.yaml`](./docs/api/openapi-web.yaml) | 47 | 75 | 22 |
| **Total** | | **123** | **209** | **45** |

Una *ruta* es una URL (`/api/v1/guardias/{guardia_id}`) y una *operación* es cada método HTTP sobre ella (`GET`, `PATCH`…).

Convenciones aplicadas:

- Rutas en español, en plural y en minúsculas, con versión: `/api/v1/guardias`, `/api/v1/noticias`.
- Paginación con `?page=1&limit=10` (máximo 50) y respuesta `{"items": [...], "page": 1, "limit": 10, "total": N}`.
- `201 Created` con cabecera `Location`, `204 No Content` al borrar, `409 Conflict` en solapes o transiciones de estado no válidas.
- Errores siempre con el formato `{"detail": "..."}`.

Los dos contratos se validan automáticamente en cada cambio con **openapi-spec-validator** y **Redocly CLI** (workflow `lint-openapi.yml`).

### Documentación publicada

- **Portal de APIs** (catálogo con buscador, Swagger UI y Redoc): <https://daw2proyectointermodular.github.io/ProyectoIntermodular/>
- **Hoja resumen imprimible (A3)**: <https://daw2proyectointermodular.github.io/ProyectoIntermodular/cheatsheet.html>

### Ver la documentación en local

```bash
git clone https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular.git
cd ProyectoIntermodular/docs
python -m http.server 8000
```

Y abrir <http://localhost:8000> en el navegador. (Si se abre `index.html` con doble clic, el portal funciona igualmente, pero lee los contratos de la copia publicada en GitHub).

---

## 📁 Estructura del repositorio

```text
├── intranet/
│   ├── backend/              # API FastAPI
│   │   ├── app/
│   │   │   ├── api/v1/       # Endpoints versionados
│   │   │   ├── core/         # Configuración, seguridad y permisos
│   │   │   ├── models/       # Modelos de MongoDB
│   │   │   ├── schemas/      # Esquemas Pydantic
│   │   │   ├── services/     # Lógica de negocio (guardias, ausencias…)
│   │   │   └── utils/        # PDF y firmas
│   │   └── tests/            # Pruebas con pytest
│   └── frontend/             # PWA React + TypeScript
├── web-publica/
│   ├── backend/              # PHP sin framework
│   │   ├── api/v1/           # Endpoints públicos
│   │   ├── admin/            # Backoffice
│   │   ├── config/           # Conexión PDO
│   │   └── models/           # Acceso a datos
│   ├── frontend/             # HTML, CSS y TypeScript
│   └── database/             # Scripts SQL
├── docs/
│   ├── api/                  # Contratos OpenAPI 3.1
│   ├── index.html            # Portal de documentación
│   └── cheatsheet.html       # Hoja resumen A3
├── .github/workflows/
│   ├── deploy-docs.yml       # Publica docs/ en GitHub Pages
│   └── lint-openapi.yml      # Valida los contratos OpenAPI
├── .env.example              # Plantilla de variables de entorno
├── redocly.yaml              # Reglas del linter de OpenAPI
└── LICENSE
```

Las carpetas de `intranet/` y `web-publica/` están creadas y se irán completando en las siguientes fases.

---

## 🔐 Variables de entorno

Las credenciales nunca se suben al repositorio. Para trabajar en local:

```bash
cp .env.example .env
```

y rellenar los valores en el `.env` (que está excluido en `.gitignore`).

---

## 👥 Equipo

- **José Iver Peñarrieta** — [@joseiverp](https://github.com/joseiverp)
- **Francisco Guerrero** — [@FranGuerreroH](https://github.com/FranGuerreroH)

---

## 📄 Licencia

Distribuido bajo la [licencia MIT](./LICENSE).
