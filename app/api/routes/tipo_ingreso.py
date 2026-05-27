from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.tipo_ingreso import TipoIngreso, TipoIngresoCreate, TipoIngresoUpdate
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.tipo_ingreso_repo import TipoIngresoRepository

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/tipo_ingreso",
    tags=["tipo_ingreso"]
)

@router.post(
    "",
    response_model=int,
    summary="Crear un tipo de ingreso",
    description="Crea un nuevo tipo de ingreso con los datos pasados por Request body. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_201_CREATED,
    tags=[router.tags[0]]
)
async def crear_tipo_ingreso(
    tipo_ingreso: TipoIngresoCreate, 
    user = Depends(allow_super_admin)
):
    try:
        return TipoIngresoRepository.crear(tipo_ingreso)
    
    except IntegrityError as e:

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un tipo de ingreso con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )
   
@router.patch(
    "/{id}", 
    summary="Modificar tipo de ingreso",
    description="Modificar el contenido de un tipo de ingreso con id pasada por paremetro. Solo accesible para SuperAdmin.",
    response_model=TipoIngreso,
    status_code=status.HTTP_200_OK, 
    tags=[router.tags[0]]
    )
def modificar_tipo_ingreso(
    id: int,
    tipo_ingreso: TipoIngresoUpdate,
    user = Depends(allow_super_admin)
):    
    try:
        result = TipoIngresoRepository.modificar(id, tipo_ingreso)

        if not result:
            raise HTTPException(404, "Tipo de ingreso no encontrado")
        else:
            return result
        
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un tipo de ingreso con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

    
@router.delete(
    "/{id}", 
    summary="Eliminar tipo de ingreso",
    description="Eliminar un tipo de ingreso con id pasada por parametro. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[router.tags[0]]
    )
def eliminar_tipo_ingreso(
    id: int,
    user = Depends(allow_super_admin)
):
   
    try:
        eliminado = TipoIngresoRepository.eliminar(id)

        if eliminado:
            return None
        else:
            raise HTTPException(status_code=404, detail="Tipo de ingreso no encontrado")


    except IntegrityError as e:
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el tipo de ingreso porque tiene ejemplares asociados"
            )

        raise HTTPException(
            status_code=500,
            detail="Error de integridad en la base de datos"
        )

@router.get(
    "",      
    response_model=List[TipoIngreso],
    summary="Listar tipos de ingresos",
    description="Obtiene todas los tipos de ingresos existentes. Accesible para todos los administradores.",
    tags=[router.tags[0]]
    )
def get_sedes(
    user = Depends(allow_any_admin)
):
    try:
        return TipoIngresoRepository.obtener()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
