from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import crear_db_y_tablas
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al iniciar la aplicación, crear la base de datos y las tablas
    crear_db_y_tablas()
    yield
    # Al finalizar la aplicación, se puede realizar limpieza si es necesario (opcional)


app = FastAPI(
    title="API de Equipos y Jugadores",
    description=(
        "Ejemplo del curso: **muchos a muchos** con SQLModel. "
        "Un equipo tiene varios jugadores y un jugador puede estar en varios equipos."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Conecta a la aplicación las rutas creadas en routes.py
app.include_router(router)
