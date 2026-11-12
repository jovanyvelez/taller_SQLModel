# ⚽ Taller — Un jugador, un equipo: de muchos a muchos a uno a muchos

| | |
|---|---|
| **Modalidad** | En parejas |
| **Duración** | 2 sesiones |
| **Dificultad** | ⭐⭐⭐☆☆ Intermedio |
| **Base** | El proyecto **API de Equipos y Jugadores** (que usa muchos a muchos) |
| **Tema** | Pasar de una relación N:M a una relación 1:N |

---

## 1. La historia

El proyecto que acaban de ver permite que un jugador esté en **varios equipos**: el de la
liga profesional y el de un torneo recreacional. Esa era la idea.

Pero la liga cambió el reglamento:

> **Regla nueva:** un jugador solo puede estar inscrito en **un** equipo. Sí, un equipo
> sigue teniendo muchos jugadores.

O sea: hay que **quitar** el muchos a muchos y dejar un **uno a muchos**. La pregunta del
taller es: ¿qué se borra, qué se agrega y **por qué**?

> 🎯 Al final deben poder explicar, con sus palabras, por qué la tabla intermedia ya no
> hace falta… y cuándo volvería a hacer falta.

---

## 2. Antes de empezar: qué consultar

| Capítulo | Para qué |
|---|---|
| [Create Connected Tables](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-tables/) | Cómo se escribe una clave foránea |
| [Create and Connect Rows](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-rows/) | Cómo se guardan datos relacionados |
| [Read Connected Data](https://sqlmodel.tiangolo.com/tutorial/connect/read-connected-data/) | Cómo se leen |
| [Define Relationship Attributes](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/) | `Relationship` y `back_populates` |
| [Read One Model with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/read-one/) | `GET` de un solo registro y el `404` |
| [Update Data with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/update/) | El `PATCH` que cambia de equipo |
| [Filter Data - WHERE](https://sqlmodel.tiangolo.com/tutorial/where/) | Para los retos de filtrar |
| [Models with Relationships in FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/) | Cómo devolver un objeto con sus hijos |
| [Many to Many](https://sqlmodel.tiangolo.com/tutorial/many-to-many/) | Para **comparar**: lo que usan hoy |

Y la guía del proyecto (`README.md`), sobre todo los pasos 1 y 2.

---

## 3. El cambio, en una tabla

| | Versión actual (N:M) | Versión que van a construir (1:N) |
|---|---|---|
| ¿Dónde vive el vínculo? | En la tabla `equipo_jugador_link` | En una columna `equipo_id` dentro de `jugadores` |
| ¿Cuántos equipos por jugador? | Varios | **Uno** |
| ¿Cuántos jugadores por equipo? | Varios | Varios |
| En el código | `jugador.equipos` (una **lista**) | `jugador.equipo` (un **objeto**) |
| Número de tablas | 3 | **2** |
| Endpoints de vínculo | `POST` y `DELETE` para fichar/sacar | Ya no hacen falta |

**La tabla intermedia desaparece** porque ya no hay combinaciones que guardar: cada
jugador apunta a su equipo con una columna.

📚 Fuentes: [Create Connected Tables](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-tables/)
muestra la relación 1:N con clave foránea; [Many to Many](https://sqlmodel.tiangolo.com/tutorial/many-to-many/)
explica la que acaban de usar (y con qué se compara).

---

## 4. Qué cambia en el modelo (`database.py`)

### 4.1 Se borra

- La clase `EquipoJugadorLink` y su tabla.
- `Jugador.equipos` (la lista) y `Equipo.jugadores` con `link_model=`.
- Los modelos `JugadorConEquipos` y las rutas de fichar/sacar.

### 4.2 Se agrega en `Jugador`

```python
equipo_id: int | None = Field(default=None, foreign_key="equipos.id", index=True)
equipo: Equipo | None = Relationship(back_populates="jugadores")
```

### 4.3 Se cambia en `Equipo`

```python
jugadores: list["Jugador"] = Relationship(back_populates="equipo")
```

> 💡 Fíjense en el detalle: **`back_populates` apunta al nombre exacto del atributo del
> otro lado**. `Equipo.jugadores` ↔ `Jugador.equipo`.

📚 Fuentes: [Create Connected Tables](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-tables/)
para la clave foránea, [Define Relationship Attributes](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/)
para el `Relationship`, y [Relationship back_populates](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/back-populates/)
para el nombre que debe coincidir en los dos lados.

### 4.4 Modelos de la API

| Modelo | Qué debe tener |
|---|---|
| `JugadorCreate` | `nombre`, `posicion`, `dorsal` y **`equipo_id`** |
| `JugadorUpdate` | Todos opcionales, incluido `equipo_id` |
| `JugadorPublico` | Los datos + `id` + `equipo_id` |
| `EquipoConJugadores` | El equipo + `jugadores: list[JugadorPublico]` |
| `JugadorConEquipo` | El jugador + `equipo: EquipoPublico \| None` |

Las comillas en `list["Jugador"]` son normales: la clase todavía no existe en esa línea.
El porqué está en [Type annotation strings](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/type-annotation-strings/).

📚 Fuentes para los modelos de respuesta: [Models with Relationships in FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/)
(cómo devolver un objeto con sus hijos) y [Multiple Models with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/)
(por qué conviene tener varios modelos).

---

## 5. Los endpoints que deben quedar

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/equipos/` | Crear equipo (`201`) — pueden reutilizar el que ya existe |
| `GET` | `/equipos/` | Listar equipos — reutilizar |
| `POST` | `/jugadores/` | Crear jugador **con su equipo**; si el equipo no existe → `404` |
| `GET` | `/jugadores/` | Listar jugadores (con `id` y `equipo_id`) |
| `GET` | `/jugadores/{jugador_id}` | Un jugador **con los datos de su equipo**; si no existe → `404` |
| `GET` | `/equipos/{equipo_id}` | Un equipo **con su plantilla** |
| `PATCH` | `/jugadores/{jugador_id}` | Cambiar de equipo (o nombre, posición, dorsal) |

**Ya no existen** `/jugadores/{id}/equipos/{equipo_id}` (ni el `POST` ni el `DELETE`):
sin tabla intermedia no hay vínculo que crear o borrar.

📚 Fuentes por endpoint:

- Crear un jugador con su equipo: [Create and Connect Rows](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-rows/).
- Leer uno y responder `404`: [Read One Model with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/read-one/).
- Cambiar de equipo con `PATCH`: [Update Data with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/update/)
  y [Update Data Connections](https://sqlmodel.tiangolo.com/tutorial/connect/update-data-connections/).
- `DELETE` (si lo necesitan): [Delete Data with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/delete/).

### Reglas de negocio

1. Un jugador **no puede** tener dos equipos: lo garantiza la columna `equipo_id`.
2. Si se envía un `equipo_id` que no existe → **404**.
3. Cambiar de equipo **reemplaza** el anterior (no se acumulan).
4. Un equipo puede tener **cero** jugadores: `"jugadores": []`.
5. Al crear, responder **`201`**.

Pista para el `PATCH`:

```python
cambios = datos.model_dump(exclude_unset=True)
if cambios.get("equipo_id") is not None and session.get(Equipo, cambios["equipo_id"]) is None:
    raise HTTPException(status_code=404, detail="El equipo no existe")
jugador.sqlmodel_update(cambios)
```

---

## 6. Contrato de la API

**Crear un jugador con su equipo** — `POST /jugadores/`

```json
{"nombre": "Juan Pérez", "posicion": "delantero", "dorsal": 9, "equipo_id": 1}
```

→ `201`

```json
{
  "nombre": "Juan Pérez", "posicion": "delantero", "dorsal": 9,
  "id": 1, "equipo_id": 1,
  "equipo": {"nombre": "Atlético Nacional", "ciudad": "Medellín", "id": 1}
}
```

**Ver el equipo** — `GET /equipos/1` → `200`

```json
{
  "nombre": "Atlético Nacional", "ciudad": "Medellín", "id": 1,
  "jugadores": [
    {"nombre": "Juan Pérez", "posicion": "delantero", "dorsal": 9, "id": 1, "equipo_id": 1}
  ]
}
```

**Cambiar de equipo** — `PATCH /jugadores/1` con `{"equipo_id": 2}`

El cuerpo devuelto ya trae el equipo nuevo y **no** una lista: `"equipo": {...}`.

**Errores esperados**

```json
// POST /jugadores/ con equipo_id 99 → 404
{"detail": "El equipo 99 no existe"}

// GET /jugadores/99 → 404
{"detail": "Jugador 99 no encontrado"}
```

---

## 7. Plan de trabajo

### Paso 0 — Preparar el proyecto

Copien la carpeta base a una nueva llamada `liga` y **borren la base de datos**:

```bash
# macOS / Linux
cp -r javiera_sqlmodel liga && cd liga
rm database.db
```

```powershell
# Windows (PowerShell)
xcopy ..\javiera_sqlmodel liga /E /I
cd liga
del database.db
```

```bash
python -m venv .venv
```

Actívenlo (`source .venv/bin/activate` o `.venv\Scripts\Activate.ps1`) e instalen:

```bash
pip install -r requirements.txt
```

> ⚠️ **Borrar `database.db` es obligatorio.** `create_all` no modifica tablas: la tabla
> `equipo_jugador_link` se quedaría ahí y `jugadores` no tendría la columna `equipo_id`.

### Paso 1 — El modelo

- Borren `EquipoJugadorLink`.
- Quiten `link_model=` y la relación de lista `equipos` del jugador.
- Agreguen `equipo_id` y `equipo` en `Jugador`.
- Cambien `Equipo.jugadores` para que apunte a `back_populates="equipo"`.
- Ajusten los modelos de la API.

### Paso 2 — Las rutas

- Borren las rutas de fichar y sacar (`/jugadores/{id}/equipos/{equipo_id}`).
- Ajusten `POST /jugadores/` para recibir `equipo_id` y validarlo.
- Ajusten `PATCH /jugadores/{id}` para poder cambiar de equipo.
- Cambien el `response_model` del jugador a `JugadorConEquipo`.

> 💡 Si dejan una ruta que use `jugador.equipos`, la API responde `500`: ese atributo ya
> no existe. Bórrenla completa.

### Paso 3 — Probar en orden

1. `POST /equipos/` → `201`.
2. `POST /jugadores/` con `equipo_id` válido → `201` y trae el equipo.
3. `POST /jugadores/` con `equipo_id: 99` → `404`.
4. `GET /equipos/1` → la plantilla con el jugador.
5. `GET /jugadores/1` → el jugador con su equipo.
6. `PATCH /jugadores/1` con `{"equipo_id": 2}` → cambia de equipo.
7. `GET /equipos/1` → ya no está; `GET /equipos/2` → sí está.

### Paso 4 — Revisar la base de datos

```bash
sqlite3 database.db ".tables"
```

Deben aparecer **solo** `equipos` y `jugadores`. Si sigue ahí
`equipo_jugador_link`, no borraron la base de datos.

```bash
sqlite3 database.db "SELECT * FROM jugadores;"
```

Van a ver la columna `equipo_id`. **Ese número es toda la relación.**

### Paso 5 — Entregar

Ver la sección 8.

---

## 8. Entregables

1. **El código funcionando**: `database.py`, `routes.py` y `main.py`.
2. **Un `README.md` propio** con: cómo ejecutar, tabla de endpoints y un dibujo del
   esquema de **dos** tablas.
3. **Evidencias** (capturas o PDF):
   - `/docs` con los endpoints de jugadores,
   - `POST /jugadores/` con `equipo_id` (`201`),
   - `GET /equipos/1` con la plantilla,
   - `GET /jugadores/1` con su equipo,
   - un `404` (equipo inexistente),
   - un `PATCH` cambiando de equipo.
4. **Respuestas** a las preguntas de la sección 11 (máximo 10 líneas).

---

## 9. Cómo se evalúa

| Criterio | Puntos |
|---|---|
| Modelo 1:N correcto (`equipo_id` con `foreign_key="equipos.id"` + `Relationship`) | 25 |
| La tabla intermedia y las rutas de fichar/sacar fueron eliminadas | 10 |
| Crear jugador con equipo y validar que exista (`404`) | 15 |
| `GET /equipos/{id}` devuelve la plantilla | 15 |
| `GET /jugadores/{id}` devuelve el equipo | 15 |
| `PATCH` cambia de equipo sin acumular | 10 |
| Modelos de respuesta sin ciclos | 5 |
| Evidencias y `README` | 5 |
| **Total** | **100** |

**Errores que cuestan puntos:**

- Dejar `link_model` y `equipo_id` al mismo tiempo (dos relaciones contradictorias).
- Que el jugador pueda quedar en dos equipos por no validar el `PATCH`.
- Olvidar borrar `database.db` y arrastrar la tabla vieja.
- Devolver `JugadorConEquipos` (una lista) cuando ahora es `JugadorConEquipo`.

---

## 10. Retos extra (+10 cada uno, máximo 20)

Elijan **dos**:

1. **Historial de traspasos.** Quieren saber en qué equipos **estuvo** cada jugador.
   Pista: ahí vuelve a hacer falta una tabla intermedia… pero ahora con un campo extra
   (`fecha_ingreso`). Capítulo:
   [Link Model with Extra Fields](https://sqlmodel.tiangolo.com/tutorial/many-to-many/link-with-extra-fields/).
2. **Dorsal único por equipo:** si dos jugadores del mismo equipo piden el 10 → `409`.
   Pista: `select(Jugador).where(Jugador.equipo_id == ..., Jugador.dorsal == ...)`.
   Capítulo: [Filter Data - WHERE](https://sqlmodel.tiangolo.com/tutorial/where/).
3. **Filtrar por equipo:** `GET /jugadores/?equipo_id=1`.
4. **Contar la plantilla:** `GET /equipos/1` agregando `total_jugadores`.
5. **Equipo sin jugadores:** `DELETE /jugadores/{id}` cuidando que el equipo quede vacío
   pero existiendo. Capítulo:
   [Delete Data with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/delete/).

> ⚠️ Si agregan campos al modelo, **borren `database.db`** otra vez.

---

## 11. Preguntas para pensar

1. ¿Por qué en la versión N:M el vínculo vivía en una tabla y ahora vive en una columna?
2. ¿Qué se puede hacer con N:M que **ya no** se puede hacer con 1:N? Den un ejemplo real
   (no vale "el de la guía").
3. ¿Qué pasó con los vínculos que ya estaban guardados en `equipo_jugador_link` cuando
   borraron la tabla? ¿Se podía conservar esa información?
4. ¿Para qué sirve un `PATCH` que cambie `equipo_id`? ¿Qué diferencia tiene con crear un
   jugador nuevo?
5. Si la liga mañana vuelve a permitir la doble inscripción, ¿qué habría que agregar?
6. ¿Cuál de las dos versiones es "más simple"? ¿Y cuál permite más cosas? ¿Siempre es
   mejor la más simple?

---

## 12. ¿Y si usan algo que no vimos?

Si usan librerías, herramientas o metodologías que **no aparecen** en la guía ni en el
tutorial, deben entregar un documento `JUSTIFICACION.md` (máximo una página) con:

1. **Qué** usaron y **dónde** (archivo o endpoint).
2. **Qué necesidad** resolvía en este proyecto.
3. **Qué alternativa** consideraron y por qué la descartaron.
4. **Qué riesgo** trae (complejidad, seguridad, mantenimiento).
5. La **fuente** consultada (enlace).

Los grupos que lo entreguen serán los **invitados a exponer su proyecto en detalle** ante
sus compañeros (5–8 minutos, con demo en vivo desde `/docs`).

---

## 13. Consejos y errores comunes

| Síntoma | Qué revisar |
|---|---|
| `table jugadores has no column named equipo_id` | No borraron `database.db` |
| `"equipo": null` siempre | Falta la clave foránea o el `back_populates` no coincide |
| `500` en `/jugadores/...` | Quedó una ruta que usa `jugador.equipos` (ese atributo ya no existe) |
| `422` al crear jugador | Falta `equipo_id` en el modelo `Create` o el dorsal está fuera de 1–99 |
| El jugador aparece en dos equipos | Se quedó el código del `PATCH` usando listas en vez de reemplazar `equipo_id` |
| `no such table: equipo_jugador_link` | Borraron la tabla pero no la base: **borren `database.db`** |

---

## ✅ Autoevaluación (antes de entregar)

- [ ] `Jugador` tiene `equipo_id` con `foreign_key="equipos.id"` y su `Relationship`
- [ ] `Equipo.jugadores` y `Jugador.equipo` tienen `back_populates` que coinciden
- [ ] Ya no existe `EquipoJugadorLink` ni ninguna ruta de fichar/sacar
- [ ] Crear un jugador con un equipo que no existe devuelve `404`
- [ ] `GET /equipos/1` trae la plantilla
- [ ] `GET /jugadores/1` trae el equipo (objeto, no lista)
- [ ] `PATCH` cambia de equipo y el anterior se reemplaza
- [ ] `sqlite3 database.db ".tables"` muestra solo `equipos` y `jugadores`
- [ ] Puedo explicar **por qué** la tabla intermedia ya no hace falta

¡Listo! Ahora saben lo más importante de las relaciones: **no se eligen por moda, se
eligen por la regla del negocio**. ⚽
