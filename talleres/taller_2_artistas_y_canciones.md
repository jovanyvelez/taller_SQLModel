# 🎸 Taller 2 — "Artistas y Canciones": dos tablas relacionadas

| | |
|---|---|
| **Modalidad** | En parejas |
| **Duración** | 2 o 3 sesiones |
| **Dificultad** | ⭐⭐⭐☆☆ Intermedio |
| **Base** | Su **Taller 1** (o el proyecto API de Héroes) |
| **Tema** | Relación **uno a muchos** entre artistas y canciones |

---

## 1. ¿Qué van a construir?

En el Taller 1 el artista era solo un texto dentro de la canción:

```
canciones
┌────┬──────────────┬──────────┬─────────────┐
│ id │ titulo       │ artista  │ duracion…   │
├────┼──────────────┼──────────┼─────────────┤
│ 1  │ Waka Waka    │ Shakira  │ 210         │
│ 2  │ Hips Don't…  │ Shakira  │ 218         │
└────┴──────────────┴──────────┴─────────────┘
```

Eso funciona, pero tiene problemas: si Shakira cambia de nombre artístico, hay que
corregir **todas** sus canciones una por una. Y no se puede guardar un artista que
todavía no tenga canciones.

En este taller el artista se convierte en **su propia tabla**, y las canciones lo
referencian:

```
artistas                                 canciones
┌────┬──────────┬───────────┐            ┌────┬────────────┬────────────┐
│ id │ nombre   │ pais      │            │ id │ titulo     │ artista_id │
├────┼──────────┼───────────┤            ├────┼────────────┼────────────┤
│ 1  │ Shakira  │ Colombia  │◄───────────┤ 1  │ Waka Waka  │ 1          │
└────┴──────────┴───────────┘            └────┴────────────┴────────────┘
                                          └── cada canción apunta a un artista
```

Esto se llama **relación uno a muchos** (1:N): **un** artista tiene **muchas** canciones,
y **cada** canción pertenece a **un** artista.

---

## 2. Antes de empezar: qué consultar

La documentación oficial está en inglés, pero el código se entiende. Usen la
traducción del navegador si la necesitan.

**Obligatorio leer** (enfóquense en los bloques de código):

| Capítulo | Para qué sirve |
|---|---|
| [Connect Tables - Intro](https://sqlmodel.tiangolo.com/tutorial/connect/) | Qué es una relación entre tablas |
| [Create Connected Tables](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-tables/) | Cómo se escribe la clave foránea |
| [Create and Connect Rows](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-rows/) | Cómo se guardan datos relacionados |
| [Read Connected Data](https://sqlmodel.tiangolo.com/tutorial/connect/read-connected-data/) | Cómo se leen los datos relacionados |
| [Define Relationship Attributes](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/) | Qué hace `Relationship()` |
| [Models with Relationships in FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/) | Cómo devolver un objeto con sus hijos |

**Recomendado:**

- [FastAPI Path Operations for Teams - Other Models](https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/)
- [Remove Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/remove-relationships/)

> 📌 Los ejemplos del tutorial usan **Heroes** y **Teams**. Ustedes van a hacer lo
> mismo con **Canciones** y **Artistas**. La estructura es idéntica: `Team` → `Hero`
> es como `Artista` → `Cancion`.

---

## 3. La idea clave: dos formas de decir lo mismo

En SQLModel hay **dos cosas distintas** que se parecen mucho. No las confundan:

| | Qué es | Dónde va |
|---|---|---|
| `artista_id` | Un **número** guardado en la tabla `canciones` (la **clave foránea**) | Es una columna normal |
| `artista` | El **objeto** `Artista` completo, que SQLModel trae solo | **No** es una columna |

- `artista_id: int = Field(foreign_key="artistas.id")` → "esta canción apunta al
  artista con este número".
- `artista: Artista | None = Relationship(back_populates="canciones")` → "tráeme el
  objeto artista completo, y avísale al artista que esta canción es suya".

Y al revés, en `Artista`:

- `canciones: list["Cancion"] = Relationship(back_populates="artista")` → "tráeme la
  lista de todas sus canciones".

`back_populates` es como un **cable** que conecta las dos puntas: el nombre que pongan
de un lado debe ser exactamente el nombre del atributo del otro lado.

---

## 4. El modelo completo (`database.py`)

Este es el archivo que deben dejar así (o muy parecido). Las líneas nuevas están
comentadas.

```python
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class ArtistaBase(SQLModel):
    nombre: str = Field(index=True, unique=True)   # unique: no se repite
    pais: str | None = None


class Artista(ArtistaBase, table=True):
    __tablename__ = "artistas"

    id: int | None = Field(default=None, primary_key=True)
    # Un artista tiene MUCHAS canciones
    canciones: list["Cancion"] = Relationship(back_populates="artista")


class CancionBase(SQLModel):
    titulo: str = Field(index=True)
    genero: str | None = Field(default=None, index=True)
    duracion_segundos: int = Field(gt=0)
    favorita: bool = Field(default=False)
    # La clave foránea: apunta a artistas.id
    artista_id: int = Field(foreign_key="artistas.id", index=True)


class Cancion(CancionBase, table=True):
    __tablename__ = "canciones"

    id: int | None = Field(default=None, primary_key=True)
    # Muchas canciones pertenecen a UN artista
    artista: Artista | None = Relationship(back_populates="canciones")


# --- Modelos para responder por la API (no son tablas) ---

class CancionPublica(CancionBase):
    id: int


class ArtistaPublico(ArtistaBase):
    id: int


class ArtistaConCanciones(ArtistaPublico):
    canciones: list[CancionPublica] = []


class CancionConArtista(CancionPublica):
    artista: ArtistaPublico | None = None


# Necesario para que Python resuelva las referencias "hacia adelante"
Artista.model_rebuild()
Cancion.model_rebuild()
```

### ⚠️ Dos detalles que dañan a todo el mundo

**1. Las comillas dependen del orden.** `Cancion` todavía no existe cuando se escribe
`Artista`, por eso va entre comillas: `list["Cancion"]`. Pero `Artista` **ya existe**
cuando se escribe `Cancion`, así que ahí va **sin comillas**: `Artista | None`.

Si en `Cancion` escriben `artista: "Artista | None"` (con comillas), van a ver un error
parecido a:

```
InvalidRequestError: ... expression 'Artista | None' failed to locate a name ...
```

Solución: quitar las comillas de esa línea.

**2. `model_rebuild()`.** Son las dos últimas líneas. Le dicen a SQLModel "ya están
todas las clases, ahora sí resuelve las referencias". Si las olvidan, es posible que
Python se queje de que `Cancion` no está definida.

Las líneas del `engine`, `crear_db_y_tablas` y `get_session` se quedan **igual** que en
su proyecto: solo cambia la parte de los modelos.

---

## 5. Los endpoints

| Método | Ruta | Qué debe hacer |
|---|---|---|
| `POST` | `/artistas/` | Crear un artista (`201`) |
| `GET` | `/artistas/` | Listar todos los artistas |
| `GET` | `/artistas/{artista_id}` | Devolver el artista **con sus canciones**. Si no existe → `404` |
| `DELETE` | `/artistas/{artista_id}` | Borrar un artista **solo si no tiene canciones** (`409` si tiene). Si no existe → `404` |
| `POST` | `/canciones/` | Crear una canción. Si el `artista_id` no existe → `404` |
| `GET` | `/canciones/` | Listar canciones. Con `?artista_id=1`, solo las de ese artista |
| `GET` | `/canciones/{cancion_id}` | Devolver la canción **con los datos de su artista**. Si no existe → `404` |

### Reglas de negocio

1. **El nombre del artista es único.** Si se repite → `409 Conflict`. (Ojo: con
   `unique=True` la base de datos también lo impide, pero entonces el error llega como
   `500`. Mejor revísenlo **antes** de guardar y respondan `409` con un mensaje claro.)
2. **No se puede crear una canción con un artista que no existe** → `404`.
3. **No se puede borrar un artista que tenga canciones** → `409`.
   (Si no quieren bloquear, la alternativa es borrar en cascada; eso es un reto.)
4. **Un artista sin canciones** se devuelve con `"canciones": []`.
5. Al crear, respondan **`201`**.

Pista para el `404`:

```python
from fastapi import HTTPException, status

if session.get(Artista, datos.artista_id) is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"El artista {datos.artista_id} no existe",
    )
```

Pista para la relación a la hora de crear: **guarden siempre `artista_id`**, no el objeto
`artista`. El objeto se llena solo cuando consultan.

---

## 6. El contrato de la API

**Crear artista** — `POST /artistas/`

```json
{"nombre": "Shakira", "pais": "Colombia"}
```

→ `201`

```json
{"nombre": "Shakira", "pais": "Colombia", "id": 1}
```

**Crear canción** — `POST /canciones/`

```json
{
  "titulo": "Waka Waka",
  "genero": "Pop",
  "duracion_segundos": 210,
  "favorita": false,
  "artista_id": 1
}
```

→ `201`

```json
{
  "titulo": "Waka Waka",
  "genero": "Pop",
  "duracion_segundos": 210,
  "favorita": false,
  "artista_id": 1,
  "id": 1
}
```

**Ver artista con sus canciones** — `GET /artistas/1` → `200`

```json
{
  "nombre": "Shakira",
  "pais": "Colombia",
  "id": 1,
  "canciones": [
    {
      "titulo": "Waka Waka",
      "genero": "Pop",
      "duracion_segundos": 210,
      "favorita": false,
      "artista_id": 1,
      "id": 1
    }
  ]
}
```

**Ver canción con su artista** — `GET /canciones/1` → `200`

```json
{
  "titulo": "Waka Waka",
  "genero": "Pop",
  "duracion_segundos": 210,
  "favorita": false,
  "artista_id": 1,
  "id": 1,
  "artista": {"nombre": "Shakira", "pais": "Colombia", "id": 1}
}
```

**Errores esperados**

```json
// POST /canciones/ con artista_id 99  → 404
{"detail": "El artista 99 no existe"}

// DELETE /artistas/1 teniendo canciones → 409
{"detail": "No se puede eliminar un artista que tenga canciones"}

// POST /artistas/ con "Shakira" otra vez → 409
{"detail": "Ya existe un artista con ese nombre"}
```

> 👀 Fíjense que en el `GET` anidado el artista **no** trae sus `canciones` dentro de
> cada canción (sería un círculo infinito). Por eso hay **dos** modelos distintos:
> `CancionPublica` y `CancionConArtista`, y `ArtistaPublico` y `ArtistaConCanciones`.
> A eso se le llama *response models*: cada endpoint devuelve la forma que necesita.

---

## 7. Plan de trabajo (paso a paso)

### Paso 0 — Preparar el proyecto

Partan de su Taller 1 (o de la carpeta del proyecto base) y **borren la base de datos**:

```bash
rm database.db          # macOS / Linux
del database.db         # Windows
```

Arranquen el servidor (**con el entorno activado**):

```bash
fastapi dev main.py
```

> ⚠️ **¿Por qué borrarla?** `create_all` solo crea tablas que no existen: **no modifica**
> las que ya están. Su tabla `canciones` del Taller 1 tiene una columna `artista` de
> texto, y ahora necesita `artista_id`. Si no la borran, verán un error como
> `table canciones has no column named artista_id`. Borrar el archivo y arrancar de
> nuevo es lo más rápido en un proyecto de aprendizaje.

### Paso 1 — `database.py`

1. Agreguen las clases `ArtistaBase` y `Artista`.
2. En `CancionBase`, quiten `artista: str` y pongan `artista_id: int = Field(foreign_key="artistas.id", index=True)`.
3. En `Cancion`, agreguen el `Relationship`.
4. Agreguen `CancionPublica`, `ArtistaPublico`, `ArtistaConCanciones`, `CancionConArtista`.
5. Terminen con los dos `model_rebuild()`.

### Paso 2 — Endpoints de artistas (`main.py`)

- `POST /artistas/`: antes de crear, busquen si el nombre ya existe → `409`.
- `GET /artistas/`: `select(Artista)`.
- `GET /artistas/{artista_id}`: `session.get(Artista, artista_id)` y devuelvan el objeto.
  El `response_model=ArtistaConCanciones` hace que aparezcan las canciones.
- `DELETE /artistas/{artista_id}`: si `artista.canciones` tiene algo → `409`.

> 💡 `artista.canciones` funciona porque definieron el `Relationship`. Si está vacío,
> se comporta como una lista vacía: `if artista.canciones:` es falso.

### Paso 3 — Endpoints de canciones

- `POST /canciones/`: validen el artista (`404`), luego `Cancion.model_validate(datos)`.
- `GET /canciones/`: agreguen el parámetro opcional `artista_id: int | None = None` y,
  si viene, filtren con `.where(Cancion.artista_id == artista_id)`.
- `GET /canciones/{cancion_id}`: devuelvan con `response_model=CancionConArtista`.

### Paso 4 — Probar en orden

1. `POST /artistas/` con Shakira → `201`, id 1.
2. `POST /artistas/` con Shakira otra vez → `409`.
3. `GET /artistas/1` → `"canciones": []`.
4. `POST /canciones/` con `artista_id: 99` → `404`.
5. `POST /canciones/` con `artista_id: 1` → `201`.
6. `GET /artistas/1` → ahora trae la canción adentro.
7. `GET /canciones/1` → trae el artista adentro.
8. `GET /canciones/?artista_id=1` → solo las de Shakira.
9. `DELETE /artistas/1` → `409`.
10. Borren la canción y ahora sí `DELETE /artistas/1` → `200`.

### Paso 5 — Entregar

Ver la sección 8.

---

## 8. Entregables

1. **El código funcionando**: `database.py` y `main.py`.
2. **`README.md` propio** con: cómo ejecutar, tabla de endpoints y **un dibujo o
   explicación de la relación** artista → canciones.
3. **Evidencias** (capturas o PDF):
   - `/docs` con los 7 endpoints,
   - `GET /artistas/1` mostrando el artista **con** sus canciones,
   - `GET /canciones/1` mostrando la canción **con** su artista,
   - un `404` (`artista_id` inexistente),
   - un `409` (nombre repetido o borrar artista con canciones).
4. **Respuestas** a las preguntas de la sección 12 (máximo 10 líneas).
5. **Solo si usaron algo que no vimos:** el documento `JUSTIFICACION.md` de la
   sección 11.

---

## 9. Cómo se evalúa

| Criterio | Puntos |
|---|---|
| Modelo con clave foránea correcta (`foreign_key="artistas.id"`) | 15 |
| `Relationship` con `back_populates` en **ambos** lados | 10 |
| `POST` y `GET` de artistas, con `201` y listado | 15 |
| `GET /artistas/{id}` devuelve las canciones anidadas | 15 |
| `POST /canciones/` valida que el artista exista (`404`) | 15 |
| Regla `409`: nombre repetido y borrar artista con canciones | 15 |
| Filtro `?artista_id=` y `GET /canciones/{id}` con el artista | 10 |
| `README` y evidencias | 5 |
| **Total** | **100** |

**Errores que cuestan puntos:**

- Guardar `artista` como texto otra vez (no hay relación real).
- Olvidar `back_populates` en uno de los dos lados.
- Devolver un `500` cuando el nombre del artista se repite (debe ser `409`).
- Que el `GET` anidado funcione solo a veces (revisar los `response_model`).

---

## 10. Retos extra (+10 cada uno, máximo 20)

Elijan **dos**:

1. **Muchos a muchos.** Hasta ahora una canción tiene **un** artista. ¿Y si una canción
   pudiera tener **varios** artistas (una colaboración)? Se necesita una **tabla
   intermedia**. Capítulo:
   [Many to Many](https://sqlmodel.tiangolo.com/tutorial/many-to-many/).
2. **Borrado en cascada.** Que al borrar un artista se borren también sus canciones,
   con `Relationship(back_populates="artista", cascade_delete=True)`. ¿Es buena idea?
   Discútanlo.
3. **Resumen por artista.** `GET /artistas/{id}/resumen` con cuántas canciones tiene y
   la duración total en minutos.
4. **Mover una canción de artista.** `PATCH /canciones/{id}` con `artista_id` nuevo,
   validando que el artista exista.
5. **Paginación.** `GET /artistas/?offset=0&limit=10`.
   Capítulo: [LIMIT and OFFSET](https://sqlmodel.tiangolo.com/tutorial/limit-and-offset/).
6. **Top 3.** `GET /artistas/top` con los 3 artistas que más canciones tienen.

> ⚠️ Otra vez: si cambian el modelo, **borren `database.db`** y reinicien.

---

## 11. ¿Y si quieren usar algo que no vimos?

Igual que en el Taller 1: se puede resolver **entero** con lo que está en la guía del
proyecto y en el tutorial. Pero si quieren ir más allá, **pueden hacerlo**. Solo hay una
condición: **explicarlo aparte, en un documento**.

### ¿Qué cuenta como "algo que no vimos"?

Cualquier concepto, herramienta, librería o metodología que **no aparezca** ni en la
guía del proyecto (`README.md` de `javiera_sqlmodel`) ni en el tutorial
(https://sqlmodel.tiangolo.com/tutorial/).

| Sí es "algo que no vimos" | No hace falta justificar |
|---|---|
| Agregar una librería (`pydantic-settings`, `alembic`, `python-jose`…) | `Relationship`, `back_populates`, `foreign_key` |
| Autenticación, CORS, variables de entorno, Docker | `select`, `where`, `commit`, `refresh` |
| Pruebas automáticas con `pytest` | `HTTPException`, `status_code=409` |
| Programación asíncrona (`async def`, `await`) | El muchos a muchos del tutorial (tabla intermedia) |
| Una metodología de trabajo (TDD, Kanban, Git flow…) | El borrado en cascada del tutorial (`cascade_delete`) |

> 🔎 **Primero revisen el tutorial.** Varias cosas de los retos ya están explicadas ahí
> (muchos a muchos, cascada, paginación). Si aparece en el material, no hay que
> justificarla: úsenla tranquilos.

**También aplica a los retos:** si para resolver uno necesitan algo que no vimos (por
ejemplo, agrupar y contar dentro de SQL), eso también va en el documento. Si lo resuelven
con lo que ya saben (un `for` en Python), no hace falta justificar nada.

### El documento: `JUSTIFICACION.md`

Máximo **una página**, en la carpeta de la entrega. Este es el molde:

```markdown
# Justificación técnica — [nombres del grupo]

## 1. Qué construimos
Tres líneas: qué hace nuestra API y qué agregamos fuera del material base.

## 2. Elementos fuera del material
| # | Elemento | Dónde se usa | ¿Para qué? |
|---|---|---|---|
| 1 | | | |
| 2 | | | |

## 3. Detalle de cada elemento
### Elemento 1: [nombre]
- ¿Qué es? Con nuestras propias palabras, en 2 o 3 líneas.
- ¿Qué necesidad resuelve en ESTE proyecto? (el problema concreto)
- ¿Qué pasaría si no lo usáramos? La alternativa que probamos o imaginamos.
- ¿Qué riesgo o costo trae? (más complejidad, seguridad, tiempo, mantenimiento)
- Fuente consultada: [enlace]

## 4. Conclusión
¿Valió la pena? ¿Lo volverían a usar? ¿Qué aprendieron?
```

**Regla:** cada elemento que usen debe aparecer en la tabla **y** tener su detalle.
Un documento con solo la tabla no sirve.

### ¿Qué pasa si no lo entregan?

- Ese elemento **no se tiene en cuenta** como valor agregado (no suma en los retos).
- Puede **restar** en claridad: si nadie del grupo sabe explicar una parte del código,
  eso es un riesgo, no una ventaja.

### 🎤 Y hay premio: ustedes exponen

Los grupos que usen elementos fuera del material base **y entreguen su
`JUSTIFICACION.md`** serán los **invitados a exponer su proyecto en detalle** ante sus
compañeros.

La exposición dura entre 5 y 8 minutos e incluye:

1. una demostración en vivo desde `/docs`,
2. el modelo de la base de datos **con la relación** artista → canciones,
3. qué agregaron fuera del material y **por qué** lo necesitaban.

---

## 12. Preguntas para pensar

1. ¿Qué diferencia hay entre guardar `artista` como texto y guardar `artista_id`?
   ¿Qué ventaja tiene lo segundo?
2. ¿Qué es una **clave foránea**? ¿Qué debería pasar si guardan una canción con
   `artista_id = 999`?
3. ¿Por qué al borrar un artista con canciones respondemos `409` y no lo dejamos pasar?
   ¿Qué pasaría si no hubiera ninguna regla?
4. ¿Qué hace `Relationship(back_populates=...)`? ¿Qué creen que pasa si se lo quitan?
5. ¿Por qué `list["Cancion"]` lleva comillas y `Artista | None` no?
6. ¿Por qué hay cuatro modelos "de respuesta" al final de `database.py`? ¿No bastaba
   con `Cancion` y `Artista`?
7. Si quieren "todas las canciones de Shakira", ¿lo harían con `artista.canciones` o con
   un `select(...).where(...)`? ¿Da lo mismo?

---

## 13. Consejos y errores comunes

| Síntoma | Qué revisar |
|---|---|
| `table canciones has no column named artista_id` | No borraron `database.db` |
| `InvalidRequestError: ... failed to locate a name` | Comillas mal puestas en `Relationship`: quiten las de `Artista \| None` |
| `"canciones": []` siempre vacío | Falta `back_populates` en un lado, o están usando otro objeto `session` |
| `500` al repetir el nombre del artista | Con `unique=True` la base de datos lanza error: validen antes y respondan `409` |
| `500` en `GET /artistas/1` | El `response_model` pide `ArtistaConCanciones`, pero el endpoint devuelve otra cosa |
| `NoReferencedTableError` | El `foreign_key` dice `"artista.id"` en vez de `"artistas.id"` (¡el plural importa!) |
| El filtro `?artista_id=1` no filtra | Se olvidaron de aplicar el `.where(...)` o el parámetro no está en la función |

**Consejos de oro**

- Escriban primero el modelo y **prueben que arranque**; después los endpoints.
- En `/docs` prueben siempre en orden: primero los artistas, luego las canciones.
- Si algo raro pasa con datos viejos, borren `database.db`: son datos de prueba.
- El tutorial usa Heroes y Teams: cada vez que diga `Team`, piensen `Artista`; cada vez
  que diga `Hero`, piensen `Cancion`. Es el mismo ejercicio.

---

## ✅ Autoevaluación (antes de entregar)

- [ ] Mi tabla `canciones` tiene `artista_id` con `foreign_key="artistas.id"`
- [ ] Definí `Relationship` en los dos modelos, con `back_populates` que coinciden
- [ ] `GET /artistas/1` devuelve el artista con sus canciones adentro
- [ ] `GET /canciones/1` devuelve la canción con su artista adentro
- [ ] Crear una canción con un artista inexistente devuelve `404`
- [ ] Repetir el nombre de un artista devuelve `409` (no `500`)
- [ ] Borrar un artista con canciones devuelve `409`
- [ ] El filtro `?artista_id=` funciona
- [ ] Borré `database.db` antes de la entrega y el proyecto arranca limpio
- [ ] Si usé algo fuera del material, mi `JUSTIFICACION.md` está completo
- [ ] Puedo explicar con un dibujo la relación uno a muchos

¡Listo! Ya saben lo que la mayoría de la gente aprende meses después: **cómo se conectan
dos tablas**. 🎉
