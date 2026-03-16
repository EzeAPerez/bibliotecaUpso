from fastapi import FastAPI
from api.routes import obras, area_tematica, subarea_tematica, obras_subareas, sedes, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(obras.router)
app.include_router(area_tematica.router)
app.include_router(subarea_tematica.router)
app.include_router(obras_subareas.router)
app.include_router(sedes.router)