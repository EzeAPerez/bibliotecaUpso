from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.formato import Formato, FormatoCreate, FormatoUpdate
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.formato_repo import FormatoRepository

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/formato",
    tags=["formato"]
)

@router.post(
    "",
    response_model=int,
    summary="Crear formato",
    description="Crea un nuevo formato con los datos pasados por Request body. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_201_CREATED,
    tags=[router.tags[0]]
)
async def crear_formato(
    formato: FormatoCreate, 
    user = Depends(allow_super_admin)
):
    try:
        return FormatoRepository.crear(formato)
    
    except IntegrityError as e:

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un formato con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )
   
@router.patch(
    "/{id}", 
    summary="Modificar formato",
    description="Modificar el contenido de un formato con id pasada por paremetro. Solo accesible para SuperAdmin.",
    response_model=Formato,
    status_code=status.HTTP_200_OK, 
    tags=[router.tags[0]]
    )
def modificar_formato(
    id: int,
    formato: FormatoUpdate,
    user = Depends(allow_super_admin)
):    
    try:
        result = FormatoRepository.modificar(id, formato)

        if not result:
            raise HTTPException(404, "Formato no encontrado")
        else:
            return result
        
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un fromato con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

    
@router.delete(
    "/{id}", 
    summary="Eliminar formato",
    description="Eliminar un formato con id pasada por parametro. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[router.tags[0]]
    )
def eliminar_formato(
    id: int,
    user = Depends(allow_super_admin)
):
   
    try:
        eliminado = FormatoRepository.eliminar(id)

        if eliminado:
            return None
        else:
            raise HTTPException(status_code=404, detail="Formato no encontrado")


    except IntegrityError as e:
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el formato porque tiene ejemplares asociados"
            )

        raise HTTPException(
            status_code=500,
            detail="Error de integridad en la base de datos"
        )

@router.get(
    "",      
    response_model=List[Formato],
    summary="Listar formatos",
    description="Obtiene todas los formatos existentes. Accesible para todos los administradores.",
    tags=[router.tags[0]]
    )
def get_formatos(
    user = Depends(allow_any_admin)
):
    try:
        return FormatoRepository.obtener()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
