from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.restricciones import Restricciones, RestriccionesUpdate
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.restricciones_repo import RestriccionesRepository

from core.security import (
    allow_super_admin
)

router = APIRouter(
    prefix="/restricciones",
    tags=["restricciones"]
)

   
@router.patch(
    "/{id}", 
    summary="Modificar una restriccion",
    description="Modificar el contenido de una restriccion con id pasada por paremetro. Solo accesible para SuperAdmin.",
    response_model=Restricciones,
    status_code=status.HTTP_200_OK, 
    tags=[router.tags[0]]
    )
def modificar_restriccion(
    id: int,
    tipo_ingreso: RestriccionesUpdate,
    user = Depends(allow_super_admin)
):    
    try:
        result = RestriccionesRepository.modificar(id, tipo_ingreso)

        if not result:
            raise HTTPException(404, "Restriccion no encontrado")
        else:
            return result
        
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una restriccion con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "",      
    response_model=List[Restricciones],
    summary="Listar las restricciones",
    description="Obtiene todas las restricciones. Accesible para todos los SuperAdmin.",
    tags=[router.tags[0]]
    )
def get_restriccion(
    user = Depends(allow_super_admin)
):
    try:
        return RestriccionesRepository.obtener()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
