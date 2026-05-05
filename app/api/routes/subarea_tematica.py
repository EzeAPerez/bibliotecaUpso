from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from mysql.connector import IntegrityError, errorcode
from models.subarea_tematica import CreateSubAreaTematica, SubAreaTematica, UpdateSubAreaTematica
from repositories.subarea_tematica import SubAreaRepository
from services.subarea_tematica_service import SubAreaService

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/subarea_tematica",
    tags=["subarea_tematicas"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear subárea temática",
    description="Crear una subárea temática con el contenido pasado por parametro. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def crear_subarea_tematica(
    subarea_create: CreateSubAreaTematica,
    user = Depends(allow_super_admin)
):

    try:
        return SubAreaRepository.crear(subarea_create)

    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un subarea tematica con el nombre: {subarea_create.nombre} y {subarea_create.id_area_tematica}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

@router.patch(
    "/{id}",
    response_model=SubAreaTematica,
    summary="Modificar subárea temática",
    description="Modificar el contenido de una subárea temática con id pasado por parametro",
    tags=[router.tags[0]]
)
def modificar_subarea_tematica(
    id: int,
    subarea_update: UpdateSubAreaTematica
):
    try:
        data = subarea_update.model_dump(exclude_unset=True)
        result = SubAreaRepository.modificar(id, data)

        if not result:
            raise HTTPException(404, "Subarea tematica no encontrada.")
        else:
            return result
        
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un subarea tematica con el nombre: {subarea_update.nombre} y {subarea_update.id_area_tematica}"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar subárea temática",
    description="Eliminar una subárea temática específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_subarea_tematica(
    id: int,
    user = Depends(allow_super_admin)
):
    try:
        
        elimando = SubAreaRepository.eliminar(id)
        if not elimando:
            raise HTTPException(status_code=404, detail="Subárea temática no encontrada.")
        
        return None

    except IntegrityError as e:
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la subárea porque tiene relaciones asociadas"
            )

        raise HTTPException(
            status_code=500,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "",
    response_model=List[SubAreaTematica],
    summary="Obtener subáreas temáticas",
    description="Obtiene todas las subáreas temáticas. Accesible para todos los administradores.",
    tags=[router.tags[0]] 
)
def get_subarea_tematicas(user = Depends(allow_any_admin)):
    return SubAreaRepository.obtener()

    
@router.get(
    "/{id}",
    response_model=SubAreaTematica,
    summary="Obtener subarea tematica por id",
    description="Obtiene el nombre del subarea tematica a partir de su id. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_subarea_tematica_id(
    id: int,
    user = Depends(allow_any_admin)
):
    subarea = SubAreaService.obtener_por_id(id)
    if subarea:
        return subarea
    else:
        raise HTTPException(status_code=404, detail="Subárea temática no encontrada.")