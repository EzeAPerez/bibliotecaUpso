from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.area_tematica import CreateAreaTematica, AreaTematica, UpdateAreaTematica
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.area_tematica_repo import AreaTematicaRepository
from services.area_tematica_service import AreaTematicaService

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/area_tematica",
    tags=["areas_tematicas"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear area tematica",
    description="Crea una nueva area tematica con los datos pasados por Request body. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def crear_area_tematica(
    area_create: CreateAreaTematica,
    user = Depends(allow_super_admin)
):
    try:
        area_nueva = AreaTematica.model_validate(area_create)
        return AreaTematicaRepository.crear(area_nueva)
    
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe un area tematica con el nombre: {area_nueva.nombre}"
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de integridad: {e.msg}")


@router.patch(
    "/{id}",
    response_model=AreaTematica,
    summary="Modificar área temática",
    description="Modificar el contenido de una área temática con id pasado por parametro. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def modificar_area_tematica(
    id: int,
    area_update: UpdateAreaTematica,
    user = Depends(allow_super_admin)
):
    try:
        data = area_update.model_dump(exclude_unset=True)
        result = AreaTematicaRepository.modificar(id, data)

        if not result:
            raise HTTPException(404, "Área temática no encontrada.")
        else:
            return result

    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un area tematica con esos datos.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error de integridad en la base de datos.")

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar área temática",
    description="Eliminar una área temática específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_area_tematica(
    id: int,
    user = Depends(allow_super_admin)
):

    try:
        eliminado = AreaTematicaRepository.eliminar(id)

        if not eliminado:
            raise HTTPException(404, "Área temática no encontrada.")
        
        return None
    
    except IntegrityError as e:
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="No se puede eliminar el área temática porque tiene relaciones asociadas")

        raise HTTPException(status_code=500, detail="Error de integridad en la base de datos.")
    
@router.get(
    "",
    response_model=List[AreaTematica],
    summary="Obtener áreas temáticas",
    description="Obtiene todas las áreas temáticas. Accesible para todos los administradores.",
    tags=[router.tags[0]] 
)
def get_area_tematicas(user = Depends(allow_any_admin)):
    try:
        result = AreaTematicaRepository.obtener()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{id}",
    response_model=AreaTematica,
    summary="Obtener area tematica por id",
    description="Obtiene el nombre del area tematica a partir de su id. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_area_tematica_id(
    id: int,
    user = Depends(allow_any_admin)
):
    try:
        areaTematica = AreaTematicaService.obtener_por_id(id)

        if areaTematica: 
              return areaTematica
        else:  
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area temática no encontrada.")    

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
