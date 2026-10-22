# 📌 Estado del Proyecto y Guía de Continuación de Sesión

> **Para el Agente de Antigravity en cualquier máquina:**
> Este documento contiene el estado exacto en el que dejamos el proyecto el **22 de octubre de 2026**.
> Al abrir esta carpeta en cualquier ordenador (incluido el del instituto), lee este documento y `docs/CONTEXTO_OFICIAL_PROYECTO.md` para continuar sin perder nada de contexto.

---

## 👥 Datos del Equipo
* **Centro:** IES Ramón Arcas Meca (Totana, Murcia) — CFGS DAW2 (2026/2027)
* **Integrante 1:** José Iver Peñarrieta (`joseiverp` / `14499483@alu.murciaeduca.es`)
* **Integrante 2:** Francisco Guerrero (`FranKisekis` / `3728291@alu.murciaeduca.es`)
* **Repositorio GitHub:** [https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular](https://github.com/DAW2ProyectoIntermodular/ProyectoIntermodular)
* **Web de Documentación (GitHub Pages):** [https://daw2proyectointermodular.github.io/ProyectoIntermodular/](https://daw2proyectointermodular.github.io/ProyectoIntermodular/)
* **Hoja Visual Resumen (Cheatsheet A3/PDF):** [https://daw2proyectointermodular.github.io/ProyectoIntermodular/cheatsheet.html](https://daw2proyectointermodular.github.io/ProyectoIntermodular/cheatsheet.html)

---

## 🎯 Situación Actual: Entrega 1 (30 de octubre) — ¡COMPLETADA AL 100%!

Todos los requisitos oficiales de la 1ª Entrega han sido generados, auditados y corregidos:

1. **Estructura base del repositorio:**
   - Carpetas `intranet/` (FastAPI + React PWA) y `web-publica/` (PHP puro + MySQL).
   - `.gitignore`, `.env.example`, `LICENSE` (MIT) y `README.md`.
2. **Contrato OpenAPI de la Intranet (`docs/api/openapi-intranet.yaml`):**
   - 76 endpoints, 22 módulos operativos.
   - Autenticación JWT Bearer + Google OAuth2, control RBAC mediante dependencias.
   - **Corrección crítica realizada:** Se eliminó el `requestBody` en `DELETE /api/v1/notificaciones/suscripcion-push` y se transformó en parámetro de consulta (`query parameter`) para cumplir con la semántica HTTP.
   - **Estandarización OpenAPI 3.1:** Se migraron más de 770 `example` a `examples: [...]` y 75 `nullable: true` a `type: [T, "null"]`, eliminando todos los warnings y hints en Swagger Editor.
3. **Contrato OpenAPI de la Web Pública (`docs/api/openapi-web.yaml`):**
   - 48 endpoints (22 públicos sin autenticación + 26 del backoffice con sesión PHP `PHPSESSID`).
   - Normalización relacional 3FN en MySQL/MariaDB, relaciones N:M (departamentos-programas).
   - **Corrección realizada:** Se añadieron 42 descripciones técnicas faltantes en parámetros de consulta y path.
   - Migrados más de 340 `example` a `examples: [...]` para plena conformidad con JSON Schema 2020-12 / OpenAPI 3.1.
4. **Portal interactivo y GitHub Pages:**
   - Web interactiva accesible directamente en la raíz de GitHub Pages.
   - Incluye visor Swagger UI funcional, visor Redoc y hoja visual de resumen.
   - Hoja imprimible A3 (`cheatsheet.html`) con rutas canónicas completas.
   - Workflow en `.github/workflows/deploy-docs.yml` que compila y publica automáticamente.
5. **Historial Git cooperativo:**
   - Commits estructurados reflejando trabajo conjunto 50/50 con Co-authored-by.

---

## 📋 ¿Qué toca hacer a continuación?

El usuario ha pedido expresamente **no adelantar la 2ª entrega** hasta dejar la 1ª revisada y lista para la fecha oficial (30 de octubre).
Si se quiere continuar mejorando antes de la 2ª entrega:
- Verificar visualmente la visualización en Swagger Editor / Swagger UI.
- Exportar o verificar la impresión en PDF de `docs/cheatsheet.html`.
- Si se decide dar luz verde a la **2ª Entrega (30 de noviembre)**, las siguientes tareas son:
  - Fase 1 de la Intranet: Docker Compose de desarrollo (MongoDB + Redis + FastAPI).
  - Modelos ODM de MongoDB en Python y esquemas Pydantic.
  - Scaffolding de React + TypeScript (Vite + Tailwind / diseño PWA).
  - Estructura base de PHP puro para la Web Pública y script de creación de tablas MySQL (3FN).
