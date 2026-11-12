# ⚽ API de Equipos y Jugadores con FastAPI + SQLModel

Guía paso a paso de este proyecto.

Ejemplo de **una sola relación: muchos a muchos (N:M)**.

- Un equipo tiene muchos jugadores en su plantilla.
- Un jugador puede estar en varios equipos: el de la liga profesional y, por ejemplo,
  el de un torneo recreacional.

Eso no cabe en una columna de ninguna de las dos tablas, así que se resuelve con una
**tabla intermedia**. Ese es el tema del proyecto.

Se prueba desde `http://127.0.0.1:8000/docs`, sin pantallas ni formularios.

---

## Índice

1. [Antes de empezar](#1-antes-de-empezar)
2. [Cómo ejecutar el proyecto](#2-cómo-ejecutar-el-proyecto)
3. [Estructura de archivos](#3-estructura-de-archivos)
4. [Las tres tablas](#4-las-tres-tablas)
5. [Paso 1: ¿Por qué hace falta una tabla intermedia?](#paso-1-por-qué-hace-falta-una-tabla-intermedia)
6. [Paso 2: El modelo](#paso-2-el-modelo)
7. [Paso 3: Los modelos de la API](#paso-3-los-modelos-de-la-api)
8. [Paso 4: La aplicación](#paso-4-la-aplicación)
9. [Paso 5: Los endpoints](#paso-5-los-endpoints)
10. [Probarlo paso a paso](#probarlo-paso-a-paso)
11. [Mirar la tabla intermedia](#mirar-la-tabla-intermedia)
12. [¿Para qué sirve el muchos a muchos?](#para-qué-sirve-el-muchos-a-muchos)
13. [Errores comunes](#errores-comunes)
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
Cuando el entorno está activo, la línea de la terminal empieza con `(.venv)`.

> **Windows y PowerShell:** si al activar aparece un error sobre "ejecución de scripts
> deshabilitada", ejecuta
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a intentarlo;
> o usa la terminal **cmd** en lugar de PowerShell.

**3. Instalar las dependencias** (solo la primera vez)

```bash
pip install -r requirements.txt
```

**4. Arrancar el servidor** (cada vez que quieras trabajar)

```bash
fastapi dev main.py
```

> 💡 Si el comando `fastapi` no aparece, usa `python -m fastapi dev main.py`.

Abre en el navegador:

👉 **http://127.0.0.1:8000/docs**

Para detener el servidor: `Ctrl + C`.

> **Si el puerto 8000 está ocupado:** `fastapi dev main.py --port 8001`

En la primera ejecución se crea el archivo `database.db`. Ese archivo **es** la base de
datos.

---

## 3. Estructura de archivos

```
javiera_sqlmodel/
├── database.py       ← las tres tablas, la relación y la conexión
├── routes.py         ← los endpoints (/equipos y /jugadores)
├── main.py           ← crea la aplicación y conecta las rutas
├── requirements.txt  ← las librerías que hay que instalar
├── database.db       ← la base de datos SQLite (se crea sola al ejecutar)
└── README.md         ← esta guía
```

| Archivo | Se encarga de… |
|---|---|
| `database.py` | **Qué** se guarda, **cómo se relacionan** las tablas y **dónde** |
| `routes.py` | **Cómo** se consulta y se modifica desde la API |
| `main.py` | Arrancar la app y **conectar** `routes.py` |

---

## 4. Las tres tablas

```
equipos                                    jugadores
┌────┬────────────────────┬───────────┐    ┌────┬────────────┬────────────┬────────┐
│ id │ nombre             │ ciudad    │    │ id │ nombre     │ posicion   │ dorsal │
├────┼────────────────────┼───────────┤    ├────┼────────────┼────────────┼────────┤
│ 1  │ Atlético Nacional  │ Medellín  │    │ 1  │ Juan Pérez │ delantero  │ 9      │
│ 2  │ Los Cracks FC      │ Medellín  │    └────┴────────────┴────────────┴────────┘
└────┴────────────────────┴───────────┘
         ▲        ▲
         │        │
    equipo_jugador_link
    ┌────────────┬───────────┐
    │ jugador_id │ equipo_id │
    ├────────────┼───────────┤
    │ 1          │ 1         │  ← juega en la liga profesional
    │ 1          │ 2         │  ← y en el torneo recreacional
    └────────────┴───────────┘
```

Dos filas en la tabla intermedia = un jugador en dos equipos. **La relación no vive en
`equipos` ni en `jugadores`: vive en la tercera tabla.**

---

## Paso 1: ¿Por qué hace falta una tabla intermedia?

Piensa cómo lo harías con columnas normales:

- Poner `equipo_id` en `jugadores` → un jugador solo podría tener **un** equipo. Eso es
  uno a muchos, no lo que queremos.
- Poner `jugador_id` en `equipos` → un equipo solo tendría **un** jugador.
- Guardar una lista de ids en una columna (`"1,2"`) → funciona hasta que quieres
  preguntar "¿en qué equipos juega Juan?" o borrar un equipo. Ahí todo se vuelve manual.

La solución de las bases de datos relacionales es una **tabla intermedia**: una fila por
cada vínculo.

```sql
-- "Los equipos de Juan"
SELECT equipo_id FROM equipo_jugador_link WHERE jugador_id = 1;

-- "La plantilla del Atlético Nacional"
SELECT jugador_id FROM equipo_jugador_link WHERE equipo_id = 1;
```

Dos consultas simples y una tabla pequeñita. Eso es todo el truco.

> 🧠 **Regla de oro:** si cada lado puede tener **muchos** del otro, necesitas una tabla
> intermedia.

---

## Paso 2: El modelo

Abre `database.py`. Primero se define la tabla intermedia, porque las demás la van a
necesitar:

```python
class EquipoJugadorLink(SQLModel, table=True):
    __tablename__ = "equipo_jugador_link"

    jugador_id: int | None = Field(default=None, foreign_key="jugadores.id", primary_key=True)
    equipo_id: int | None = Field(default=None, foreign_key="equipos.id", primary_key=True)
```

Fíjate en tres cosas:

1. Tiene **dos claves foráneas**: una a `jugadores` y otra a `equipos`.
2. Las dos son **clave primaria** (`primary_key=True`): así no se puede repetir el mismo
   vínculo dos veces.
3. No tiene datos propios: solo los dos ids.

Después, el equipo:

```python
class Equipo(EquipoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # N:M — la plantilla del equipo.
    jugadores: list["Jugador"] = Relationship(
        back_populates="equipos", link_model=EquipoJugadorLink
    )
```

Y el jugador:

```python
class Jugador(JugadorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # N:M — los equipos en los que juega.
    equipos: list[Equipo] = Relationship(
        back_populates="jugadores", link_model=EquipoJugadorLink
    )
```

### Las tres piezas de un N:M

| Pieza | Dónde | Qué hace |
|---|---|---|
| `EquipoJugadorLink` | Su propia clase `table=True` | Guarda las filas del vínculo |
| `link_model=EquipoJugadorLink` | En **los dos** `Relationship` | Dice qué tabla usar como puente |
| `back_populates` | En los dos | Conecta `equipo.jugadores` con `jugador.equipos` |

Si falta `link_model` en un lado, la relación queda vacía y **no avisa**. Si los
`back_populates` no coinciden exactamente, tampoco.

### ¿Por qué `list["Jugador"]` lleva comillas?

Mira la relación del equipo:

```python
jugadores: list["Jugador"] = Relationship(...)
```

Cuando Python lee esa línea, la clase `Jugador` **todavía no existe** (se define más
abajo). Si escribieras `list[Jugador]` sin comillas, Python buscaría la clase en ese
momento y fallaría.

Con comillas es solo un texto: SQLModel lo lee después, cuando ya están todas las clases,
y lo resuelve. El editor también entiende el texto como un tipo, así que sigues teniendo
autocompletado. Es la forma oficial de Python para este caso
([capítulo del tutorial](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/type-annotation-strings/)).

### ¿Y las columnas?

En `equipos` y `jugadores` **no** hay ninguna columna nueva. Mira el esquema: solo las
tres tablas. La relación no es una columna, es una **tabla**.

---

## Paso 3: Los modelos de la API

En el mismo `database.py`, después de las tablas, hay modelos que **no son tablas**:

| Modelo | Para qué |
|---|---|
| `EquipoPublico` | Equipo sin relaciones (listas) |
| `JugadorPublico` | Jugador sin relaciones (listas) |
| `EquipoConJugadores` | Equipo **con** su plantilla |
| `JugadorConEquipos` | Jugador **con** sus equipos |

### Por qué existen dos versiones

Si un equipo incluyera a sus jugadores, y cada jugador incluyera sus equipos, y cada
equipo otra vez sus jugadores… el JSON sería infinito. Se corta usando la versión
**sin** relaciones dentro de la versión con relaciones:

```python
class EquipoConJugadores(EquipoPublico):
    jugadores: list[JugadorPublico] = []


class JugadorConEquipos(JugadorPublico):
    equipos: list[EquipoPublico] = []
```

`JugadorPublico` no trae equipos, así que ahí se acaba el círculo.

---

## Paso 4: La aplicación

`main.py` es corto: crea la app, ejecuta `crear_db_y_tablas()` al arrancar y conecta las
rutas:

```python
app = FastAPI(lifespan=lifespan)

# Conecta a la aplicación las rutas creadas en routes.py
app.include_router(router)
```

- `lifespan`: lo que está antes del `yield` corre al arrancar (crear tablas) y lo de
  después al apagar.
- `include_router(router)`: conecta **todas** las rutas de `routes.py`.

---

## Paso 5: Los endpoints

Todo está en `routes.py`. Los paths se escriben completos porque hay dos grupos:

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/equipos/` | Crea un equipo (`201`) |
| `GET` | `/equipos/` | Lista los equipos |
| `GET` | `/equipos/{equipo_id}` | Un equipo **con su plantilla** |
| `POST` | `/jugadores/` | Crea un jugador (`201`), todavía sin equipo |
| `GET` | `/jugadores/` | Lista los jugadores |
| `GET` | `/jugadores/{jugador_id}` | Un jugador **con sus equipos** |
| `POST` | `/jugadores/{jugador_id}/equipos/{equipo_id}` | **Ficha** al jugador en un equipo |
| `DELETE` | `/jugadores/{jugador_id}/equipos/{equipo_id}` | **Saca** al jugador de un equipo |

Las dos últimas son las interesantes: no crean ni borran equipos ni jugadores, crean o
borran **vínculos**.

### Fichar a un jugador

```python
@router.post("/jugadores/{jugador_id}/equipos/{equipo_id}", response_model=JugadorConEquipos)
def fichar_jugador(jugador_id: int, equipo_id: int, session: session_dependency):
    jugador = session.get(Jugador, jugador_id)
    ...
    if any(e.id == equipo_id for e in jugador.equipos):
        raise HTTPException(status_code=409, detail="El jugador ya está en ese equipo")

    jugador.equipos.append(equipo)   # ← crea la fila en equipo_jugador_link
    session.add(jugador)
    session.commit()
    session.refresh(jugador)
    return jugador
```

Esa línea `append` es todo el secreto: SQLModel traduce "agregar un equipo a la lista"
a `INSERT INTO equipo_jugador_link (...)`.

### Ver un equipo

```python
@router.get("/equipos/{equipo_id}", response_model=EquipoConJugadores)
def ver_equipo(equipo_id: int, session: session_dependency):
    equipo = session.get(Equipo, equipo_id)
    if equipo is None:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")
    return equipo
```

Con eso devuelve el equipo con su plantilla completa, sin escribir el `JOIN` a mano.

---

### ¿De dónde salen los textos de `/docs`?

Los textos no son magia: vienen del código.

| En el código | Dónde se ve en `/docs` |
|---|---|
| `summary="Crear un equipo"` | El título de la ruta |
| El **docstring** de la función | La descripción que aparece al desplegar la ruta |
| `tags=["Equipos"]` | El grupo donde se organiza la ruta |
| `FastAPI(title=..., description=...)` en `main.py` | El encabezado de la página |
| `Field(description="...")` en un modelo | La ayuda de un campo del JSON |

Ejemplo real de una ruta:

```python
@router.post(
    "/equipos/",
    response_model=EquipoPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un equipo",          # ← título en /docs
    tags=["Equipos"],                   # ← grupo en /docs
)
def crear_equipo(datos: EquipoBase, session: session_dependency):
    """Registra un equipo con su nombre y su ciudad."""   # ← descripción
```

> ⚠️ Un `# comentario` **nunca** aparece en `/docs`. Y una cadena suelta como
> `"""Ruta para crear un equipo"""` **fuera** de la función tampoco: es una expresión que
> Python ejecuta y olvida. El docstring tiene que ir **dentro** de la función, en su
> primera línea.

---

## Probarlo paso a paso

Abre `/docs` y prueba **en este orden** (`Try it out` → `Execute`).

**1. Crear dos equipos** — `POST /equipos/`

```json
{"nombre": "Atlético Nacional", "ciudad": "Medellín"}
```

```json
{"nombre": "Los Cracks FC", "ciudad": "Medellín"}
```

**2. Crear un jugador** — `POST /jugadores/`

```json
{"nombre": "Juan Pérez", "posicion": "delantero", "dorsal": 9}
```

Responde `201` con `"equipos": []`.

**3. Ficharlo en el primer equipo** — `POST /jugadores/1/equipos/1`

```json
{"nombre": "Juan Pérez", "posicion": "delantero", "dorsal": 9, "id": 1,
 "equipos": [{"nombre": "Atlético Nacional", "ciudad": "Medellín", "id": 1}]}
```

**4. Ficharlo también en el segundo** — `POST /jugadores/1/equipos/2`

Ahora `"equipos"` tiene dos entradas. **Ese es el muchos a muchos funcionando.**

**5. Mirar el equipo** — `GET /equipos/1`

Juan aparece en `"jugadores"`. Y también en `GET /equipos/2`.

**6. Repetir un fichaje** — `POST /jugadores/1/equipos/1` → `409`
("El jugador ya está en ese equipo").

**7. Probar un dorsal inválido** — `POST /jugadores/` con `"dorsal": 150` → `422`
(la regla `ge=1, le=99` del modelo).

**8. Sacarlo de un equipo** — `DELETE /jugadores/1/equipos/1`

Vuelve a `"equipos"` con un solo equipo. Repetir la misma llamada → `404`.

---

## Mirar la tabla intermedia

La mejor forma de **ver** la relación:

```bash
sqlite3 database.db "SELECT * FROM equipo_jugador_link;"
```

Después del paso 4 deberías ver:

```
1|1
1|2
```

Dos filas = el jugador 1 está en los equipos 1 y 2. La tabla no guarda nada más.

También puedes ver las otras tablas:

```bash
sqlite3 database.db "SELECT * FROM equipos;"
sqlite3 database.db "SELECT * FROM jugadores;"
```

Si no tienes `sqlite3`, abre `database.db` con **DB Browser for SQLite**.

---

## ¿Para qué sirve el muchos a muchos?

1. **Es la realidad del dominio.** Un jugador de verdad juega en la liga y en un torneo
   de barrio. El modelo lo permite sin trucos.
2. **No se duplica la información.** El nombre del equipo está una sola vez.
3. **Consultas en las dos direcciones.** "Los equipos de Juan" y "la plantilla del
   Atlético" salen con la misma tabla intermedia.
4. **Crece sin cambiar columnas.** Agregar un tercer equipo a Juan es una fila más; no
   hay que tocar el esquema.

---

## Errores comunes

| Síntoma | Qué revisar |
|---|---|
| `"equipos": []` aunque se fichó | Falta `link_model` en uno de los dos `Relationship` |
| `"jugadores": []` siempre | Los `back_populates` no coinciden entre las dos clases |
| `InvalidRequestError: ... failed to locate a name` | Comillas mal puestas: usa `list["Jugador"]` con comillas, pero `equipo: Equipo \| None` sin ellas cuando la clase ya existe |
| `NoReferencedTableError` | `foreign_key="jugador.id"` en vez de `"jugadores.id"` (¡el plural importa!) |
| `no such table` / `no such column` | El modelo cambió: **borra `database.db`** y reinicia |
| `422` al crear un jugador | Falta `posicion`, o el `dorsal` está fuera de 1–99 |
| El mismo vínculo aparece dos veces | Olvidaste la comprobación con `any(...)` antes del `append` |

---

## Glosario

| Palabra | Significado rápido |
|---|---|
| **Relación N:M** | Muchos a muchos: un jugador en varios equipos y viceversa |
| **Tabla intermedia** | Tabla con dos claves foráneas que guarda los vínculos |
| **Clave foránea** | Columna que apunta al `id` de otra tabla |
| **`Relationship`** | Atributo de Python que trae los objetos relacionados |
| **`link_model`** | La tabla intermedia que usa un `Relationship` N:M |
| **`back_populates`** | Cable que conecta las dos puntas de la relación |
| **`422`** | Error: los datos enviados no son válidos |
| **`409`** | Error: choca con una regla (el vínculo ya existe) |

---

## Siguiente paso: el taller

Un taller para hacer **en parejas**:

**[Taller — Un jugador, un equipo](talleres/taller_un_jugador_un_equipo.md)**: parten de
este proyecto y **le quitan** el muchos a muchos, para dejar la restricción de un solo
equipo por jugador (uno a muchos).

### Una regla para el taller

El taller se resuelve con lo que aprendiste en esta guía y en el tutorial. Si quieres
usar algo que **no aparece** en ninguno de los dos (otra librería, autenticación, pruebas
automáticas, una metodología de trabajo…), puedes hacerlo, pero debes entregar aparte un
documento `JUSTIFICACION.md` que explique **qué** usaste, **qué necesidad** resolvía y
**qué riesgo** trae.

Los grupos que lo hagan serán los **invitados a exponer su proyecto en detalle** ante
sus compañeros. El taller explica qué debe llevar ese documento.

La documentación oficial (en inglés, con ejemplos de código muy claros) está en
👉 https://sqlmodel.tiangolo.com/tutorial/
