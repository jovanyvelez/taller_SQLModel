"""Rutas (endpoints) de la API.

Todo lo que responde a peticiones HTTP vive aquí. El objeto `router` se conecta
a la aplicación en `main.py` con `app.include_router(router)`.

Los textos que se ven en `/docs` salen de tres sitios:

- `summary=`: el título corto de la ruta (si no se pone, FastAPI inventa uno con
  el nombre de la función).
- El **docstring** de la función (el texto entre `\"\"\"` dentro de ella): la
  descripción que aparece al desplegar la ruta.
- `tags=`: el grupo en el que se organiza la ruta.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import (
    Equipo,
    EquipoBase,
    EquipoConJugadores,
    EquipoPublico,
    Jugador,
    JugadorBase,
    JugadorConEquipos,
    JugadorPublico,
    get_session,
)

router = APIRouter()

session_dependency = Annotated[Session, Depends(get_session)]


# ---------------------------------------------------------------------------
# EQUIPOS
# ---------------------------------------------------------------------------
@router.post(
    "/equipos/",
    response_model=EquipoPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un equipo",
    tags=["Equipos"],
)
def crear_equipo(datos: EquipoBase, session: session_dependency):
    """Registra un equipo con su nombre y su ciudad.

    Devuelve el equipo con el `id` que le asignó la base de datos.
    """
    equipo = Equipo.model_validate(datos)
    session.add(equipo)
    session.commit()
    session.refresh(equipo)
    return equipo


@router.get(
    "/equipos/",
    response_model=list[EquipoPublico],
    summary="Listar equipos",
    tags=["Equipos"],
)
def listar_equipos(session: session_dependency):
    """Devuelve todos los equipos, sin sus jugadores."""
    return session.exec(select(Equipo)).all()


@router.get(
    "/equipos/{equipo_id}",
    response_model=EquipoConJugadores,
    summary="Ver un equipo con su plantilla",
    tags=["Equipos"],
)
def ver_equipo(equipo_id: int, session: session_dependency):
    """Devuelve el equipo con su plantilla completa (los vínculos del N:M).

    Si el equipo no existe, responde `404`.
    """
    equipo = session.get(Equipo, equipo_id)
    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipo {equipo_id} no encontrado",
        )
    return equipo


# ---------------------------------------------------------------------------
# JUGADORES
# ---------------------------------------------------------------------------
@router.post(
    "/jugadores/",
    response_model=JugadorConEquipos,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un jugador",
    tags=["Jugadores"],
)
def crear_jugador(datos: JugadorBase, session: session_dependency):
    """Crea un jugador. Todavía no tiene equipo: se ficha con la ruta de abajo.

    El campo `dorsal` es opcional y debe estar entre 1 y 99.
    """
    jugador = Jugador.model_validate(datos)
    session.add(jugador)
    session.commit()
    session.refresh(jugador)
    return jugador


@router.get(
    "/jugadores/",
    response_model=list[JugadorPublico],
    summary="Listar jugadores",
    tags=["Jugadores"],
)
def listar_jugadores(session: session_dependency):
    """Devuelve todos los jugadores, sin sus equipos."""
    return session.exec(select(Jugador)).all()


@router.get(
    "/jugadores/{jugador_id}",
    response_model=JugadorConEquipos,
    summary="Ver un jugador con sus equipos",
    tags=["Jugadores"],
)
def ver_jugador(jugador_id: int, session: session_dependency):
    """Devuelve el jugador con todos los equipos en los que juega.

    Si el jugador no existe, responde `404`.
    """
    jugador = session.get(Jugador, jugador_id)
    if jugador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jugador {jugador_id} no encontrado",
        )
    return jugador


@router.post(
    "/jugadores/{jugador_id}/equipos/{equipo_id}",
    response_model=JugadorConEquipos,
    summary="Fichar a un jugador en un equipo",
    tags=["Jugadores"],
)
def fichar_jugador(jugador_id: int, equipo_id: int, session: session_dependency):
    """Ficha al jugador en un equipo: crea una fila en la tabla intermedia.

    Si el jugador o el equipo no existen, responde `404`. Si el vínculo ya
    existe, responde `409`.
    """
    jugador = session.get(Jugador, jugador_id)
    if jugador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jugador {jugador_id} no encontrado",
        )

    equipo = session.get(Equipo, equipo_id)
    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipo {equipo_id} no encontrado",
        )

    if any(e.id == equipo_id for e in jugador.equipos):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El jugador ya está en ese equipo",
        )

    jugador.equipos.append(equipo)
    session.add(jugador)
    session.commit()
    session.refresh(jugador)
    return jugador


@router.delete(
    "/jugadores/{jugador_id}/equipos/{equipo_id}",
    response_model=JugadorConEquipos,
    summary="Sacar a un jugador de un equipo",
    tags=["Jugadores"],
)
def sacar_jugador(jugador_id: int, equipo_id: int, session: session_dependency):
    """Saca al jugador de un equipo: borra la fila de la tabla intermedia.

    Si el jugador no existe o no está en ese equipo, responde `404`.
    """
    jugador = session.get(Jugador, jugador_id)
    if jugador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jugador {jugador_id} no encontrado",
        )

    equipo = next((e for e in jugador.equipos if e.id == equipo_id), None)
    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El jugador no está en ese equipo",
        )

    jugador.equipos.remove(equipo)
    session.add(jugador)
    session.commit()
    session.refresh(jugador)
    return jugador
