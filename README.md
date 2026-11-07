# 🏫 Plataforma Digital — IES Ramón Arcas Meca

[![Validación OpenAPI](https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular/actions/workflows/lint-openapi.yml/badge.svg)](https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular/actions/workflows/lint-openapi.yml)
[![API Docs](https://img.shields.io/badge/API_Docs-GitHub_Pages-blue?logo=swagger)](https://daw2proyectointermodular.github.io/ProyectoIntermodular/)
[![License: MIT](https://img.shields.io/badge/Licencia-MIT-green.svg)](./LICENSE)

Proyecto desarrollado para el **IES Ramón Arcas Meca** (Lorca, Murcia) en el marco del segundo curso del **CFGS Desarrollo de Aplicaciones Web (DAW)**, curso académico 2026/2027.

La plataforma se compone de dos productos digitales desacoplados e independientes: una **intranet privada transaccional** para la operativa diaria del profesorado y equipo directivo, y un **portal web institucional accesible** para toda la comunidad educativa.

---

## 📦 Productos Digitales

### 1. Intranet de Gestión Docente (Privada y Transaccional)

Herramienta interna enfocada en agilizar y transparentar las gestiones cotidianas del centro escolar:
- Algoritmo de asignación equitativa de guardias lectivas por rondas y tramos horarios.
- Registro y justificación de ausencias con captura de firma manuscrita digital.
- Comunicación interna, reservas de espacios compartidos y tablón de anuncios.
- Gestión de incidencias técnicas (RMI), compras y seguimiento de FCT/FEM con mapas Leaflet.
- Panel de control para el equipo directivo con indicadores clave de funcionamiento.

| Capa | Tecnologías |
|---|---|
| **Backend** | Python 3.12 · FastAPI (asíncrono) · Autenticación JWT y Google OAuth2 · RBAC |
| **Bases de Datos** | MongoDB (almacenamiento documental) + Redis (caché y denylist de tokens) |
| **Frontend** | React 18 · TypeScript · PWA (interfaz de escritorio con menú lateral y móvil estilo app nativa) |
| **Documentación y Reportes** | WeasyPrint / ReportLab para partes oficiales y exportaciones en PDF |
| **Pruebas** | pytest (cobertura en lógica de guardias, permisos y autenticación) |

---

### 2. Portal Web Institucional (Público y Accesible)

Portal oficial del centro educativo enfocado a familias, alumnado y entorno social, con un panel de administración privado para secretaría y redacción de novedades:
- Catálogo de enseñanzas formativas (ESO, Bachillerato, Ciclos Formativos de FP).
- Publicación de noticias, convocatorias, eventos y proyectos del centro.
- Sección de secretaría virtual con trámites telemáticos y descarga de impresos.
- Directorio de departamentos didácticos y contacto directo.
- Cumplimiento de directivas de accesibilidad para la administración pública (WCAG 2.1 nivel AA).

| Capa | Tecnologías |
|---|---|
| **Backend** | PHP 8.3 puro (sin frameworks externos) · API REST bajo `/api/v1` |
| **Autenticación Panel** | Sesiones nativas de PHP con cookie de seguridad (`PHPSESSID`) |
| **Base de Datos** | MySQL / MariaDB normalizada en Tercera Forma Normal (3FN) con claves foráneas |
| **Frontend** | HTML5 semántico · CSS moderno minimalista · TypeScript |
| **SEO y Rendimiento** | Enlaces legibles (`slugs`), sitemap dinámico y marcado de accesibilidad ARIA |

---

## 📊 Especificación de Endpoints (OpenAPI 3.1)

El proyecto cuenta con una especificación formal de **124 endpoints** descritos bajo el estándar **OpenAPI 3.1**, validados sin advertencias mediante `openapi-spec-validator` y siguiendo una convención REST coherente:

- **Convención de rutas:** Recursos en plural y en español (`/api/v1/guardias`, `/api/v1/noticias`, `/api/v1/departamentos`).
- **Paginación uniforme:** Parámetros `?page=1&limit=10` con formato estándar `{ "items": [...], "page": 1, "limit": 10, "total": N }`.
- **Códigos de estado:** `200 OK`, `201 Created` con cabecera `Location`, `204 No Content` para eliminaciones, y respuestas detalladas de error `{ "detail": "..." }`.

| Sistema | Archivo de Especificación | Rutas | Módulos | Visor Interactivo |
|---|---|---|---|---|
| **Intranet Docente** | [`docs/api/openapi-intranet.yaml`](./docs/api/openapi-intranet.yaml) | **76** | 22 | [Swagger UI](https://daw2proyectointermodular.github.io/ProyectoIntermodular/) |
| **Web Pública** | [`docs/api/openapi-web.yaml`](./docs/api/openapi-web.yaml) | **48** | 22 | [Redoc](https://daw2proyectointermodular.github.io/ProyectoIntermodular/) |
| **Hoja Resumen A3** | [`docs/cheatsheet.html`](./docs/cheatsheet.html) | **124** | 44 | [Cheatsheet A3](https://daw2proyectointermodular.github.io/ProyectoIntermodular/cheatsheet.html) |

---

## 📁 Estructura del Proyecto

```text
├── intranet/                     # Módulo privado transaccional
│   ├── backend/                  # API en FastAPI (Python)
│   │   ├── app/
│   │   │   ├── api/v1/           # Endpoints versionados
│   │   │   ├── core/             # Configuración, seguridad y permisos
│   │   │   ├── models/           # Modelos de datos (MongoDB)
│   │   │   ├── schemas/          # Esquemas de validación Pydantic
│   │   │   ├── services/         # Lógica de guardias, ausencias y gestión
│   │   │   └── utils/            # Generación documental y firmas
│   │   └── tests/                # Pruebas automatizadas con pytest
│   └── frontend/                 # Aplicación cliente React + TypeScript (PWA)
│       ├── src/
│       └── public/
├── web-publica/                  # Módulo público institucional
│   ├── backend/                  # API y lógica en PHP nativo
│   │   ├── api/v1/               # Endpoints REST públicos
│   │   ├── admin/                # Backoffice editorial
│   │   ├── config/               # Conexión PDO a base de datos
│   │   └── models/               # Repositorios y entidades SQL
│   ├── frontend/                 # Vistas HTML5, hojas de estilo y scripts TS
│   └── database/                 # Esquemas relacionales y migraciones SQL
├── docs/                         # Documentación técnica
│   ├── api/                      # Contratos OpenAPI 3.1
│   │   ├── openapi-intranet.yaml
│   │   └── openapi-web.yaml
│   ├── index.html                # Portal interactivo (Swagger UI y Redoc)
│   └── cheatsheet.html           # Hoja visual resumida para consulta e impresión
├── .github/workflows/            # Automatización e integración continua
│   ├── deploy-docs.yml           # Despliegue del portal a GitHub Pages
│   └── lint-openapi.yml          # Validación continua de contratos OpenAPI
├── docker-compose.yml            # Orquestación de servicios en contenedores
├── .gitignore
├── LICENSE                       # Licencia MIT en español
└── README.md
```

---

## 🚀 Consulta de la Documentación

Toda la documentación técnica de las APIs está desplegada y disponible para su consulta interactiva:

* **Portal de Documentación API:** [daw2proyectointermodular.github.io/ProyectoIntermodular](https://daw2proyectointermodular.github.io/ProyectoIntermodular/)
* **Hoja Resumen A3 (Imprimible):** [Cheatsheet de Endpoints](https://daw2proyectointermodular.github.io/ProyectoIntermodular/cheatsheet.html)

Para consultar la especificación en local, basta con clonar el repositorio y abrir `docs/index.html` en cualquier navegador web:

```bash
git clone https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular.git
cd ProyectoIntermodular
```

---

## 👥 Equipo de Desarrollo

* **José Iver Peñarrieta** — [@joseiverp](https://github.com/joseiverp) (`14499483@alu.murciaeduca.es`)
* **Francisco Guerrero** — [@FranGuerreroH](https://github.com/FranGuerreroH) (`3728291@alu.murciaeduca.es`)

Centro Educativo: **IES Ramón Arcas Meca**, Lorca (Región de Murcia).

---

## 📄 Licencia

Este proyecto se distribuye bajo los términos de la **[Licencia MIT](./LICENSE)** en español.
