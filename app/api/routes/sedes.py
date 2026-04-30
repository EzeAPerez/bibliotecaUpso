from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.sedes import Sede, SedeCreate, SedeUpdate
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.sedes_repo import SedesRepository
from services.sedes_service import SedesService

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/sedes",
    tags=["sedes"]
)

@router.post(
    "",
    response_model=int,
    summary="Crear sede",
    description="Crea una nueva sede con los datos pasados por Request body. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_201_CREATED,
    tags=[router.tags[0]]
)
async def crear_sede(
    sede: SedeCreate, 
    user = Depends(allow_super_admin)
):
    try:
        return SedesRepository.crear(sede)
    
    except IntegrityError as e:

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una sede con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )
   
@router.patch(
    "/{id}", 
    summary="Modificar sede",
    description="Modificar el contenido de una sede con id pasada por paremetro. Solo accesible para SuperAdmin.",
    response_model=Sede,
    status_code=status.HTTP_200_OK, 
    tags=[router.tags[0]]
    )
def modificar_sede(
    id: int,
    sede_update: SedeUpdate,
    user = Depends(allow_super_admin)
):    
    try:
        result = SedesRepository.modificar(id, sede_update)

        if not result:
            raise HTTPException(404, "Sede no encontrada")
        else:
            return result
        
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una sede con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

    
@router.delete(
    "/{id}", 
    summary="Eliminar sede",
    description="Eliminar una sede con id pasada por parametro. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[router.tags[0]]
    )
def eliminar_sede(
    id: int,
    user = Depends(allow_super_admin)
):
   
    try:
        eliminado = SedesRepository.eliminar(id)

        if eliminado:
            return None
        else:
            raise HTTPException(status_code=404, detail="Sede no encontrada")


    except IntegrityError as e:
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la sede porque tiene obras asociadas"
            )

        raise HTTPException(
            status_code=500,
            detail="Error de integridad en la base de datos"
        )

@router.get(
    "",      
    response_model=List[Sede],
    summary="Listar sedes",
    description="Obtiene todas las sedes existentes. Accesible para todos los administradores.",
    tags=[router.tags[0]]
    )
def get_sedes(
    user = Depends(allow_any_admin)
):
    try:
        return SedesRepository.obtener()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{id}",
    response_model=Sede,
    summary="Obtener sede por id",
    description="Obtiene una sede por su id. Accesible para todos los administradores.",
    tags=[router.tags[0]]
    )
def sede_por_id(
    id: int,
    user = Depends(allow_any_admin)
):
    sedes = SedesService.obtener_por_id(id)

    if not sedes:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    return sedes


@router.get(
    "/buscar/",
    response_model=List[Sede],
    summary="Buscar sedes por nombre o direccion",
    description="Obtiene todas las sedes filtradas por nombre o direccion. Accesible para todos los administradores. Accesible para todos los administradores.",
    tags=[router.tags[0]]
    )
def buscar_sedes(
    q: str,
    user = Depends(allow_any_admin)
):
    sedes = SedesService.obtener_por_buscar(q)

    if not sedes:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    return sedes

