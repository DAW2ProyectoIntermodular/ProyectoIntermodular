# Backend de la intranet

API REST de la intranet de gestión docente, hecha con **FastAPI**, **MongoDB** y **Redis**. Implementa el contrato [`docs/api/openapi-intranet.yaml`](../../docs/api/openapi-intranet.yaml).

## Qué hay implementado

| Módulo | Rutas |
|---|---|
| Autenticación | `POST /api/v1/auth/login/google` · `POST /api/v1/auth/refresh` · `POST /api/v1/auth/logout` |
| Usuarios | `GET`/`PUT /api/v1/usuarios/me` · `GET`/`POST /api/v1/usuarios` · `GET`/`PUT`/`PATCH`/`DELETE /api/v1/usuarios/{usuario_id}` · `PUT /api/v1/usuarios/{usuario_id}/roles` |
| Departamentos | `GET`/`POST /api/v1/departamentos` · `GET`/`PUT /api/v1/departamentos/{departamento_id}` |

## Ponerlo en marcha

Con Docker, desde la raíz del repositorio:

```bash
cp .env.example .env
docker compose up --build
```

- API: <http://localhost:8000>
- Documentación interactiva (Swagger): <http://localhost:8000/docs>

Sin Docker (hacen falta MongoDB y Redis en marcha en el ordenador):

```bash
cd intranet/backend
python -m venv .venv
.venv\Scripts\activate          # en Linux o macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Primer acceso

Las altas las aprueba un administrador, así que el primero hay que crearlo al arrancar:

1. En el `.env`, pon tu correo en `PRIMER_ADMIN_EMAIL` y arranca la API. Se crea un usuario administrador con ese correo.
2. Inicia sesión:
   - **Con Google:** hace falta `GOOGLE_CLIENT_ID` en el `.env` (se obtiene en Google Cloud Console, credencial de tipo «ID de cliente de OAuth» para aplicación web). El frontend obtiene el token de identidad con Google Identity Services y lo envía a `POST /api/v1/auth/login/google`.
   - **Sin Google, solo en desarrollo:** `POST /api/v1/auth/login/dev` con `{"email": "tu-correo"}` devuelve los tokens de un usuario que ya existe. Esta ruta no existe cuando `ENVIRONMENT` no es `development`.
3. En Swagger, pulsa **Authorize** y pega el `access_token`.

## Cómo funciona la autenticación

- **Access token** (JWT, 30 minutos): se envía en cada petición como `Authorization: Bearer <token>`.
- **Refresh token** (JWT, 7 días): sirve para pedir un par nuevo en `/auth/refresh`. Cada refresh token vale **una sola vez**: al usarlo se revoca en Redis (rotación). `/auth/logout` también lo revoca.
- En cada petición se lee el usuario de la base de datos, así que un cambio de roles o una desactivación tienen efecto inmediato.
- Un usuario que entra con Google por primera vez queda en `pendiente_confirmacion` y recibe `403` hasta que un administrador lo aprueba con `PATCH /api/v1/usuarios/{usuario_id}`.

## Control de roles

Los endpoints declaran qué roles pueden usarlos con una dependencia:

```python
SoloAdmin = Annotated[dict, Depends(requiere_roles(Rol.ADMINISTRADOR))]

@router.post("")
async def crear_usuario(cuerpo: UsuarioCrear, _: SoloAdmin, db=Depends(get_db)):
    ...
```

El rol `administrador` tiene acceso a todo. Sin token se responde `401`; con token pero sin el rol necesario, `403`.

## Estructura

```text
app/
├── main.py              # Crea la aplicación, arranque y manejo de errores
├── api/v1/
│   ├── router.py        # Reúne los endpoints bajo /api/v1
│   └── endpoints/       # Una capa fina: recibe la petición y llama al servicio
├── core/
│   ├── config.py        # Variables de entorno
│   ├── database.py      # Conexión a MongoDB e índices
│   ├── cache.py         # Conexión a Redis
│   ├── security.py      # Crear y validar tokens JWT
│   ├── permisos.py      # Usuario autenticado y control de roles
│   └── errores.py       # Errores de negocio (401, 403, 404, 409, 422)
├── models/              # Valores permitidos y reglas de cada entidad
├── schemas/             # Esquemas Pydantic de entrada y salida
└── services/            # Lógica de negocio y acceso a datos
tests/                   # Tests con pytest
```

Una petición recorre siempre el mismo camino: **endpoint → servicio → base de datos**. Los servicios no saben nada de HTTP: si algo va mal lanzan un error de negocio (`NoEncontrado`, `Conflicto`…) y `main.py` lo convierte en la respuesta `{"detail": "..."}` con su código.

## Tests

```bash
cd intranet/backend
pytest
```

No necesitan MongoDB ni Redis: se sustituyen por versiones en memoria (`mongomock` y `fakeredis`). Cubren la autenticación, el control de roles y la gestión de usuarios. Se ejecutan también en GitHub en cada cambio (workflow `tests-backend.yml`).
