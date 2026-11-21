# Aplicación de atenciones médicas (Python + PostgreSQL)

## Puesta en marcha desde Visual Studio Code en macOS

### 1. Preparar Python

Abre la carpeta `atenciones` en Visual Studio Code y selecciona **Terminal → Nueva terminal**. Ejecuta desde esa carpeta:

```zsh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Conectarse a PostgreSQL

En la misma terminal, configura la conexión. La primera línea corresponde a PostgreSQL 18 instalado en `/Library/PostgreSQL/18`. Si `psql --version` ya funciona, puedes omitirla. Cambia `PGUSER` si usas un rol distinto de `postgres`.

```zsh
export PATH="/Library/PostgreSQL/18/bin:$PATH"
export PGHOST=127.0.0.1 PGPORT=5432 PGDATABASE=atenciones PGUSER=postgres
read -rs 'PGPASSWORD?Contraseña de PostgreSQL: '
export PGPASSWORD
printf '\n'
psql -d postgres -tAc "SELECT datname FROM pg_database WHERE datname = 'atenciones'"
```

Escribe la contraseña del rol de PostgreSQL cuando se solicite. Mientras escribes, la terminal deja el campo en blanco. Si el comando muestra `atenciones`, la base ya existe. Si termina correctamente sin mostrar un nombre, créala con `createdb atenciones`.

### 3. Crear las tablas y cargar la demostración

Ejecuta estos comandos una vez en una base vacía. Si ya tienes las tablas del proyecto con datos, pasa directamente al paso 4. `schema.sql` elimina y vuelve a crear las tablas `paciente`, `medico` y `atencion`.

```zsh
psql -d atenciones -v ON_ERROR_STOP=1 --single-transaction -f schema.sql
psql -d atenciones -v ON_ERROR_STOP=1 --single-transaction -f datos_prueba.sql
```

`datos_prueba.sql` es opcional. Sirve para mostrar la consulta de vigentes durante la evaluación.

### 4. Ejecutar y verificar

```zsh
python -m streamlit run app.py
```

Abre la dirección **Local URL** que muestra Streamlit, normalmente `http://localhost:8501`. En el menú lateral, elige **Atenciones vigentes → Ejecutar consulta**. Si acabas de cargar los datos de prueba, verás **3 atenciones vigentes**.

Para detener la aplicación, pulsa **Control+C** en la terminal. Si abres una terminal nueva, vuelve a activar `.venv` y a configurar la conexión del paso 2 antes de arrancar Streamlit. Los scripts SQL solo se necesitan al preparar una base vacía.

## Archivos
- `schema.sql`: tablas PACIENTE, MEDICO, ATENCION con PK/FK (`fecha_alta` acepta NULL)
- `datos_prueba.sql`: 3 pacientes, 3 médicos, 5 atenciones (2 con alta, 3 vigentes)
- `db.py`: conexión y funciones `consultar` / `ejecutar`
- `app.py`: interfaz (ingresar, modificar, atenciones vigentes)

## Cómo se cubre cada punto de la tarea
| Punto | Dónde |
|---|---|
| Python + PostgreSQL | `db.py` (psycopg2) |
| Interfaz | Menú lateral en `app.py` |
| Ingresar con formularios | `pagina_ingresar` (3 tablas; paciente y médico por lista desplegable en Atención) |
| Modificar (consultando antes) | `pagina_modificar`: muestra la tabla, se elige un registro y se edita |
| Consulta de vigentes | `pagina_vigentes`: `WHERE fecha_alta IS NULL` |

## Para explicar en la revisión
- Las consultas usan parámetros (`%s`), no concatenan texto.
- `ejecutar` hace commit/rollback; `consultar` devuelve un DataFrame.
- "Vigente" = `fecha_alta IS NULL`; en los formularios se deja sin marcar "fecha de alta".
