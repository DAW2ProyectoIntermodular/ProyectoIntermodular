# 🏫 Proyecto Intermodular — IES Ramón Arcas Meca

[![Validación OpenAPI](https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular/actions/workflows/lint-openapi.yml/badge.svg)](https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular/actions/workflows/lint-openapi.yml)
[![API Docs](https://img.shields.io/badge/API_Docs-GitHub_Pages-blue?logo=swagger)](https://daw2proyectointermodular.github.io/ProyectoIntermodular/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

> **2º CFGS Desarrollo de Aplicaciones Web (DAW2) — Curso 2026/2027**
>
> Proyecto intermodular compuesto por dos productos digitales independientes para el **IES Ramón Arcas Meca** (Lorca, Murcia).

---

## 📦 Productos Digitales

### 1. Intranet de Gestión Docente (Privada y Transaccional)
Plataforma transaccional para la operativa interna del profesorado y equipo directivo: comunicación, horarios, asignación de guardias por rondas, ausencias con firma manuscrita/digital, tickets RMI/compras, seguimiento FEM (500h) con mapas Leaflet y dashboard directivo (9 KPIs).

| Capa | Tecnología |
|------|-----------|
| Backend | Python · FastAPI (v1) · JWT (Access + Refresh) |
| Bases de Datos | MongoDB (almacén persistente NoSQL) + Redis (caché y sesiones) |
| Frontend | React · TypeScript · PWA (Escritorio estilo sidebar / Móvil estilo iOS) |
| Generación Documental | WeasyPrint / ReportLab + Pillow (firma manuscrita en canvas) |
| Tests | pytest (cobertura en autenticación, RBAC y algoritmo de guardias) |

### 2. Web Pública del Centro Educativo
Portal institucional para familias, alumnado y comunidad educativa con backoffice administrativo privado para gestión editorial sin frameworks.

| Capa | Tecnología |
|------|-----------|
| Backend | PHP puro (sin framework) · API REST en `/api/v1` |
| Autenticación Admin | Sesión nativa con cookie segura (`PHPSESSID`) |
| Base de Datos | MySQL / MariaDB (normalizada en 3FN, claves foráneas, relaciones N:M) |
| Frontend | HTML5 · CSS moderno minimalista · TypeScript |
| SEO y Accesibilidad | URLs amigables (`slug`) · `sitemap.xml` dinámico · Pautas WCAG 2.1 AA |

---

## 📊 Especificación de Endpoints (1ª Entrega — 30 de octubre)

Total de **124 endpoints** definidos bajo especificación formal **OpenAPI 3.1**, validados al 100% sin advertencias y cumpliendo estrictamente la guía de estilo REST:

* **Rutas en español y sustantivos en plural:** `/api/v1/guardias`, `/api/v1/noticias`, `/api/v1/usuarios`, etc.
* **Paginación estándar:** `?page=1&limit=10` con envoltorio `{"items": [...], "page": 1, "limit": 10, "total": N}`.
* **Semántica HTTP:** `POST` (201 Created con cabecera `Location`), `PUT` (reemplazo completo), `PATCH` (estados/parcial), `DELETE` (204 No Content).
* **Gestión canónica de errores:** Formato canónico `{"detail": "..."}` en todos los códigos HTTP.

| Producto | Archivo OpenAPI | Endpoints | Módulos | Documentación Interactiva |
|---|---|---|---|---|
| **Intranet Docente** | [`docs/api/openapi-intranet.yaml`](./docs/api/openapi-intranet.yaml) | **76** | 22 | [Ver en Swagger UI](https://daw2proyectointermodular.github.io/ProyectoIntermodular/) |
| **Web Pública** | [`docs/api/openapi-web.yaml`](./docs/api/openapi-web.yaml) | **48** | 22 | [Ver en Redoc](https://daw2proyectointermodular.github.io/ProyectoIntermodular/) |
| **Hoja Resumen A3** | [`docs/cheatsheet.html`](./docs/cheatsheet.html) | **124** | 44 | [Ver Hoja Visual Cheatsheet](https://daw2proyectointermodular.github.io/ProyectoIntermodular/cheatsheet.html) |

---

## 📁 Estructura del Repositorio

```
├── intranet/                    # Proyecto 1: Intranet de Gestión Docente
│   ├── backend/                 # FastAPI + Python
│   │   ├── app/
│   │   │   ├── api/v1/          # Endpoints versionados
│   │   │   ├── core/            # Configuración, seguridad JWT, RBAC
│   │   │   ├── models/          # Modelos ODM MongoDB
│   │   │   ├── schemas/         # Pydantic schemas
│   │   │   ├── services/        # Lógica de negocio (guardias, etc.)
│   │   │   └── utils/           # Generación de PDFs y firmas
│   │   ├── tests/               # Tests con pytest
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/                # React + TypeScript PWA
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── Dockerfile
├── web-publica/                 # Proyecto 2: Web Pública del Centro
│   ├── backend/                 # PHP puro (sin framework)
│   │   ├── api/v1/              # Endpoints REST públicos y admin
│   │   ├── admin/               # Backoffice (sesión PHPSESSID)
│   │   ├── config/              # Conexión PDO a MySQL
│   │   ├── models/              # DAO / Repositorios (3FN)
│   │   └── public/              # Punto de entrada
│   ├── frontend/                # HTML5 + CSS + TypeScript
│   │   ├── src/
│   │   └── assets/
│   ├── database/                # Esquemas y migraciones SQL
│   └── Dockerfile
├── docs/                        # Documentación Oficial
│   ├── api/                     # Contratos OpenAPI 3.1
│   │   ├── openapi-intranet.yaml
│   │   └── openapi-web.yaml
│   ├── CONTEXTO_OFICIAL_PROYECTO.md
│   ├── ESTADO_ACTUAL_Y_CONTINUACION.md
│   ├── index.html               # Portal interactivo (Swagger UI + Redoc)
│   └── cheatsheet.html          # Hoja visual imprimible A3 / PDF
├── .github/workflows/           # CI/CD (GitHub Actions)
│   ├── deploy-docs.yml          # Despliegue automático a GitHub Pages
│   └── lint-openapi.yml         # Validación continua de contratos OpenAPI
├── docker-compose.yml           # Orquestación de contenedores
├── .env.example                 # Variables de entorno de plantilla
├── .gitignore
├── LICENSE                      # Licencia MIT
└── README.md
```

---

## 🚀 Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular.git
cd ProyectoIntermodular

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar servicios con Docker
docker-compose up -d

# 4. Enlaces de acceso
# Intranet PWA:      http://localhost:3000
# Intranet API:      http://localhost:8000/api/v1
# Web Pública:       http://localhost:8080
# Documentación API: https://daw2proyectointermodular.github.io/ProyectoIntermodular/
```

---

## 👥 Equipo y Distribución del Trabajo (50 / 50)

| Integrante | Usuario GitHub | Correo Oficial | Rol Principal |
|---|---|---|---|
| **José Iver Peñarrieta** | [@joseiverp](https://github.com/joseiverp) | `14499483@alu.murciaeduca.es` | Co-Arquitecto / Full-Stack |
| **Francisco Guerrero** | [@FranGuerreroH](https://github.com/FranGuerreroH) | `3728291@alu.murciaeduca.es` | Co-Arquitecto / Full-Stack |

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **[MIT](./LICENSE)** como software libre para el ámbito educativo.
