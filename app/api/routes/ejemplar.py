from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.ejemplar import *
from mysql.connector import IntegrityError, errorcode
from repositories.ejemplar_repo import EjemplarRepository
from services.ejemplar_services import EjemplarService

from core.security import (
    allow_everyone,
    allow_super_admin
)

router = APIRouter(
    prefix="/ejemplar",
    tags=["ejemplar"]
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear ejemplar",
    description="Crear un nuevo ejemplar en la base de datos. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def crear_ejemplar(
    ejemplar: EjemplarCreate, 
    user = Depends(allow_super_admin)
):
    try:
        ejemplar_nuevo = Ejemplar.model_validate(ejemplar)
        return EjemplarRepository.crear(ejemplar_nuevo)
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(status_code=409, detail=f"Ya existe un ejemplar con código: {ejemplar.codigo_fisico}")
        raise HTTPException(status_code=400, detail=f"Error de integridad: {e.msg}")

@router.patch(
    "/{id}", 
    status_code=status.HTTP_200_OK,
    response_model=Ejemplar,
    summary="Modificar un ejemplar",
    description="Modificar el contenido de un ejemplar con id pasado por parametro. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
    )
def modificar_ejemplar(
    id: int,
    ejemplar_update: EjemplarUpdate,
    user = Depends(allow_super_admin)
):
    try:
        data = ejemplar_update.model_dump(exclude_unset=True)
        result = EjemplarRepository.actualizar(id, data)
        
        if not result:
            raise HTTPException(404, "Ejemplar no encontrada")
        else:
            return result
    
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe un ejemplar con el codigo: {ejemplar_update.codigo_fisico}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de integridad: {e.msg}")

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ejemplar",
    description="Eliminar un ejemplar específico de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_ejemplar(
    id: int,
    user = Depends(allow_super_admin)
):
    try:
        eliminado = EjemplarRepository.eliminar(id)
        
        if not eliminado:
            raise HTTPException(404, "Ejemplar no encontrada")

        return None
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "", 
    response_model=list[Ejemplar],
    tags=[router.tags[0]],
    summary="Obtener ejemplares",
    description="Obtener todas los ejemplares almacenados en la base de datos."
)
def get_ejemplar(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    rows = EjemplarRepository.obtener(page=page, limit=limit)

    return rows


@router.get(
    "/{id}",
    response_model=Ejemplar,
    summary="Obtener un ejemplar por ID",
    description="Obtener un ejemplar específica de la base de datos por su ID. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_ejemplar_id(
    id: int,
    user = Depends(allow_everyone)
):
    ejemplar = EjemplarService.obtener_por_id(id)  

    if ejemplar:
        return ejemplar
    else:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado")


@router.get(
    "/obra/{id_obra}",
    status_code=status.HTTP_200_OK,
    response_model=List[Ejemplar],
    summary="Obtener ejemplares por obra",
    description="Obtener todas los ejemplares de una obra de la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_ejempar_id_obra(
    id_obra: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    return EjemplarService.obtener_por_id_obra(id_obra, page, limit)
   

@router.get(
    "/estado/{id_estado}",
    response_model=List[Ejemplar],
    summary="Obtener ejemplares por estado",
    description="Obtener todas los ejemplares de un estado de la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_ejemplar_estado(
    id_estado: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    return EjemplarService.obtener_por_estado(id_estado, page, limit)

#### Ejemplar detallados con todos los datos de las obras ####

@router.get(
    "/detallado/", 
    response_model=list[EjemplarDetallado],
    tags=[router.tags[0]],
    summary="Obtener obras detallada",
    description="Obtener todas las obras con detalles de las subareas y areas. Accesible para todos los usuarios."
)
def get_ejemplar(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    rows = EjemplarRepository.obtener_detallado(page=page, limit=limit)

    return EjemplarService.procesar_ejemplares(rows)


@router.get(
    "/detallado/{id}/",
    response_model=EjemplarDetallado,
    summary="Obtener un ejemplar por ID",
    description="Obtener un ejemplar específica de la base de datos por su ID. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_ejemplar_id(
    id: int,
    user = Depends(allow_everyone)
):
    ejemplar = EjemplarService.obtener_por_id_detallado(id)  

    if ejemplar:
        return ejemplar
    else:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado")


@router.get(
    "/detallado/obra/{id_obra}",
    status_code=status.HTTP_200_OK,
    response_model=List[EjemplarDetallado],
    summary="Obtener ejemplares por obra",
    description="Obtener todas los ejemplares de una obra de la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_ejempar_id_obra(
    id_obra: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    return EjemplarService.obtener_por_id_obra_detallado(id_obra, page, limit)
   

@router.get(
    "/detallado/estado/{id_estado}",
    response_model=List[EjemplarDetallado],
    summary="Obtener ejemplares por estado",
    description="Obtener todas los ejemplares de un estado de la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_ejemplar_estado(
    id_estado: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    return EjemplarService.obtener_por_estado_detallado(id_estado, page, limit)
