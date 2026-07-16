# Seguimiento de Actividades (Salidas de Oficina)

Aplicativo web para el seguimiento interno de un equipo: los funcionarios registran
cuándo salen de la oficina (soporte, reunión, trámite…) y la jefatura ve quién está
fuera y consulta el historial.

## Stack

- **Backend**: Flask (monolito, patrón *app factory*) que sirve templates Jinja **y** una API JSON.
- **Frontend**: Vue 3 desde CDN, montado sobre cascarones HTML. El frontend consume **solo** la API.
- **Auth**: login sin contraseña por cédula → **JWT** guardado en `localStorage`. API stateless.
- **Base de datos**: Turso (libSQL) con SQL crudo y patrón repositorio.

## Arquitectura (separación de responsabilidades)

```
app/
├── api/            # Endpoints JSON (auth, actividades, admin, usuarios, tipos)
├── auth/           # JWT + decoradores de autorización
├── repositories/   # Acceso a datos (SQL crudo). Sin lógica de negocio ni HTTP.
├── views/          # Rutas que sirven las páginas HTML
├── templates/      # Cascarones Jinja que montan las apps Vue
├── static/         # CSS y apps Vue (login, funcionario, admin)
├── db.py           # Cliente libSQL por request
└── config.py       # Configuración desde variables de entorno
scripts/sql/        # Scripts .sql para ejecutar en la base de datos
```

La API (`/api/...`) está desacoplada de las vistas. Para escalar, la SPA de Vue podría
separarse en su propio despliegue sin tocar el backend.

## Puesta en marcha

### 1. Dependencias

```bash
python -m venv venv
venv\Scripts\activate          # Windows (PowerShell/CMD)
# source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

### 2. Variables de entorno

```bash
copy .env.example .env         # Windows
# cp .env.example .env         # Linux/macOS
```

Edita `.env`:

- **Prueba local sin Turso** (recomendado para probar rápido):
  `TURSO_DATABASE_URL=file:local.db` y `TURSO_AUTH_TOKEN=` (vacío).
- **Turso real**: `TURSO_DATABASE_URL=libsql://<tu-db>-<org>.turso.io` y
  `TURSO_AUTH_TOKEN=<token>` (genera el token con `turso db tokens create <tu-db>`).

Cambia también `JWT_SECRET` por un valor largo y aleatorio.

### 3. Crear el esquema y datos iniciales

Ejecuta los scripts en `scripts/sql/` **en orden**: `001_schema.sql`, `002_indexes.sql`,
`003_seed_admin.sql`. **Antes** de correr el 003, edita la cédula del ADMIN
(`0000000000`) por la cédula real de la jefatura.

- **En Turso**:
  ```bash
  turso db shell <tu-db> < scripts/sql/001_schema.sql
  turso db shell <tu-db> < scripts/sql/002_indexes.sql
  turso db shell <tu-db> < scripts/sql/003_seed_admin.sql
  ```
- **En modo local** (archivo `local.db`), con el CLI de sqlite3:
  ```bash
  sqlite3 local.db < scripts/sql/001_schema.sql
  sqlite3 local.db < scripts/sql/002_indexes.sql
  sqlite3 local.db < scripts/sql/003_seed_admin.sql
  ```

### 4. Ejecutar

```bash
python run.py
```

Abre <http://localhost:5000>. Ingresa con la cédula del ADMIN (jefatura) o la del
funcionario demo (`1111111111`).

## Modelo de datos

- **usuarios**: `id`, `cedula` (único, login), `nombre`, `rol` (ADMIN|FUNCIONARIO), `activo`.
- **tipos_actividad**: `id`, `nombre`, `activo` (catálogo, solo ADMIN).
- **actividades**: `id`, `usuario_id`, `tipo_actividad_id`, `comentario` (obligatorio),
  `estado` (EN_CURSO|FINALIZADA|CANCELADA), `fecha_hora_inicio`, `fecha_hora_fin`.

Un índice único parcial (`ux_actividad_encurso`) garantiza a nivel de BD que un funcionario
no tenga más de una actividad `EN_CURSO` a la vez. Las fechas se guardan en UTC (ISO-8601)
y se muestran en hora local.

## API

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/api/auth/login` | público | Login por cédula → devuelve JWT |
| GET | `/api/actividades/actual` | funcionario | Actividad EN_CURSO propia (o null) |
| POST | `/api/actividades` | funcionario | Iniciar salida |
| PATCH | `/api/actividades/<id>/finalizar` | funcionario | Finalizar salida |
| PATCH | `/api/actividades/<id>/cancelar` | funcionario | Cancelar salida |
| GET | `/api/admin/dashboard` | admin | Funcionarios fuera ahora |
| GET | `/api/admin/actividades` | admin | Historial con filtros (`desde`, `hasta`, `usuario_id`, `estado`) |
| GET/POST | `/api/admin/usuarios` | admin | Listar / crear usuarios |
| PUT | `/api/admin/usuarios/<id>` | admin | Editar usuario |
| PATCH | `/api/admin/usuarios/<id>/estado` | admin | Activar / desactivar (soft delete) |
| GET | `/api/admin/tipos` | admin (o `?solo_activos=1` autenticado) | Listar tipos |
| POST | `/api/admin/tipos` | admin | Crear tipo |
| PUT | `/api/admin/tipos/<id>` | admin | Editar tipo |
| PATCH | `/api/admin/tipos/<id>/estado` | admin | Activar / desactivar (soft delete) |

## Nota de seguridad

El acceso solo con cédula es cómodo pero débil (las cédulas son semi-públicas). Mitigaciones
incluidas: solo usuarios activos pueden ingresar, JWT de expiración corta y *rate-limit* básico
en el login. Como mejora futura se puede añadir un PIN de 4 dígitos por usuario.
