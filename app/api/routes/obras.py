from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.obras import ObraCreate, ObraUpdate, Obras, ObraDetallada
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.obras_repo import ObraRepository
from services.obras_services import ObraService

from core.security import (
    allow_everyone,
    allow_super_admin
)

router = APIRouter(
    prefix="/obras",
    tags=["obras"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear obra",
    description="Crear una nueva obra en la base de datos. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def crear_obra(
    obra: ObraCreate, 
    user = Depends(allow_super_admin)
):
    try:
        obra_nueva = Obras.model_validate(obra)
        return ObraRepository.crear(obra_nueva, obra.subareas)
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(status_code=409, detail=f"Ya existe un libro con código: {obra.codigo_fisico}")
        raise HTTPException(status_code=400, detail=f"Error de integridad: {e.msg}")

@router.patch(
    "/{id}", 
    status_code=status.HTTP_200_OK,
    response_model=Obras,
    summary="Modificar obra",
    description="Modificar el contenido de una obra con id pasado por parametro. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
    )
def modificar_obras(
    id: int,
    obra_update: ObraUpdate,
    user = Depends(allow_super_admin)
):
    try:
        data = obra_update.model_dump(exclude_unset=True)
        result = ObraRepository.actualizar(id, data)
        
        if not result:
            raise HTTPException(404, "Obra no encontrada")
        else:
            return result
    
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe una obra con el codigo: {obra_update.codigo_fisico}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de integridad: {e.msg}")

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar obra",
    description="Eliminar una obra específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_obras(
    id: int,
    user = Depends(allow_super_admin)
):
    try:
        eliminado = ObraRepository.eliminar(id)
        
        if not eliminado:
            raise HTTPException(404, "Obra no encontrada")

        return None
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "", 
    response_model=list[ObraDetallada],
    tags=[router.tags[0]],
    summary="Obtener obras detallada",
    description="Obtener todas las obras con detalles de las subareas y areas. Accesible para todos los usuarios."
)
def get_obras(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    rows = ObraRepository.obtener_base(page=page, limit=limit)

    return ObraService.procesar_obras(rows)

@router.get(
    "/estado/{id_estado}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por estado",
    description="Obtener todas las obras de un estado de la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_estado(
    id_estado: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    return ObraService.obtener_por_estado(id_estado, page, limit)

@router.get(
    "/tipo/{id_tipo}",
    status_code=status.HTTP_200_OK,
    response_model=List[ObraDetallada],
    summary="Obtener obras por tipo",
    description="Obtener todas las obras de un tipo la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_tipo(
    id_tipo: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    return ObraService.obtener_por_tipo(id_tipo, page, limit)

@router.get(
    "/{id}",
    response_model=ObraDetallada,
    summary="Obtener una obra por ID",
    description="Obtener una obra específica de la base de datos por su ID. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_id(
    id: int,
    user = Depends(allow_everyone)
):
    obra = ObraService.obtener_por_id(id)  

    if obra:
        return obra
    else:
        raise HTTPException(status_code=404, detail="Obra no encontrada")

@router.get(
    "/codigo/{codigo:path}",
    response_model=ObraDetallada,
    summary="Obtener una obra por código",
    description="Obtener una obra específica de la base de datos por su código. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_codigo(
    codigo: str,
    user = Depends(allow_everyone)
):
    obra = ObraService.obtener_por_codigo(codigo)
    if obra:
        return obra
    else:
        raise HTTPException(status_code=404, detail="Obra no encontrada")

@router.get(
    "/buscar/",
    response_model=List[ObraDetallada],
    summary="Buscar una obra especifica.",
    description="Buscar y obtener obras a partir del filtro de busqueda. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_buscar(
    q: str,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    return ObraService.obtener_por_busqueda(q, page, limit)

@router.get(
    "/area_tematica/{id_area}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por area tematica",
    description="Obtener todas las obras almacenadas en la base de datos de un area tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_area_tematica(
    id_area: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    return ObraService.obtener_por_area_tematica(id_area, page, limit)

@router.get(
    "/subarea_tematica/{id_subarea}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por subarea tematica",
    description="Obtener todas las obras almacenadas en la base de datos de un subarea tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_sub_area_tematica(
    id_subarea: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    return ObraService.obtener_por_area_tematica(id_subarea, page, limit)

@router.get(
    "/sede/{id_sede}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por sede",
    description="Obtener todas las obras almacenadas en la base de datos de una sede expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_sede(
    id_sede: int,
    page: int = 1,
    limit: int =10,
    user = Depends(allow_everyone)
):
    return ObraService.obtener_por_sede(id_sede, page, limit)

@router.get(
    "/cantidad/",
    response_model=int,
    summary="Obtener la cantidad de obras",
    description="Obtener la cantidad de obras almacenadas en la base de datos. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cant_obras(
    user = Depends(allow_everyone)
):
    return ObraService.contar_obras()

@router.get(
    "/buscar/cantidad",
    response_model=int,
    summary="Cantidad de obras segun filtro de busqueda",
    description="Obtener la cantidad de obras almacenadas en la base de datos segun el filtro de busqueda. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cantidad_obras_buscar(
    q: str,
    user = Depends(allow_everyone)
):
    return ObraService.contar_por_busqueda(q)



@router.get(
    "/tipo/{id_tipo}/cantidad",
    response_model=int,
    summary="Obtener la cantidad de obras de un tipo",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un tipo expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cant_obras_tipo(
    id_tipo: int,
    user = Depends(allow_everyone)
):
    return ObraService.contar_por_tipo(id_tipo)


@router.get(
    "/estado/{id_estado}/cantidad",
    response_model=int,
    summary="Obtener la cantidad de obras de un estado",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un estado expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cant_obras_estado(
    id_estado: int,
    user = Depends(allow_everyone)
):
    return ObraService.contar_por_estado(id_estado)


@router.get(
    "/area_tematica/{id_area}/cantidad",
    response_model=int,
    summary="Cantidad de obras por area tematica",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un area tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cantidad_obras_area_tematica(
    id_area: int,
    user = Depends(allow_everyone)
):
    return ObraService.contar_por_area(id_area)

@router.get(
    "/subarea_tematica/{id_subarea}/cantidad",
    response_model=int,
    summary="Cantidad de obras por subarea tematica",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un subarea tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cantidad_obras_sub_area_tematica(
    id_subarea: int,
    user = Depends(allow_everyone)
):
    return ObraService.contar_por_subarea(id_subarea)