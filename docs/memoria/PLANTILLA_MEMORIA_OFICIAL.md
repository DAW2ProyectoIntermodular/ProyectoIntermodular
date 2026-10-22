# MEMORIA DEL PROYECTO INTERMODULAR
## CFGS Desarrollo de Aplicaciones Web (DAW2) — Curso 2026/2027
### IES Ramón Arcas Meca (Lorca, Murcia)

---

> **Normas Formales de Redacción:**
> - Fuente: Arial 11 pt, interlineado 1,5, márgenes de 2,54 cm en los cuatro lados.
> - Texto justificado, páginas numeradas abajo a la derecha (portada sin numerar).
> - Extensión: aproximadamente 15 páginas por alumno (sin contar portada, índice ni anexos).
> - Citas y referencias bibliográficas en estricto formato **APA 7.ª edición** (sangría francesa).
> - Índice de similitud antiplagio inferior al 25%.

---

## 1. PORTADA
- **Título del Proyecto:** Plataforma Digital Integral para el IES Ramón Arcas Meca: Intranet Transaccional de Gestión Docente y Portal Web Institucional Accesible.
- **Ciclo Formativo:** 2º Curso de Grado Superior en Desarrollo de Aplicaciones Web.
- **Centro Educativo:** IES Ramón Arcas Meca.
- **Autores:**
  - José Iver Peñarrieta Villcasana (14499483@alu.murciaeduca.es)
  - Francisco Guerrero (3728291@alu.murciaeduca.es)
- **Tutor / Profesor Evaluador:** [Nombre del Tutor]
- **Fecha de Entrega:** [Fecha oficial de entrega]

---

## 2. RESUMEN / ABSTRACT
### 2.1 Resumen en Español (200 - 300 palabras)
[Breve descripción del problema detectado en la gestión del centro, los dos productos digitales desarrollados (Intranet privada FastAPI/React y Web pública PHP/MySQL), la metodología ágil seguida (Scrum, Git 50/50, Jira, IA) y los principales resultados obtenidos].

### 2.2 Abstract en Inglés
[Traducción fiel del resumen al idioma inglés técnico].

### 2.3 Palabras Clave / Keywords
- **Español:** Intranet docente, API REST, OpenAPI 3.1, FastAPI, PHP nativo, PWA, Gestión de guardias, Accesibilidad WCAG, RGPD.
- **English:** Educational Intranet, RESTful API, OpenAPI 3.1, FastAPI, Native PHP, PWA, On-duty Teacher Scheduling, WCAG Accessibility, GDPR.

---

## 3. INTRODUCCIÓN
### 3.1 Contexto y Justificación
[Justificación de la necesidad de modernizar la infraestructura digital del IES Ramón Arcas Meca, separando la operativa confidencial de la información pública].

### 3.2 Objetivos del Proyecto
#### Objetivo General:
Desarrollar e implantar dos productos digitales desacoplados que optimicen la gestión docente y la presencia web institucional del IES Ramón Arcas Meca.

#### Objetivos Específicos (en infinitivo):
- **OE1:** Diseñar y validar contratos de API REST bajo OpenAPI 3.1 en español y sin framework en la parte pública.
- **OE2:** Implementar una Intranet privada con FastAPI, MongoDB y Redis con autenticación JWT y roles granulares.
- **OE3:** Desarrollar un algoritmo equitativo de asignación de guardias por rondas y contadores por tramo horario.
- **OE4:** Diseñar una interfaz PWA adaptativa (escritorio tipo sidebar, móvil tipo iOS).
- **OE5:** Construir un portal web público en PHP puro accesible (WCAG 2.1 AA) con panel CRUD para secretaría y noticias.
- **OE6:** Automatizar pruebas unitarias y de integración con `pytest` alcanzando una cobertura superior al 80%.

### 3.3 Alcance y Limitaciones
[Definición de lo que abarca el proyecto y las fronteras de los sistemas externos: Google Workspace, OpenStreetMap/Nominatim, firma biométrica].

---

## 4. ANÁLISIS Y CONTEXTUALIZACIÓN DE EMPRESAS DEL SECTOR (APORTACIÓN INDIVIDUAL)

### 4.1 Aportación Individual — Integrante 1: José Iver Peñarrieta
#### 4.1.1 Caracterización de la Empresa / Subsector TIC (CNAE 6201)
- Análisis DAFO (Debilidades, Amenazas, Fortalezas, Oportunidades).
- Análisis PESTEL (Político, Económico, Social, Tecnológico, Ecológico, Legal).
#### 4.1.2 Catálogo de Productos y Servicios
#### 4.1.3 Contribución a los Objetivos de Desarrollo Sostenible (ODS)
- ODS 4 (Educación de Calidad) y ODS 9 (Industria, Innovación e Infraestructura).
#### 4.1.4 Prevención de Riesgos Laborales en el Sector del Desarrollo Web
- Aplicación de la Ley 31/1995 de Prevención de Riesgos Laborales y Real Decreto 488/1997 sobre pantallas de visualización de datos (PVD), ergonomía, pausas y fatiga visual/mental.
#### 4.1.5 Conclusiones del Análisis Individual

### 4.2 Aportación Individual — Integrante 2: Francisco Guerrero
#### 4.2.1 Caracterización de la Empresa / Subsector TIC
- Análisis DAFO y PESTEL.
#### 4.2.2 Catálogo de Productos y Servicios
#### 4.2.3 Contribución a los Objetivos de Desarrollo Sostenible (ODS)
#### 4.2.4 Prevención de Riesgos Laborales en Puestos de Trabajo Informáticos
- Medidas de prevención ergonómica, riesgos psicosociales y adaptación del puesto.
#### 4.2.5 Conclusiones del Análisis Individual

---

## 5. DESARROLLO DEL PROYECTO
### 5.1 Metodología de Trabajo
- Metodología Ágil (Scrum/Kanban) gestionada mediante Atlassian Jira.
- Flujo de trabajo en Git con ramas por funcionalidad y reparto estricto 50/50.
- Declaración ética del uso de herramientas de Inteligencia Artificial como copiloto asistivo de desarrollo y revisión arquitectónica.

### 5.2 Planificación y Temporalización (Diagrama de Gantt)
- Cronograma de las 4 entregas del curso 2026/2027.

### 5.3 Actividades Realizadas y Relación con los Módulos de DAW
| Módulo Profesional del Ciclo | Actividades Concretas en el Proyecto |
|---|---|
| **Sistemas Informáticos** | Despliegue con Docker, Docker Compose y variables de entorno `.env`. |
| **Bases de Datos** | Diseño NoSQL en MongoDB y modelo relacional 3FN con claves foráneas en MySQL. |
| **Programación** | Algoritmos de guardias, estructuras de datos, POO y validaciones Pydantic. |
| **Lenguajes de Marcas (LMSGI)** | Contratos OpenAPI 3.1 (YAML), sitemap XML y validación JSON Schema. |
| **Entornos de Desarrollo** | Control de versiones Git, GitHub Actions (CI/CD) y Jira. |
| **Desarrollo Web en Entorno Cliente (DWEC)** | React, TypeScript, PWA, Service Workers y consumo de APIs REST. |
| **Desarrollo Web en Entorno Servidor (DWES)** | Backend FastAPI (Python) y Backend PHP nativo sin framework. |
| **Diseño de Interfaces Web (DIW)** | UI/UX responsivo, menú lateral Claude/Gemini, interfaz móvil iOS, pautas WCAG. |
| **Despliegue de Aplicaciones Web (DAW)** | Despliegue en GitHub Pages, Dockerización de servicios y Nginx. |
| **Empresa e Iniciativa Emprendedora (EIE)** | Análisis DAFO/PESTEL, costes y viabilidad de implantación. |
| **Proyecto Intermodular** | Integración transversal de ambos productos digitales. |

### 5.4 Recursos y Stack Tecnológico Detallado

---

## 6. RESULTADOS Y ANÁLISIS
### 6.1 Matriz de Consecución de Objetivos (OE1 .. OE6)
### 6.2 Cobertura de Pruebas Automatizadas (pytest)
### 6.3 Auditoría de Rendimiento y Accesibilidad (Lighthouse / WCAG)
### 6.4 Verificación de Cumplimiento RGPD

---

## 7. CONCLUSIONES Y LÍNEAS FUTURAS
### 7.1 Conclusiones
### 7.2 Recomendaciones y Trabajo Futuro

---

## BIBLIOGRAFÍA (APA 7.ª EDICIÓN)
[Referencias con sangría francesa e inclusión de herramientas de IA declaradas].

---

## ANEXOS
- **Anexo I:** Documentación Técnica, Diagramas de Arquitectura y Contratos OpenAPI 3.1.
- **Anexo II:** Evidencias Multimedia del Sistema (Capturas numeradas con licencia propia).
- **Anexo III:** Ficha de Autoevaluación Individual (Escala 1 - 4).
- **Anexo IV:** Ficha de Coevaluación Interpares (Escala 1 - 4).
