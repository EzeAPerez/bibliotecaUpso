from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status, Query
from models.renovaciones import *
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.renovaciones_repo import RenovacionesRepository
from services.renovaciones_service import RenovacionesService

from core.security import (
    allow_everyone,
    allow_super_admin,
    allow_any_admin
)

router = APIRouter(
    prefix="/renovaciones",
    tags=["renovaciones"]
)

@router.post(
    "/general/",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear una renovacion",
    description="Crear una nueva renovacion en la base de datos. Accesibles para todos los administradores.",
    tags=[router.tags[0]]
)
def crear_reserva_general(
    renovaciones: RenovacionesCreate, 
    current_user = Depends(allow_any_admin)
):
    try: 
        renovaciones_data = renovaciones.model_dump()

        renovacion_nueva = Renovaciones.model_validate(renovaciones_data)

        return RenovacionesRepository.crear(renovacion_nueva)

    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad: {e.msg}"
        )
    
## Crea una reserva del lado del usuario. Solo debe mandar la obra y la sede, el resto se encarga el sistema.

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crear una renovaciones por usuario.",
    description="Crear una nueva renovacion en la base de datos. Accesibles para todos los usuarios.",
    tags=[router.tags[0]]
)
def crear_reserva(
    renovaciones: RenovacionesCreateUser, 
    current_user = Depends(allow_everyone)
):
    try: 
        renovacion_data = renovaciones.model_dump()

        return RenovacionesService.crear(renovacion_data)

    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad: {e.msg}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.patch(
    "/{id}", 
    status_code=status.HTTP_200_OK,
    summary="Modificar renovacion",
    description="Modificar el contenido de una renovacion con id pasado por parametro. Solo accesible para Aministradores.",
    tags=[router.tags[0]]
    )
def modificar_reserva(
    id: int,
    renovacion_update: RenovacionesUpdate,
    user = Depends(allow_any_admin)
):
    try:
        data = renovacion_update.model_dump(exclude_unset=True)

        return RenovacionesRepository.actualizar(
            id,
            data
        )

    except LookupError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except IntegrityError as e:

        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad: {e.msg}"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor:"
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar renovacion",
    description="Eliminar una renovacion específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_reserva(
    id: int,
    user = Depends(allow_super_admin)
):
    try:
        eliminado = RenovacionesRepository.eliminar(id)
        
        if not eliminado:
            raise HTTPException(404, "Reserva no encontrada")

        return None
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "", 
    response_model=PaginatedRenovaciones,
    tags=[router.tags[0]],
    summary="Obtener renovaciones",
    description="Obtener todas las renovaciones. Accesible para todos los usuarios."
)
def get_reservas(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    return RenovacionesService.obtener(page=page, limit=limit)


@router.get(
    "/{id}",
    response_model=Renovaciones,
    summary="Obtener una reserva por ID",
    description="Obtener una reserva específica de la base de datos por su ID. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_reserva_id(
    id: int,
    user = Depends(allow_everyone)
):
    reserva = RenovacionesService.obtener_por_id(id)  

    if reserva:
        return reserva
    else:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")


@router.get(
    "/user/{id_user}",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedRenovaciones,
    summary="Obtener renovaciones por user",
    description="Obtener todas las renovaciones de un usuario, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    id_user: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return RenovacionesService.obtener_por_user(id_user, page, limit)

@router.get(
    "/me/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedRenovaciones,
    summary="Obtener renovaciones por el usuario activo",
    description="Obtener todas las renovaciones del usuario activo solicitante, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    page: int = 1,
    limit: int = 10,
    current_user = Depends(allow_everyone)
):
    id_user = current_user["id"]
    return RenovacionesService.obtener_por_user(id_user, page, limit)