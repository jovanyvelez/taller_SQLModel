from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from database import Heroe, HeroeBase, crear_db_y_tablas, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al iniciar la aplicación, crear la base de datos y las tablas
    crear_db_y_tablas()
    yield
    # Al finalizar la aplicación, se puede realizar limpieza si es necesario (opcional)


app = FastAPI(lifespan=lifespan)

session_dependency = Annotated[Session, Depends(get_session)]

# Rutas de la API


# Endpoint para crear un héroe
@app.post("/heroes/", response_model=Heroe)
def create_hero(heroe: HeroeBase, session: session_dependency):
    new_heroe = Heroe.model_validate(heroe)
    session.add(new_heroe)
    session.commit()
    session.refresh(new_heroe)
    return new_heroe


# Endpoint para obtener todos los héroes
@app.get("/heroes/", response_model=list[Heroe])
def ver_heroes(session: session_dependency):
    consulta = select(Heroe)
    return session.exec(consulta).all()


# Endpoint para borrar un héroe por su ID
@app.delete("/heroes/{hero_id}", response_model=Heroe)
def delete_hero(hero_id: int, session: session_dependency):
    heroe = session.get(Heroe, hero_id)
    if heroe is None:
        return {"error": "Heroe no encontrado"}
    data = Heroe.model_validate(heroe)
    session.delete(heroe)
    session.commit()
    return data


# Endpoint para actualizar un héroe por su ID
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
