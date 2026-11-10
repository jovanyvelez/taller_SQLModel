# 🦸 API de Héroes con FastAPI + SQLModel

Guía paso a paso de este proyecto.

Es una API pequeña: guarda **héroes** en una base de datos SQLite y los publica como
endpoints REST. No tiene pantallas ni formularios: todo se prueba desde una página web
que genera FastAPI automáticamente (`/docs`).

Con este proyecto vas a entender cómo se conectan cuatro ideas:

```
Modelo (clase de Python)  →  Tabla (base de datos)  →  Endpoints (API)  →  /docs
```

---

## Índice

1. [Antes de empezar](#1-antes-de-empezar)
2. [Cómo ejecutar el proyecto](#2-cómo-ejecutar-el-proyecto)
3. [Estructura de archivos](#3-estructura-de-archivos)
4. [Paso 1: El modelo (la tabla)](#paso-1-el-modelo-la-tabla)
5. [Paso 2: El engine (la conexión)](#paso-2-el-engine-la-conexión)
6. [Paso 3: Crear las tablas](#paso-3-crear-las-tablas)
7. [Paso 4: La sesión](#paso-4-la-sesión)
8. [Paso 5: El lifespan](#paso-5-el-lifespan)
9. [Paso 6: La dependencia](#paso-6-la-dependencia)
10. [Paso 7: Los endpoints](#paso-7-los-endpoints)
11. [Cómo probar la API](#cómo-probar-la-api)
12. [Errores comunes](#errores-comunes)
13. [Detalles que podemos mejorar](#detalles-que-podemos-mejorar)
14. [Glosario](#glosario)
15. [Siguiente paso: los talleres](#siguiente-paso-los-talleres)

---

## 1. Antes de empezar

Solo necesitas **Python 3.10 o superior**. `pip` viene incluido con Python, así que no
hay que instalar nada más.

| Herramienta | Para qué | Cómo comprobarla |
|---|---|---|
| **Python 3.10 o superior** | Ejecutar el código | `python --version` |
| **pip** | Instalar las librerías | `pip --version` |

> En Windows, si `python` no responde, prueba con `py --version`. En macOS o Linux,
> prueba con `python3 --version`. Si `pip` no aparece, prueba con
> `python -m pip --version`.

---

## 2. Cómo ejecutar el proyecto

Desde la carpeta del proyecto, en la terminal:

**1. Crear el entorno virtual** (solo la primera vez)

```bash
python -m venv .venv
```

**2. Activarlo** (elige tu sistema operativo)

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

En Windows con **cmd** (no PowerShell) el comando es `.venv\Scripts\activate.bat`.

Cuando el entorno está activo, la línea de la terminal empieza con `(.venv)`. Cada vez
que abras una terminal nueva tendrás que activarlo otra vez (paso 2).

> **Windows y PowerShell:** si al activar aparece un error sobre "ejecución de scripts
> deshabilitada", ejecuta
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a intentarlo;
> o usa la terminal **cmd** en lugar de PowerShell.

**3. Instalar las dependencias** (solo la primera vez)

```bash
pip install -r requirements.txt
```

Si no tienes el archivo `requirements.txt`, instala las dos librerías directamente:

```bash
pip install "fastapi[standard]" sqlmodel
```

**4. Arrancar el servidor** (cada vez que quieras trabajar)

```bash
fastapi dev main.py
```

> 💡 Si el comando `fastapi` no aparece, usa `python -m fastapi dev main.py`.

Vas a ver algo parecido a esto:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...] using WatchFiles
INFO:     Application startup complete.
```

Fíjate en dos cosas:

- **Recarga automática**: `fastapi dev` reinicia el servidor cada vez que guardas un
  archivo. No hay que apagarlo y prenderlo.
- `echo=True` (lo verás en `database.py`): el SQL que se ejecuta aparece en la consola.
  Es como mirar "por debajo del capó". Con el tiempo puedes ponerlo en `False`.

Abre en el navegador:

👉 **http://127.0.0.1:8000/docs**

Ahí está la documentación interactiva de la API. También existe
**http://127.0.0.1:8000/redoc** (la misma información, en otro formato).

Para detener el servidor: `Ctrl + C`.

> **Si el puerto 8000 está ocupado**, usa otro: `fastapi dev main.py --port 8001`

En la primera ejecución se crea el archivo `database.db` en la carpeta del proyecto.
Ese archivo **es** la base de datos.

---

## 3. Estructura de archivos

El proyecto es pequeño a propósito: solo dos archivos de Python.

```
javiera_sqlmodel/
├── database.py       ← el modelo (la tabla) y la conexión a la base de datos
├── main.py           ← los endpoints de la API
├── requirements.txt  ← las librerías que hay que instalar
├── database.db       ← la base de datos SQLite (se crea sola al ejecutar)
└── README.md         ← esta guía
```

> Si en tu copia aparecen `pyproject.toml` y `uv.lock`, ignóralos: son de **uv**, otro
> gestor de paquetes. Con `pip` solo necesitas `requirements.txt`.

La idea es simple:

| Archivo | Se encarga de… |
|---|---|
| `database.py` | **Qué** se guarda y **dónde** |
| `main.py` | **Cómo** se consulta y se modifica desde la API |

---

## Paso 1: El modelo (la tabla)

Abre `database.py`. Lo primero que aparece es esto:

```python
class HeroeBase(SQLModel):
    nombre: str = Field(index=True)
    nombre_secreto: str
    edad: int | None = Field(default=None, index=True)
```

`HeroeBase` **no es una tabla**: es solo una lista de campos. Piensa en ella como el
"molde" de los datos de un héroe.

| Campo | Tipo | ¿Obligatorio? | Nota |
|---|---|---|---|
| `nombre` | texto | Sí | `index=True` → búsquedas más rápidas |
| `nombre_secreto` | texto | Sí | |
| `edad` | número entero | No | `int \| None` significa "entero o vacío" |

Un truco para leer los tipos:

- `str` → texto
- `int` → número entero
- `bool` → verdadero/falso
- `int | None` → "número **o** nada". La barra `|` se lee **"o"**.

Después viene la tabla de verdad:

```python
class Heroe(HeroeBase, table=True):
    __tablename__: str = "heroes"
    id: int | None = Field(default=None, primary_key=True)
```

Aquí pasan tres cosas importantes:

1. **`table=True`** → esta clase sí es una tabla en la base de datos.
   Sin esa palabra, `Heroe` sería solo otra clase de Python.
2. **`__tablename__ = "heroes"`** → el nombre real de la tabla en SQL.
3. **`id` con `primary_key=True`** → la **clave primaria**: el número único que identifica
   a cada héroe. La base de datos lo genera sola, por eso empieza en `None`
   (todavía no existe hasta que se guarda).

> 💡 **¿Por qué `Heroe` hereda de `HeroeBase`?** Para no repetir los campos. `HeroeBase`
> tiene los datos que se piden al crear un héroe; `Heroe` añade el `id` y se convierte
> en tabla. Lo mismo que un formulario (datos) y el archivador donde se guarda.

---

## Paso 2: El engine (la conexión)

```python
DATA_BASE_URL = "sqlite:///database.db"
connects_args = {"check_same_thread": False}

engine = create_engine(DATA_BASE_URL, connect_args=connects_args, echo=True)
```

- **`sqlite:///database.db`** → usa SQLite y guarda todo en el archivo `database.db`.
  Tres barras `///` significan "ruta relativa a esta carpeta".
- **`connect_args={"check_same_thread": False}`** → SQLite es celoso con los hilos
  (threads). FastAPI atiende varias peticiones a la vez, así que hay que decirle que sí
  permita compartir la conexión.
- **`echo=True`** → imprime en la consola cada instrucción SQL que se ejecuta.
  Perfecto para aprender; en un proyecto real normalmente va en `False`.

El **engine** es la "puerta de entrada" a la base de datos. Se crea **una sola vez**
para todo el programa.

---

## Paso 3: Crear las tablas

```python
def crear_db_y_tablas():
    SQLModel.metadata.create_all(engine)
```

`SQLModel.metadata` es el catálogo de todas las tablas que declaraste con `table=True`.
`create_all(engine)` crea las que **faltan**.

> ⚠️ **Muy importante:** `create_all` **no modifica** tablas que ya existen.
> Si después le agregas un campo al modelo, la tabla vieja se queda como estaba.
> En este proyecto de aprendizaje la solución es simple: **borra `database.db`**
> y arranca de nuevo. (En proyectos grandes se usan *migraciones*, como Alembic.)

Cuando arranca la aplicación, en la consola aparece el SQL real de la tabla:

```sql
CREATE TABLE heroes (
    nombre VARCHAR NOT NULL,
    nombre_secreto VARCHAR NOT NULL,
    edad INTEGER,
    id INTEGER NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX ix_heroes_nombre ON heroes (nombre);
CREATE INDEX ix_heroes_edad ON heroes (edad);
```

Esas dos últimas líneas son los índices que pediste con `index=True`: son como el
índice de un libro, permiten encontrar filas sin leer la tabla completa.

---

## Paso 4: La sesión

```python
def get_session():
    with Session(engine) as session:
        yield session
```

Una **sesión** es una conversación con la base de datos: por ella pasan las consultas
y los cambios (`commit`). Al terminar, se cierra sola gracias al `with`.

La palabra `yield` es la clave: entrega la sesión, **pausa** la función, y cuando el
endpoint termina, continúa y cierra la sesión.

---

## Paso 5: El lifespan

En `main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_db_y_tablas()
    yield

app = FastAPI(lifespan=lifespan)
```

`lifespan` son los "eventos de vida" de la aplicación:

- Lo que está **antes** del `yield` → se ejecuta **al arrancar** (aquí: crear tablas).
- Lo que está **después** del `yield` → se ejecuta **al apagar** (aquí: nada).

Así te aseguras de que las tablas existan antes de que llegue la primera petición.

---

## Paso 6: La dependencia

```python
session_dependency = Annotated[Session, Depends(get_session)]
```

Esta línea es una **dependencia de FastAPI**. Se lee así:

> "Cada vez que un endpoint necesite una sesión, llama a `get_session` y pásasela."

Después, en cualquier endpoint basta con escribir `session: session_dependency` y FastAPI
se encarga de abrirla y cerrarla. No hay que crear sesiones a mano en cada función.

---

## Paso 7: Los endpoints

Un **endpoint** es una dirección (URL) + un método HTTP. Juntos forman el **CRUD**:

| Método | Ruta | Acción | En el CRUD |
|---|---|---|---|
| `POST` | `/heroes/` | Crear un héroe | **C**reate |
| `GET` | `/heroes/` | Listar todos | **R**ead |
| `PUT` | `/heroes/{hero_id}` | Actualizar uno | **U**pdate |
| `DELETE` | `/heroes/{hero_id}` | Borrar uno | **D**elete |

`{hero_id}` es un **parámetro de ruta**: en `/heroes/3`, vale `3`.

### 7.1 Crear un héroe — `POST /heroes/`

```python
@app.post("/heroes/", response_model=Heroe)
def create_hero(heroe: HeroeBase, session: session_dependency):
    new_heroe = Heroe.model_validate(heroe)
    session.add(new_heroe)
    session.commit()
    session.refresh(new_heroe)
    return new_heroe
```

Paso a paso:

1. `heroe: HeroeBase` → FastAPI lee el JSON que llega y lo valida contra el modelo.
   Si falta un campo obligatorio, responde **422** automáticamente.
2. `Heroe.model_validate(heroe)` → convierte los datos en un objeto `Heroe`
   (el que sabe guardarse).
3. `session.add(...)` → lo deja "listo para guardar".
4. `session.commit()` → **guarda de verdad** en la base de datos.
5. `session.refresh(...)` → vuelve a leerlo para traer el `id` que generó la base de datos.

> `response_model=Heroe` indica qué forma tiene la respuesta. Así, si devuelves algo que
> no encaja, la documentación y la validación te avisan.

### 7.2 Listar héroes — `GET /heroes/`

```python
@app.get("/heroes/", response_model=list[Heroe])
def ver_heroes(session: session_dependency):
    consulta = select(Heroe)
    return session.exec(consulta).all()
```

- `select(Heroe)` → "tráeme todos los héroes" (equivale a `SELECT * FROM heroes`).
- `session.exec(...)` → ejecuta la consulta.
- `.all()` → devuelve la lista de resultados.

Si la tabla está vacía, la respuesta es `[]`.

### 7.3 Actualizar un héroe — `PUT /heroes/{hero_id}`

```python
@app.put("/heroes/{hero_id}", response_model=Heroe)
def update_hero(hero_id: int, updated_hero: HeroeBase, session: session_dependency):
    heroe = session.get(Heroe, hero_id)
    if heroe is None:
        return {"error": "Heroe no encontrado"}

    heroe.nombre = updated_hero.nombre
    heroe.nombre_secreto = updated_hero.nombre_secreto
    heroe.edad = updated_hero.edad

    session.add(heroe)
    session.commit()
    session.refresh(heroe)
    return heroe
```

1. `session.get(Heroe, hero_id)` → busca por clave primaria. Devuelve `None` si no existe.
2. Se copian los campos nuevos uno por uno.
3. `commit()` guarda los cambios y `refresh()` devuelve los datos actualizados.

> `PUT` reemplaza **todos** los campos. Por eso `updated_hero` es un `HeroeBase`
> completo: hay que enviar `nombre`, `nombre_secreto` y `edad`.

### 7.4 Borrar un héroe — `DELETE /heroes/{hero_id}`

```python
@app.delete("/heroes/{hero_id}", response_model=Heroe)
def delete_hero(hero_id: int, session: session_dependency):
    heroe = session.get(Heroe, hero_id)
    if heroe is None:
        return {"error": "Heroe no encontrado"}
    data = Heroe.model_validate(heroe)
    session.delete(heroe)
    session.commit()
    return data
```

Fíjate en el orden: **primero se copia** (`data = Heroe.model_validate(heroe)`) y
**después se borra**. Si intentaras leer el objeto después del `commit`, ya no existiría
en la base de datos y daría error.

---

## Cómo probar la API

### Opción A: la página `/docs` (la más fácil)

1. Abre http://127.0.0.1:8000/docs
2. Haz clic en `POST /heroes/` → botón **Try it out**.
3. Reemplaza el ejemplo por:

   ```json
   {
     "nombre": "Superman",
     "nombre_secreto": "Clark Kent",
     "edad": 35
   }
   ```

4. Clic en **Execute**. Abajo verás la respuesta:

   ```json
   {
     "nombre_secreto": "Clark Kent",
     "edad": 35,
     "id": 1,
     "nombre": "Superman"
   }
   ```

5. Prueba `GET /heroes/` → **Execute**. Debe aparecer una lista con el héroe.
6. Prueba `PUT /heroes/1` con otros datos, y luego `DELETE /heroes/1`.

El orden de los campos en el JSON puede variar: no importa, es lo mismo.

### Opción B: la terminal con `curl`

```bash
# Crear
curl -X POST http://127.0.0.1:8000/heroes/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Wonder Woman","nombre_secreto":"Diana Prince","edad":30}'

# Listar
curl http://127.0.0.1:8000/heroes/

# Actualizar
curl -X PUT http://127.0.0.1:8000/heroes/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Wonder Woman","nombre_secreto":"Diana","edad":31}'

# Borrar
curl -X DELETE http://127.0.0.1:8000/heroes/1
```

### Opción C: mirar la base de datos directamente

```bash
sqlite3 database.db "SELECT * FROM heroes;"
```

Si no tienes `sqlite3` instalado, abre `database.db` con un programa visual como
**DB Browser for SQLite**. Vas a ver la tabla `heroes` con los datos que guardaste.

### Mirar el SQL que se ejecuta

Con `echo=True`, cada petición imprime en la consola algo como:

```
INSERT INTO heroes (nombre, nombre_secreto, edad) VALUES (?, ?, ?)
SELECT ... FROM heroes
```

Es la mejor forma de entender qué está haciendo la librería por ti.

---

## Errores comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Address already in use` | El puerto 8000 está ocupado | Usa `--port 8001` o cierra el otro servidor |
| `ModuleNotFoundError: fastapi` | No instalaste las dependencias o el entorno no está activo | Activa `.venv` e instala: `pip install -r requirements.txt` |
| `fastapi: command not found` | El entorno virtual no está activado | Actívalo, o usa `python -m fastapi dev main.py` |
| `no such table: heroes` | No pasaste por el `lifespan` o estás en otra carpeta | Arranca con `fastapi dev main.py` desde la carpeta del proyecto |
| Cambié el modelo y no se refleja | `create_all` no modifica tablas existentes | Borra `database.db` y reinicia |
| `422 Unprocessable Entity` | Falta un campo obligatorio o el tipo no coincide | Revisa el JSON: `nombre` y `nombre_secreto` son obligatorios |
| `500 Internal Server Error` con "response validation" | El endpoint devuelve algo que no encaja con `response_model` | Ver el punto siguiente |

En Windows, para borrar la base de datos usa `del database.db`; en macOS/Linux, `rm database.db`.

---

## Detalles que podemos mejorar

Estos puntos no están "mal" para aprender, pero son buenas conversaciones (y buenos
retos):

1. **No existe `GET /heroes/{hero_id}`.** Se pueden listar todos, pero no pedir uno solo.
2. **Si pides un héroe que no existe, la API responde `200` con datos vacíos.** Mira lo
   que devuelve hoy `PUT /heroes/99`:

   ```json
   {"edad": null, "id": null}
   ```

   ¿Por qué? Porque el endpoint devuelve un diccionario `{"error": ...}` para un
   `response_model=Heroe`. FastAPI intenta convertirlo en un héroe, no encuentra los
   campos y los deja vacíos. Lo correcto sería lanzar un código **404**:

   ```python
   from fastapi import HTTPException, status

   if heroe is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Heroe no encontrado",
       )
   ```

3. **`POST` responde `200` al crear.** Lo habitual en una API REST es `201 Created`:
   `@app.post("/heroes/", status_code=201)`.
4. **`PUT` exige todos los campos.** Un `PATCH` permitiría enviar solo el campo que
   cambia (`edad`, por ejemplo).
5. **`nombre_secreto` se muestra en todas las respuestas.** En un caso real, esa sería
   información privada que no debería salir en el `GET`. Se resuelve con un modelo
   aparte (por ejemplo `HeroePublic` sin ese campo).

¿Te animas a arreglar alguno? Es justo lo que piden los talleres.

---

## Glosario

| Palabra | Significado rápido |
|---|---|
| **Modelo** | Clase de Python que describe los datos |
| **Tabla** | Donde se guardan los datos, como una hoja de cálculo |
| **Fila / registro** | Un elemento de la tabla (un héroe) |
| **Columna / campo** | Un dato de todos los registros (`nombre`, `edad`…) |
| **Clave primaria** | Número único que identifica cada fila (`id`) |
| **Índice** | Estructura que acelera las búsquedas por un campo |
| **ORM** | Librería que traduce clases de Python a tablas SQL (aquí, SQLModel) |
| **Engine** | La conexión con la base de datos |
| **Sesión** | Una conversación con la base de datos |
| **`commit()`** | Guardar los cambios de verdad |
| **Dependencia** | Algo que FastAPI prepara y entrega a los endpoints |
| **Endpoint** | Una URL + un método HTTP |
| **CRUD** | Crear, Leer, Actualizar, Borrar |
| **JSON** | Formato de texto para enviar y recibir datos |
| **422** | Error: los datos enviados no son válidos |
| **404** | Error: lo que buscas no existe |

---

## Siguiente paso: los talleres

Ahora que entiendes el proyecto, es tu turno. Hay dos talleres para hacer **en parejas**:

1. **[Taller 1 — Mi Playlist](talleres/taller_1_playlist_una_tabla.md)**:
   un CRUD de una sola tabla, muy parecido a este proyecto.
2. **[Taller 2 — Artistas y Canciones](talleres/taller_2_artistas_y_canciones.md)**:
   el mismo estilo, pero con **dos tablas relacionadas**.

### Una regla para los dos talleres

Los talleres se resuelven con lo que aprendiste en esta guía y en el tutorial. Si quieres
usar algo que **no aparece** en ninguno de los dos (otra librería, autenticación, pruebas
automáticas, una metodología de trabajo…), puedes hacerlo, pero debes entregar aparte un
documento `JUSTIFICACION.md` que explique **qué** usaste, **qué necesidad** resolvía y
**qué riesgo** trae.

Los grupos que lo hagan serán los **invitados a exponer su proyecto en detalle** ante
sus compañeros. El molde del documento está en cada taller.

La documentación oficial (en inglés, pero con ejemplos de código muy claros) está en
👉 https://sqlmodel.tiangolo.com/tutorial/

Consejo para leerla: no hace falta entender todo el texto; mira los bloques de código,
cópialos en tu editor y ejecútalos. El navegador puede traducir la página.
