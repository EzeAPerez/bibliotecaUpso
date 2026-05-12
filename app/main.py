from fastapi import FastAPI
from api.routes import obras, area_tematica, subarea_tematica, obras_subareas, sedes, auth, auth_prueba, ejemplar

app = FastAPI()

app.include_router(auth_prueba.router)
app.include_router(obras.router)
app.include_router(area_tematica.router)
app.include_router(subarea_tematica.router)
app.include_router(obras_subareas.router)
app.include_router(sedes.router)
app.include_router(ejemplar.router)