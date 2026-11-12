"""Modelos y conexión a la base de datos.

El ejemplo tiene **una sola** relación: muchos a muchos (N:M) entre equipos y
jugadores.

- Un equipo tiene muchos jugadores en su plantilla.
- Un jugador puede estar en la plantilla de varios equipos: el equipo de la liga
  profesional y, por ejemplo, el de un torneo recreacional.

Como ningún lado puede guardar "el otro" en una columna (un jugador tendría que
guardar varios equipos), se usa una **tabla intermedia**: `EquipoJugadorLink`.
"""

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


# ---------------------------------------------------------------------------
# Tabla intermedia de la relación MUCHOS A MUCHOS
# ---------------------------------------------------------------------------
# No guarda datos propios: cada fila es un "vínculo" jugador ↔ equipo.
class EquipoJugadorLink(SQLModel, table=True):
    __tablename__ = "equipo_jugador_link"

    jugador_id: int | None = Field(
        default=None, foreign_key="jugadores.id", primary_key=True
    )
    equipo_id: int | None = Field(
        default=None, foreign_key="equipos.id", primary_key=True
    )


# ---------------------------------------------------------------------------
# Equipo
# ---------------------------------------------------------------------------
class EquipoBase(SQLModel):
    nombre: str = Field(index=True)
    ciudad: str


class Equipo(EquipoBase, table=True):
    __tablename__ = "equipos"

    id: int | None = Field(default=None, primary_key=True)

    # N:M — la plantilla del equipo. Los vínculos NO viven en esta tabla:
    # viven en EquipoJugadorLink.
    jugadores: list["Jugador"] = Relationship(
        back_populates="equipos", link_model=EquipoJugadorLink
    )


# ---------------------------------------------------------------------------
# Jugador
# ---------------------------------------------------------------------------
class JugadorBase(SQLModel):
    nombre: str = Field(index=True)
    posicion: str
    dorsal: int | None = Field(default=None, ge=1, le=99)


class Jugador(JugadorBase, table=True):
    __tablename__ = "jugadores"

    id: int | None = Field(default=None, primary_key=True)

    # N:M — los equipos en los que juega. No hay columna en `jugadores`:
    # la información está en EquipoJugadorLink.
    equipos: list[Equipo] = Relationship(
        back_populates="jugadores", link_model=EquipoJugadorLink
    )


# ---------------------------------------------------------------------------
# Modelos para la API (NO son tablas)
# ---------------------------------------------------------------------------
class EquipoPublico(EquipoBase):
    id: int


class JugadorPublico(JugadorBase):
    id: int


# Un equipo CON su plantilla (GET /equipos/{id})
class EquipoConJugadores(EquipoPublico):
    jugadores: list[JugadorPublico] = []


# Un jugador CON sus equipos (GET /jugadores/{id})
class JugadorConEquipos(JugadorPublico):
    equipos: list[EquipoPublico] = []


# ---------------------------------------------------------------------------
# Conexión y sesión
# ---------------------------------------------------------------------------
DATA_BASE_URL = "sqlite:///database.db"
connects_args = {"check_same_thread": False}

engine = create_engine(DATA_BASE_URL, connect_args=connects_args, echo=True)


def crear_db_y_tablas():
    """Crea las tres tablas: equipos, jugadores y la tabla intermedia."""
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
