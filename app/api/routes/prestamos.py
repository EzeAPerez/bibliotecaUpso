from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status, Query
from models.prestamos import Prestamos, PrestamosUpdate, PrestamosCreate
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.prestamos_repo import PrestamosRepository
from services.prestamos_service import PrestamosService

from core.security import (
    allow_everyone,
    allow_super_admin,
    allow_any_admin
)

router = APIRouter(
    prefix="/prestamos",
    tags=["prestamos"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear un prestamo",
    description="Crear un nuevo prestamo en la base de datos. Accesibles para todos los usuarios.",
    tags=[router.tags[0]]
)
def crear_prestamo(
    prestamo: PrestamosCreate, 
    current_user = Depends(allow_everyone)
):
    try: 
        user_id = current_user["id"]

        prestamo_data = prestamo.model_dump()
        prestamo_data["id_user"] = user_id

        prestamo_nuevo = Prestamos.model_validate(prestamo_data)

        return PrestamosRepository.crear(prestamo_nuevo)

    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad: {e.msg}"
        )
    

@router.patch(
    "/{id}", 
    status_code=status.HTTP_200_OK,
    response_model=Prestamos,
    summary="Modificar prestamo",
    description="Modificar el contenido de un prestamo con id pasado por parametro. Solo accesible para Aministradores.",
    tags=[router.tags[0]]
    )
def modificar_prestamo(
    id: int,
    obra_update: PrestamosUpdate,
    user = Depends(allow_any_admin)
):
    try:
        data = obra_update.model_dump()
        result = PrestamosRepository.actualizar(id, data)
        
        if not result:
            raise HTTPException(404, "Reserva no encontrada")
        else:
            return result
    
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de integridad: {e.msg}")

@router.patch(
    "/{id}/estado",
    status_code=status.HTTP_200_OK,
    summary="Modificar el estado del prestamo",
    description="Modificar el estado del prestamo. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def modificar_estado_prestamo(
    id: int, 
    id_estado: int = Query(ge=1, le=3),
    current_user = Depends(allow_any_admin)
):
    
    try:
        return PrestamosService.modificar_estado(id, id_estado)
        
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar prestamo",
    description="Eliminar un prestamo específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_prestamo(
    id: int,
    user = Depends(allow_super_admin)
):
    try:
        eliminado = PrestamosRepository.eliminar(id)
        
        if not eliminado:
            raise HTTPException(404, "Prestamo no encontrado")

        return None
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "", 
    response_model=list[Prestamos],
    tags=[router.tags[0]],
    summary="Obtener prestamos",
    description="Obtener todas los prestamos. Accesible para todos los usuarios."
)
def get_prestamos(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    rows = PrestamosRepository.obtener(page=page, limit=limit)

    return rows

@router.get(
    "/{id}",
    response_model=Prestamos,
    summary="Obtener un prestamo por ID",
    description="Obtener un prestmoa específica de la base de datos por su ID. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_prestamo_id(
    id: int,
    user = Depends(allow_everyone)
):
    prestamo = PrestamosService.obtener_por_id(id)  

    if prestamo:
        return prestamo
    else:
        raise HTTPException(status_code=404, detail="Prestamo no encontrada")

@router.get(
    "/sedes/{id_sede}",
    status_code=status.HTTP_200_OK,
    response_model=List[Prestamos],
    summary="Obtener prestamos por sedes",
    description="Obtener todas los prestamos de una sede, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_sede(
    id_sede: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return PrestamosService.obtener_por_sede(id_sede, page, limit)

@router.get(
    "/user/{id_user}",
    status_code=status.HTTP_200_OK,
    response_model=List[Prestamos],
    summary="Obtener prestamos por user",
    description="Obtener todos los prestamos de un usuario, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    id_user: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return PrestamosService.obtener_por_user(id_user, page, limit)

@router.get(
    "/me/",
    status_code=status.HTTP_200_OK,
    response_model=List[Prestamos],
    summary="Obtener prestamos por el usuario activo",
    description="Obtener todas las prestamos del usuario activo solicitante, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    page: int = 1,
    limit: int = 10,
    current_user = Depends(allow_everyone)
):
    id_user = current_user["id"]
    return PrestamosService.obtener_por_user(id_user, page, limit)