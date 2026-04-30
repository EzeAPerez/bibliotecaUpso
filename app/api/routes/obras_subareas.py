from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode
from models.obras_subareas import ObraYSubarea, ObrasySubareasDetallado, ModificarObraYSubarea
from repositories.obras_subarea_repo import ObraSubareaRepository
from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/obras_subareas",
    tags=["obras_y_subareas"]
)
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Asignar subárea temática a obra",
    description="Asignar una subárea temática a una obra específica por sus IDs. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def asignar_subarea_obra(
    obra_subarea: ObraYSubarea,
    user = Depends(allow_super_admin)
):
    try:
        ObraSubareaRepository.asignar(obra_subarea)

    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La obra ya tiene asignada esa subárea temática"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    summary="Modificar asignación de subárea temática a obra",
    description="Modificar la asignación de una subárea temática a una obra específica por sus IDs. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def modificar_subarea_obra(
    obra_subarea: ModificarObraYSubarea,
    user = Depends(allow_super_admin)
):
    try:
        result = ObraSubareaRepository.modificar(obra_subarea)
        
        if result == 0:
            raise HTTPException(
                status_code=404,
                detail="La ralacion obra subarea tematica no existe"
            )
        
        return {"message": "Relación actualizada correctamente"}
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de integridad: {e.msg}")

@router.delete(
    "/{id_obra}/{id_subarea}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar subárea temática de obra",
    description="Eliminar la asignación de una subárea temática a una obra específica por sus IDs. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_subarea_obra(
    id_obra: int,
    id_subarea: int,
    user = Depends(allow_super_admin)
):
    try:
        result = ObraSubareaRepository.eliminar(id_obra, id_subarea)

        if result == 0:
            raise HTTPException(
                status_code=404,
                detail="La realcion obra subarea tematica no existe"
            )

    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de integridad: {e.msg}")

@router.get(
    "",
    response_model=List[ObrasySubareasDetallado],
    summary="Obtener las relaciones entre las obras y las subáreas temáticas",
    description="Obtener todas las relaciones obras subáreas temáticas asignadas. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_subareas_obra(
    user = Depends(allow_any_admin)
):
    try:

        result = ObraSubareaRepository.obtener()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

