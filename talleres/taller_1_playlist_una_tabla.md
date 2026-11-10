# 🎵 Taller 1 — "Mi Playlist": CRUD con una sola tabla

| | |
|---|---|
| **Modalidad** | En parejas |
| **Duración** | 2 sesiones (unas 2 horas en total) |
| **Dificultad** | ⭐⭐☆☆☆ Principiante |
| **Base** | El proyecto **API de Héroes** que acabamos de ver |
| **Tema** | Crear una API para administrar una playlist de canciones |

---

## 1. ¿Qué van a construir?

Una API para guardar las canciones favoritas de la playlist del curso. Cada canción
tiene un título, un artista, un género, una duración y si es favorita o no.

Al final, en `http://127.0.0.1:8000/docs` van a poder **crear, listar, buscar, actualizar
y borrar** canciones. Sin pantallas, sin formularios: todo desde `/docs`.

Es **casi igual** al proyecto de héroes. La diferencia es que ustedes van a:

- inventar su propio modelo (la tabla `canciones`),
- agregar un endpoint que el proyecto de héroes **no tiene** (`GET` de una sola canción),
- y manejar bien el error **404** cuando algo no existe.

> 🎯 **La meta no es copiar y pegar.** Al terminar deben poder explicar, línea por
> línea, qué hace cada parte de su código.

---

## 2. Antes de empezar: qué consultar

La documentación oficial está en inglés, pero los ejemplos de código se entienden
solos. Pueden usar la traducción automática del navegador (clic derecho → "Traducir
página").

**Obligatorio leer** (miren el código, no hace falta leer todo el texto):

| Capítulo | Para qué sirve |
|---|---|
| [Create a Table with SQLModel](https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/) | Cómo se define una tabla |
| [Create Rows - INSERT](https://sqlmodel.tiangolo.com/tutorial/insert/) | Cómo se guarda un registro |
| [Read Data - SELECT](https://sqlmodel.tiangolo.com/tutorial/select/) | Cómo se leen los registros |
| [Read One Row](https://sqlmodel.tiangolo.com/tutorial/one/) | Cómo se busca uno solo |
| [Update Data - UPDATE](https://sqlmodel.tiangolo.com/tutorial/update/) | Cómo se actualiza |
| [Delete Data - DELETE](https://sqlmodel.tiangolo.com/tutorial/delete/) | Cómo se borra |
| [Indexes](https://sqlmodel.tiangolo.com/tutorial/indexes/) | Por qué `index=True` |

**Recomendado** (si quieren ir más allá):

- [Filter Data - WHERE](https://sqlmodel.tiangolo.com/tutorial/where/)
- [Simple Hero API with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/simple-hero-api/)
- [Session with FastAPI Dependency](https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/)

Y por supuesto, la guía del proyecto: `README.md` de la carpeta `javiera_sqlmodel`.

---

## 3. Requisitos: el modelo

Su tabla se debe llamar **`canciones`** y tener exactamente estos campos:

| Campo | Tipo | Regla |
|---|---|---|
| `id` | entero | Clave primaria, la genera la base de datos |
| `titulo` | texto | Obligatorio. `index=True` |
| `artista` | texto | Obligatorio. Es el **nombre** del artista, por ahora solo texto |
| `genero` | texto o vacío | Opcional. `index=True` |
| `duracion_segundos` | entero | Obligatorio y **mayor que 0** |
| `favorita` | verdadero/falso | Por defecto `False` |

Pistas:

- Los campos van en una clase `CancionBase(SQLModel)` y la tabla en
  `Cancion(CancionBase, table=True)`, igual que `HeroeBase` y `Heroe`.
- Para que la base de datos rechace duraciones de 0 o negativas:
  `duracion_segundos: int = Field(gt=0)`. (`gt` = *greater than*, mayor que).
- Para el valor por defecto: `favorita: bool = Field(default=False)`.
- Para la relación con la base de datos, la clave foránea **no** va aquí todavía:
  en este taller `artista` es solo un texto. La relación real es el **Taller 2**.

---

## 4. Requisitos: los endpoints

Cinco endpoints, ni uno más:

| Método | Ruta | Qué debe hacer |
|---|---|---|
| `POST` | `/canciones/` | Crear una canción y devolverla con su `id` |
| `GET` | `/canciones/` | Devolver la lista de todas las canciones |
| `GET` | `/canciones/{cancion_id}` | Devolver una canción. Si no existe → **404** |
| `PUT` | `/canciones/{cancion_id}` | Actualizar una canción. Si no existe → **404** |
| `DELETE` | `/canciones/{cancion_id}` | Borrar una canción. Si no existe → **404** |

### Reglas de negocio (mírenlas como un contrato)

1. Si falta `titulo`, `artista` o `duracion_segundos` → la API debe responder **422**
   (FastAPI lo hace solo si el modelo está bien definido).
2. Si `duracion_segundos` es 0 o negativo → **422** (gracias a `gt=0`).
3. `favorita` es `False` si no se envía.
4. Si el `id` no existe, **no** devuelvan un diccionario con un mensaje: lancen una
   excepción para que la API responda **404**. Así:

   ```python
   from fastapi import HTTPException, status

   cancion = session.get(Cancion, cancion_id)
   if cancion is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail=f"Canción {cancion_id} no encontrada",
       )
   ```

5. Al crear, lo ideal es responder **201 Created**:
   `@app.post("/canciones/", status_code=status.HTTP_201_CREATED)`.

---

## 5. El contrato de la API (ejemplos)

Esto es lo que debe pasar en `/docs`. Compárenlo con su resultado.

**Crear** — `POST /canciones/`

```json
{
  "titulo": "Waka Waka",
  "artista": "Shakira",
  "genero": "Pop",
  "duracion_segundos": 210,
  "favorita": true
}
```

Respuesta esperada (`201`):

```json
{
  "titulo": "Waka Waka",
  "artista": "Shakira",
  "genero": "Pop",
  "duracion_segundos": 210,
  "favorita": true,
  "id": 1
}
```

**Listar** — `GET /canciones/` → `200`

```json
[
  {
    "titulo": "Waka Waka",
    "artista": "Shakira",
    "genero": "Pop",
    "duracion_segundos": 210,
    "favorita": true,
    "id": 1
  }
]
```

**Buscar una que no existe** — `GET /canciones/99` → `404`

```json
{"detail": "Canción 99 no encontrada"}
```

**Actualizar** — `PUT /canciones/1`

```json
{
  "titulo": "Waka Waka (Esto es África)",
  "artista": "Shakira",
  "genero": "Pop",
  "duracion_segundos": 211,
  "favorita": false
}
```

**Borrar** — `DELETE /canciones/1` → `200` con la canción que se borró.

---

## 6. Plan de trabajo (paso a paso)

### Paso 0 — Crear su proyecto

Creen una carpeta nueva para el taller y copien ahí los archivos del proyecto base
(`database.py`, `main.py` y `requirements.txt`). En el ejemplo la carpeta base se llama
`javiera_sqlmodel`: usen el nombre real de su carpeta.

```bash
# macOS / Linux
mkdir playlist && cd playlist
cp ../javiera_sqlmodel/database.py .
cp ../javiera_sqlmodel/main.py .
cp ../javiera_sqlmodel/requirements.txt .
```

```powershell
# Windows (PowerShell)
mkdir playlist
cd playlist
copy ..\javiera_sqlmodel\database.py .
copy ..\javiera_sqlmodel\main.py .
copy ..\javiera_sqlmodel\requirements.txt .
```

Si solo les dieron el código, creen ustedes el `requirements.txt` con estas dos líneas:

```text
fastapi[standard]>=0.162.2
sqlmodel>=0.0.48
```

Ahora preparen el entorno (esto se hace **una sola vez**). Elijan su sistema:

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ahora abran `database.py` y `main.py`. Van a reemplazar a los héroes por canciones.

### Paso 1 — Cambiar el modelo (`database.py`)

- Borren `HeroeBase` y `Heroe`.
- Escriban `CancionBase` y `Cancion` con los campos de la sección 3.
- **No cambien** el `engine`, ni `crear_db_y_tablas`, ni `get_session`: ya funcionan.

### Paso 2 — Cambiar los endpoints (`main.py`)

- Cambien los imports: ahora traen `Cancion` y `CancionBase` desde `database`.
- Adapten `POST`, `GET` (lista), `PUT` y `DELETE`.
- Agreguen el `GET /canciones/{cancion_id}` nuevo, con su `HTTPException`.
- Cambien las rutas `/heroes/` por `/canciones/`.

> 💡 **Truco:** cambien **una cosa a la vez** y prueben. Y ojo con el nombre exacto del
> parámetro: es `response_model`, en inglés y con guion bajo.

### Paso 3 — Arrancar y probar

```bash
fastapi dev main.py
```

> Recuerden activar el entorno si abren una terminal nueva: `source .venv/bin/activate`
> (macOS/Linux) o `.venv\Scripts\Activate.ps1` (Windows).

Abran http://127.0.0.1:8000/docs y prueben **en este orden**:

1. `POST` con una canción válida → debe devolver `201` y un `id`.
2. `POST` sin `titulo` → debe devolver `422`.
3. `POST` con `duracion_segundos: 0` → debe devolver `422`.
4. `GET` lista → debe aparecer la canción.
5. `GET /canciones/99` → debe devolver `404`.
6. `PUT` → cambiar la duración y verificar.
7. `DELETE` → borrarla y comprobar que ya no aparece en la lista.

### Paso 4 — Revisar la base de datos

```bash
sqlite3 database.db "SELECT * FROM canciones;"
```

(Y en la consola del servidor van a ver el SQL que se ejecuta, porque `echo=True`.)

### Paso 5 — Entregar

Ver la sección 7.

---

## 7. Entregables

1. **El código funcionando**: `database.py` y `main.py`.
2. **Un `README.md` propio y corto** con:
   - cómo ejecutar el proyecto (los dos comandos),
   - la tabla de endpoints,
   - un ejemplo de `JSON` para crear una canción.
3. **Evidencias** (capturas de pantalla o un PDF):
   - `/docs` mostrando los 5 endpoints de canciones,
   - un `POST` exitoso con su `201` y su `id`,
   - un `404` real (`GET /canciones/99`),
   - un `422` (por ejemplo, una canción sin `titulo`).
4. **Las respuestas** a las preguntas de la sección 11 (máximo 10 líneas).
5. **Solo si usaron algo que no vimos:** el documento `JUSTIFICACION.md` de la
   sección 10.

Todo va en una sola carpeta entregada por la plataforma del curso, con el nombre de
los dos integrantes.

---

## 8. Cómo se evalúa

| Criterio | Puntos |
|---|---|
| El modelo tiene los 6 campos, con `table=True`, clave primaria e índices | 20 |
| `POST` crea y devuelve la canción con `id` (ideal: `201`) | 15 |
| `GET` lista todas y `GET` por id devuelve una, con `404` correcto | 20 |
| `PUT` actualiza todos los campos | 15 |
| `DELETE` borra y desaparece de la lista | 10 |
| Validaciones y códigos HTTP correctos (`422`, `404`, `201`) | 10 |
| `README` y evidencias claras | 10 |
| **Total** | **100** |

**Cómo se pierden puntos fácilmente:**

- Devolver `{"error": "..."}` en vez de lanzar `HTTPException` (queda un `200` con
  datos vacíos: eso es un error, no una respuesta).
- Olvidar `status_code=201`.
- Poner `index=True` en `id` (la clave primaria ya es un índice).
- Que el `PUT` cambie solo un campo y deje los demás como estaban.

---

## 9. Retos extra (+10 cada uno, máximo 20)

Si terminan antes, elijan **dos**:

1. **Filtrar por favoritas:** `GET /canciones/?favorita=true` devuelve solo las favoritas.
   Pista: `select(Cancion).where(Cancion.favorita == favorita)`.
2. **Filtrar por género:** `GET /canciones/?genero=Rock`.
3. **Ordenar:** que la lista salga de la canción más corta a la más larga.
   Pista: `order_by(Cancion.duracion_segundos)`.
4. **Contar:** `GET /canciones/resumen` que devuelva cuántas canciones hay y la duración
   total en minutos.
5. **Actualización parcial:** agregar `PATCH /canciones/{id}` que solo cambie los campos
   enviados. Pista: el capítulo
   [Update Data with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/update/)
   y `cancion.sqlmodel_update(datos.model_dump(exclude_unset=True))`.
6. **Búsqueda:** `GET /canciones/?q=waka` que busque el texto en el título.

> ⚠️ Si le agregan un campo nuevo al modelo, **borren `database.db`** y reinicien:
> `create_all` no modifica tablas que ya existen.

---

## 10. ¿Y si quieren usar algo que no vimos?

Este taller se puede resolver **entero** con lo que está en la guía del proyecto y en
el tutorial de SQLModel. Pero si quieren ir más allá, **pueden hacerlo**. Solo hay una
condición: **explicarlo aparte, en un documento**.

### ¿Qué cuenta como "algo que no vimos"?

Cualquier concepto, herramienta, librería o metodología que **no aparezca** ni en la
guía del proyecto (`README.md` de `javiera_sqlmodel`) ni en el tutorial
(https://sqlmodel.tiangolo.com/tutorial/).

| Sí es "algo que no vimos" | No hace falta justificar |
|---|---|
| Agregar una librería (`pydantic-settings`, `alembic`, `python-jose`…) | `Field`, `index=True`, `primary_key` |
| Autenticación, CORS, variables de entorno, Docker | `select`, `where`, `commit`, `refresh` |
| Separar el código en varios archivos (`routers/`) | `HTTPException`, `status_code=404` |
| Pruebas automáticas con `pytest` | `Depends`, `Annotated`, `lifespan` |
| Una metodología de trabajo (TDD, Kanban, Git flow…) | `SQLModel`, `Session`, `create_engine` |

> 🔎 **Primero revisen el tutorial.** Muchas cosas ya están ahí (por ejemplo, `PATCH`
> está en *Update Data with FastAPI*). Si aparece en el material, no hay que
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
2. el modelo de la base de datos (sus tablas y sus campos),
3. qué agregaron fuera del material y **por qué** lo necesitaban.

---

## 11. Preguntas para pensar

Respondan en parejas, con sus propias palabras:

1. ¿Qué pasaría si quitan `table=True` de la clase `Cancion`? ¿La tabla existiría?
2. ¿Por qué el `id` se escribe `int | None` y no simplemente `int`?
3. ¿Cuál es la diferencia entre un error **404** y un **422**? Den un ejemplo de cada uno
   en su API.
4. ¿Para qué sirve `index=True`? ¿Por qué no lo pusieron en `duracion_segundos`?
5. Si mañana agregan el campo `album`, ¿qué deben hacer para que la tabla tenga esa
   columna?
6. ¿Por qué después de `commit()` hace falta `refresh()` al crear una canción?
7. ¿Qué diferencia hay entre `PUT` y `PATCH`?

---

## 12. Consejos y errores comunes

| Síntoma | Qué revisar |
|---|---|
| `422` al crear con todos los datos | El nombre de un campo está mal escrito o el tipo no coincide |
| `no such table: canciones` | No corrieron `fastapi dev main.py` desde la carpeta del proyecto, o el `lifespan` no está creando las tablas |
| Cambiaron el modelo y la tabla sigue igual | Borren `database.db` y reinicien |
| `500` con "response validation" | Están devolviendo un diccionario cualquiera donde se espera una `Cancion` |
| El `GET` por id no existe en `/docs` | La ruta tiene un error de escritura, o hay dos funciones con el mismo nombre de ruta |
| `Address already in use` | Otro servidor usa el puerto 8000: `--port 8001` |

**Consejos de oro**

- Cambien una cosa, prueben, y solo entonces sigan con la siguiente.
- `echo=True` es su mejor amigo: ahí ven el SQL real.
- Si algo se daña sin explicación, borren `database.db` y vuelvan a empezar: son datos
  de prueba, no se pierde nada.
- Lo importante es que puedan **explicar** cada línea, aunque hayan pedido ayuda.

---

## ✅ Autoevaluación (antes de entregar)

- [ ] Mi tabla se llama `canciones` y tiene los 6 campos pedidos
- [ ] `duracion_segundos` rechaza el 0 y los negativos
- [ ] `favorita` vale `False` si no la envío
- [ ] Crear una canción devuelve `201` con su `id`
- [ ] `GET /canciones/{id}` con un id que no existe devuelve `404` de verdad
- [ ] `PUT` y `DELETE` también responden `404` cuando no encuentran la canción
- [ ] Probé todo desde `/docs` y guardé las capturas
- [ ] Mi `README.md` explica cómo ejecutar el proyecto
- [ ] Si usé algo fuera del material, mi `JUSTIFICACION.md` está completo
- [ ] Puedo explicar qué hace cada línea de mi `main.py`

¡Y ahora el reto grande: **[Taller 2 — Artistas y Canciones](taller_2_artistas_y_canciones.md)**,
donde la playlist se convierte en **dos tablas relacionadas**! 🎸
