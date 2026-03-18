from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode
from models.subarea_tematica import CreateSubAreaTematica, SubAreaTematica, UpdateSubAreaTematica

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/subarea_tematica",
    tags=["sub_area_tematicas"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear subárea temática",
    description="Crear una subárea temática con el contenido pasado por parametro. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def crear_subarea_tematica(
    subarea_create: CreateSubAreaTematica,
    user = Depends(allow_super_admin)
):
    nueva_subarea = SubAreaTematica.model_validate(subarea_create)
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    conexion.autocommit = False
    cursor = conexion.cursor()

    try:
        query = """
            INSERT INTO subarea_tematica (
                nombre,
                id_area_tematica
            )
            VALUES (%s, %s)
            """
        
        cursor.execute(query, (nueva_subarea.nombre, nueva_subarea.id_area_tematica))

        id_subarea = cursor.lastrowid
        conexion.commit()

        cursor.close()
        conexion.close()

        return id_subarea

    except IntegrityError as e:
        conexion.rollback()

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un subarea tematica con el nombre: {nueva_subarea.nombre} y {nueva_subarea.id_area_tematica}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

    finally:
        cursor.close()
        conexion.close()

@router.patch(
    "/{id}",
    response_model=SubAreaTematica,
    summary="Modificar subárea temática",
    description="Modificar el contenido de una subárea temática con id pasado por parametro",
    tags=[router.tags[0]]
)
def modificar_subarea_tematica(
    id: int,
    subarea_update: UpdateSubAreaTematica
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        query = """
            UPDATE subarea_tematica
            SET nombre = %s, id_area = %s
            WHERE id = %s
        """

        cursor.execute(query, (subarea_update.nombre, subarea_update.id_area, id))
        conexion.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Subárea temática no encontrada"
            )

        cursor.close()
        conexion.close()

        return {
            "id": id,
            "nombre": subarea_update.nombre,
            "id_area": subarea_update.id_area
        }

    except IntegrityError:
        conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar subárea temática",
    description="Eliminar una subárea temática específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_subarea_tematica(
    id: int,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM subarea_tematica WHERE id = %s", (id,))
        conexion.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subárea temática no encontrada")

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
    response_model=List[SubAreaTematica],
    summary="Obtener subáreas temáticas",
    description="Obtiene todas las subáreas temáticas. Accesible para todos los administradores.",
    tags=[router.tags[0]] 
)
def get_subarea_tematicas(user = Depends(allow_any_admin)):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM subarea_tematica")
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
    response_model=SubAreaTematica,
    summary="Obtener subarea tematica por id",
    description="Obtiene el nombre del subarea tematica a partir de su id. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_subarea_tematica_id(
    id: int,
    user = Depends(allow_any_admin)
):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM subarea_tematica WHERE id = %s", (id,))
        resultados = cursor.fetchall()
        
        return resultados[0]

    except Exception as e:
        if resultados is None or len(resultados) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subárea temática no encontrada"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    finally:
        cursor.close() 
