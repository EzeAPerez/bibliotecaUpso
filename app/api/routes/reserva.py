from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status, Query
from models.reserva import Reserva, ReservaCreate, ReservaDetallada, ReservaUpdate, ReservaCreateUser
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.reserva_repo import ReservaRepository
from services.reserva_services import ReservaService

from core.security import (
    allow_everyone,
    allow_super_admin,
    allow_any_admin
)

router = APIRouter(
    prefix="/reserva",
    tags=["reserva"]
)

@router.post(
    "/general/",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear una reserva",
    description="Crear una nueva reserva en la base de datos. Accesibles para todos los administradores.",
    tags=[router.tags[0]]
)
def crear_reserva_general(
    reserva: ReservaCreate, 
    current_user = Depends(allow_any_admin)
):
    try: 
        user_id = current_user["id"]

        reserva_data = reserva.model_dump()
        reserva_data["id_user"] = user_id

        reserva_nueva = Reserva.model_validate(reserva_data)

        return ReservaRepository.crear(reserva_nueva)

    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad: {e.msg}"
        )
    
## Crea una reserva del lado del usuario. Solo debe mandar la obra y la sede, el resto se encarga el sistema.

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear una reserva.",
    description="Crear una nueva reserva en la base de datos. Accesibles para todos los usuarios.",
    tags=[router.tags[0]]
)
def crear_reserva(
    reserva: ReservaCreateUser, 
    current_user = Depends(allow_everyone)
):
    try: 
        user_id = current_user["id"]

        reserva_data = reserva.model_dump()
        reserva_data["id_user"] = user_id

        return ReservaService.crear(reserva_data)

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
    summary="Modificar reserva",
    description="Modificar el contenido de una reserva con id pasado por parametro. Solo accesible para Aministradores.",
    tags=[router.tags[0]]
    )
def modificar_reserva(
    id: int,
    obra_update: ReservaUpdate,
    user = Depends(allow_any_admin)
):
    try:
        data = obra_update.model_dump(exclude_unset=True)

        return ReservaService.actualizar_admin(
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


@router.patch(
    "/{id}/estado",
    status_code=status.HTTP_200_OK,
    summary="Modificar el estado de la reserva",
    description="Modificar el estado de la reserva. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def modificar_estado_reserva(
    id: int, 
    id_estado: int = Query(ge=1, le=6),
    current_user = Depends(allow_any_admin)
):
    
    try:
        return ReservaService.modificar_estado(id, id_estado)
        
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reserva",
    description="Eliminar una reserva específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_reserva(
    id: int,
    user = Depends(allow_super_admin)
):
    try:
        eliminado = ReservaService.eliminar(id)
        
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
    response_model=list[Reserva],
    tags=[router.tags[0]],
    summary="Obtener reservas",
    description="Obtener todas las reservas. Accesible para todos los usuarios."
)
def get_reservas(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    rows = ReservaRepository.obtener(page=page, limit=limit)

    return rows

@router.get(
    "/{id}",
    response_model=Reserva,
    summary="Obtener una reserva por ID",
    description="Obtener una reserva específica de la base de datos por su ID. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_reserva_id(
    id: int,
    user = Depends(allow_everyone)
):
    reserva = ReservaService.obtener_por_id(id)  

    if reserva:
        return reserva
    else:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

@router.get(
    "/buscar/",
    response_model=List[Reserva],
    summary="Buscar una reserva especifica.",
    description="Buscar y obtener obras a partir del filtro de busqueda. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_reserva_buscar(
    q: str,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return ReservaService.obtener_por_busqueda(q, page, limit)


@router.get(
    "/sedes/{id_sede}",
    status_code=status.HTTP_200_OK,
    response_model=List[Reserva],
    summary="Obtener reserva por sedes",
    description="Obtener todas las reservas de una sede, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_sede(
    id_sede: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return ReservaService.obtener_por_sede(id_sede, page, limit)

@router.get(
    "/user/{id_user}",
    status_code=status.HTTP_200_OK,
    response_model=List[Reserva],
    summary="Obtener reserva por user",
    description="Obtener todas las reservas de un usuario, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    id_user: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return ReservaService.obtener_por_user(id_user, page, limit)

@router.get(
    "/me/",
    status_code=status.HTTP_200_OK,
    response_model=List[Reserva],
    summary="Obtener reserva por el usuario activo",
    description="Obtener todas las reservas del usuario activo solicitante, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    page: int = 1,
    limit: int = 10,
    current_user = Depends(allow_everyone)
):
    id_user = current_user["id"]
    return ReservaService.obtener_por_user(id_user, page, limit)


@router.get(
    "/detallada/", 
    response_model=list[ReservaDetallada],
    tags=[router.tags[0]],
    summary="Obtener reservas detalladas",
    description="Obtener todas las reservas detalladas. Accesible para todos los usuarios."
)
def get_reserva(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    rows = ReservaRepository.obtener_detallado(page=page, limit=limit)

    return rows

@router.get(
    "/detallada/{id}",
    response_model=ReservaDetallada,
    summary="Obtener una reserva detallada por ID",
    description="Obtener una reserva detallada específica de la base de datos por su ID. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_reserva_id(
    id: int,
    user = Depends(allow_everyone)
):
    Reserva = ReservaService.obtener_detallada_por_id(id)  

    if Reserva:
        return Reserva
    else:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

@router.get(
    "/detallada/buscar/",
    response_model=List[ReservaDetallada],
    summary="Buscar una reserva especifica.",
    description="Buscar y obtener las reservas a partir del filtro de busqueda. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_reserva_buscar(
    q: str,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return ReservaService.obtener_detallada_por_busqueda(q, page, limit)


@router.get(
    "/detallada/sedes/{id_sede}",
    status_code=status.HTTP_200_OK,
    response_model=List[ReservaDetallada],
    summary="Obtener reserva por sedes",
    description="Obtener todas las reservas de una sede, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_sede(
    id_sede: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return ReservaService.obtener_detallada_por_sede(id_sede, page, limit)

@router.get(
    "/detallada/user/{id_user}",
    status_code=status.HTTP_200_OK,
    response_model=List[ReservaDetallada],
    summary="Obtener reserva por user",
    description="Obtener todas las reservas de un usuario, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    id_user: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_any_admin)
):
    return ReservaService.obtener_detallada_por_user(id_user, page, limit)


@router.get(
    "/detallada/me/",
    status_code=status.HTTP_200_OK,
    response_model=List[ReservaDetallada],
    summary="Obtener reserva por user",
    description="Obtener todas las reservas de un usuario, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_reserva_user(
    page: int = 1,
    limit: int = 10,
    current_user = Depends(allow_any_admin)
):
    id_user = current_user["id"]
    return ReservaService.obtener_detallada_por_user(id_user, page, limit)