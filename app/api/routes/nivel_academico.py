from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.nivel_academico import NivelAcademico, NivelAcademicoCreate, NivelAcademicoUpdate
from typing import List
from mysql.connector import IntegrityError, errorcode
from repositories.nivel_academico_repo import NivelAcademicoRepository

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/nivel_academico",
    tags=["nivel_academico"]
)

@router.post(
    "",
    response_model=int,
    summary="Crear un nivel academico",
    description="Crea un nuevo nivel academico con los datos pasados por Request body. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_201_CREATED,
    tags=[router.tags[0]]
)
async def crear_nivel_academico(
    nivel_academico: NivelAcademicoCreate, 
    user = Depends(allow_super_admin)
):
    try:
        return NivelAcademicoRepository.crear(nivel_academico)
    
    except IntegrityError as e:

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un nivel academico con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )
   
@router.patch(
    "/{id}", 
    summary="Modificar nivel academico",
    description="Modificar el contenido de un nivel academico con id pasada por paremetro. Solo accesible para SuperAdmin.",
    response_model=NivelAcademico,
    status_code=status.HTTP_200_OK, 
    tags=[router.tags[0]]
    )
def modificar_sede(
    id: int,
    nivel_academico: NivelAcademicoUpdate,
    user = Depends(allow_super_admin)
):    
    try:
        result = NivelAcademicoRepository.modificar(id, nivel_academico)

        if not result:
            raise HTTPException(404, "Nivel academico no encontrado")
        else:
            return result
        
    except IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un nivel academico con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

    
@router.delete(
    "/{id}", 
    summary="Eliminar nivel academico",
    description="Eliminar un nivel academico con id pasada por parametro. Solo accesible para SuperAdmin.",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[router.tags[0]]
    )
def eliminar_sede(
    id: int,
    user = Depends(allow_super_admin)
):
   
    try:
        eliminado = NivelAcademicoRepository.eliminar(id)

        if eliminado:
            return None
        else:
            raise HTTPException(status_code=404, detail="Nivel academico no encontrado")


    except IntegrityError as e:
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el nivel academico porque tiene obras asociadas"
            )

        raise HTTPException(
            status_code=500,
            detail="Error de integridad en la base de datos"
        )

@router.get(
    "",      
    response_model=List[NivelAcademico],
    summary="Listar niveles academicos",
    description="Obtiene todas los niveles academicos existentes. Accesible para todos los administradores.",
    tags=[router.tags[0]]
    )
def get_sedes(
    user = Depends(allow_any_admin)
):
    try:
        return NivelAcademicoRepository.obtener()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
