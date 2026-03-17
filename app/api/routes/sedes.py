from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.sedes import Sede, SedeCreate, SedeUpdate
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode

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
    nueva_sede = Sede.model_validate(sede)
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    conexion.autocommit = False
    cursor = conexion.cursor()

    try:
        query = """
            INSERT INTO sedes (
                nombre
            )
            VALUES (%s)
            """
        
        cursor.execute(query, (nueva_sede.nombre,))

        id = cursor.lastrowid
        conexion.commit()

        cursor.close()
        conexion.close()

        return id

    except IntegrityError as e:
        conexion.rollback()

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una sede con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

    finally:
        cursor.close()
        conexion.close() 
   
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
    conexion = get_connection()
    
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        query = """
            UPDATE sedes
            SET nombre = %s
            WHERE id = %s
        """

        cursor.execute(query, (sede_update.nombre, id))
        conexion.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Sede no encontrada o no modificada"
            )

        cursor.close()
        conexion.close()

        return {
            "id": id,
            "nombre": sede_update.nombre
            }
    except IntegrityError as e:
        conexion.rollback()

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una sede con esos datos."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )
    
    finally:
        cursor.close()
        conexion.close()

    
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
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    conexion.autocommit = False
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM sedes WHERE id = %s", (id,))
        conexion.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        cursor.close()
        conexion.close()

        return None

    except IntegrityError as e:
        conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
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
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM sedes")
        resultados = cursor.fetchall()

        return resultados

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    finally:
        cursor.close()
        conexion.close()

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
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM sedes WHERE id = %s", (id,))

    sedes = cursor.fetchone()

    if not sedes:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    cursor.close()
    conexion.close()

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
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    cursor = conexion.cursor(dictionary=True)

    like = f"%{q}%"

    query = """
        SELECT * FROM sedes
        WHERE nombre LIKE %s
        """

    cursor.execute(query, (like,))

    sedes = cursor.fetchall()

    if not sedes:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    cursor.close()
    conexion.close()

    return sedes

