# 🏫 Proyecto Intermodular — IES Ramón Arcas Meca

[![API Docs](https://img.shields.io/badge/API_Docs-GitHub_Pages-blue?logo=swagger)](https://daw2proyectointermodular.github.io/ProyectoIntermodular/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

> **2º CFGS Desarrollo de Aplicaciones Web (DAW2) — Curso 2026/2027**
>
> Proyecto intermodular compuesto por dos productos digitales independientes para el IES Ramón Arcas Meca (Lorca, Murcia).

---

## 📦 Productos

### 1. Intranet de Gestión Docente (Privada)
Plataforma transaccional para la gestión interna del profesorado: comunicación, horarios, guardias, ausencias, tickets, FEM y dashboard directivo.

| Capa | Tecnología |
|------|-----------|
| Backend | Python · FastAPI · JWT |
| Base de Datos | MongoDB + Redis |
| Frontend | React · TypeScript · PWA |
| Tests | pytest |

### 2. Web Pública del Centro Educativo
Portal informativo para familias, alumnado y comunidad educativa con backoffice de gestión de contenidos.

| Capa | Tecnología |
|------|-----------|
| Backend | PHP puro (sin framework) · API REST |
| Base de Datos | MySQL / MariaDB (3FN) |
| Frontend | HTML5 · CSS · TypeScript |
| SEO | URLs amigables · sitemap.xml · WCAG |

---

## 📁 Estructura del Repositorio

```
├── intranet/                    # Proyecto 1: Intranet
│   ├── backend/                 # FastAPI + Python
│   │   ├── app/
│   │   │   ├── api/v1/          # Endpoints versionados
│   │   │   ├── core/            # Config, seguridad, dependencias
│   │   │   ├── models/          # Modelos MongoDB (ODM)
│   │   │   ├── schemas/         # Pydantic schemas
│   │   │   ├── services/        # Lógica de negocio
│   │   │   └── utils/           # Utilidades (PDF, email, push)
│   │   ├── tests/               # Tests con pytest
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/                # React + TypeScript PWA
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── Dockerfile
├── web-publica/                 # Proyecto 2: Web Pública
│   ├── backend/                 # PHP puro
│   │   ├── api/v1/              # Endpoints REST
│   │   ├── admin/               # Backoffice
│   │   ├── config/              # Configuración y conexión BD
│   │   ├── models/              # Modelos (DAO/Repository)
│   │   └── public/              # Punto de entrada
│   ├── frontend/                # HTML5 + CSS + TypeScript
│   │   ├── src/
│   │   └── assets/
│   ├── database/                # Migraciones SQL
│   └── Dockerfile
├── docs/                        # Documentación
│   ├── api/                     # Contratos OpenAPI
│   │   ├── openapi-intranet.yaml
│   │   └── openapi-web.yaml
│   ├── CONTEXTO_OFICIAL_PROYECTO.md
│   └── github-pages/            # Web de documentación API
├── docker-compose.yml           # Orquestación de todos los servicios
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular.git
cd ProyectoIntermodular

# 2. Copiar variables de entorno
cp .env.example .env
# Editar .env con los valores reales

# 3. Levantar con Docker
docker-compose up -d

# 4. Acceder
# Intranet Frontend: http://localhost:3000
# Intranet API:      http://localhost:8000/api/v1
# Web Pública:       http://localhost:8080
# Documentación API: https://daw2proyectointermodular.github.io/ProyectoIntermodular/
```

---

## 📖 Documentación de la API

La documentación interactiva de ambas APIs está disponible en **GitHub Pages**:

🔗 **[Ver Documentación API](https://daw2proyectointermodular.github.io/ProyectoIntermodular/)**

Incluye:
- Visor Swagger UI interactivo para probar endpoints
- Visor Redoc con documentación detallada
- Hoja visual de resumen (*cheatsheet*) de todos los endpoints

---

## 👥 Equipo

| Integrante | GitHub | Email |
|-----------|--------|-------|
| José Iver Peñarrieta | [@joseiverp](https://github.com/joseiverp) | 14499483@alu.murciaeduca.es |
| Francisco Guerrero | [@FranKisekis](https://github.com/FranKisekis) | 3728291@alu.murciaeduca.es |

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](./LICENSE).
