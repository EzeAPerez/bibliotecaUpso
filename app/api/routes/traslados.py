from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List
from mysql.connector import errorcode, IntegrityError
from repositories.traslados_repo import TrasladosRepository
from models.traslados import Traslados, TrasladosUpdate
from services.traslados_services import TrasladosService

from core.security import (
    allow_any_admin,
    allow_super_admin   
)

router = APIRouter(
    prefix="/traslados",
    tags=["traslados"]
)

@router.get(
    "", 
    response_model=list[Traslados],
    tags=[router.tags[0]],
    summary="Obtener traslados",
    description="Obtener todos los traslados."
)
def get_reservas(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_any_admin)
    ):

    rows = TrasladosRepository.obtener(page=page, limit=limit)

    return rows

@router.patch(
    "/{id}",
    tags=[router.tags[0]],
    summary="Modificar un traslado.",
    description="Modificar un traslado con id pasad por parametro. Accesible para super admin"
)
def modificar_traslado(
    id:int,
    traslado: TrasladosUpdate,
    current_user = Depends(allow_super_admin)
    ):
    try:
        data = traslado.model_dump(exclude_unset=True)

        return TrasladosService.actualizar(
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
            detail=f"Error interno del servidor: {e}"
        )


@router.patch(
    "/{id}/estado",
    status_code=status.HTTP_200_OK,
    summary="Modificar el estado del traslado",
    description="Modificar el estado del traslado. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def modificar_estado_reserva(
    id: int, 
    id_estado: int = Query(ge=1, le=4),
    current_user = Depends(allow_any_admin)
):
    
    try:
        return TrasladosService.modificar_estado(id, id_estado)
        
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar traslado",
    description="Eliminar una Traslado específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_Traslado(
    id: int,
    user = Depends(allow_super_admin)
):
    try:
        eliminado = TrasladosRepository.eliminar(id)
        
        if not eliminado:
            raise HTTPException(404, "Traslado no encontrada")

        return None
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )