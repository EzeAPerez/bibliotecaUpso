from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.area_tematica import CreateAreaTematica, AreaTematica, UpdateAreaTematica
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/area_tematica",
    tags=["areas_tematicas"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear area tematica",
    description="Crea una nueva area tematica con los datos pasados por Request body. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def crear_area_tematica(
    area_create: CreateAreaTematica,
    user = Depends(allow_super_admin)
):
    nueva_area = AreaTematica.model_validate(area_create)
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    conexion.autocommit = False
    cursor = conexion.cursor()

    try:
        query = """
            INSERT INTO area_tematica (
                nombre
            )
            VALUES (%s)
            """
        
        cursor.execute(query, (nueva_area.nombre,))

        id_area = cursor.lastrowid
        conexion.commit()

        cursor.close()
        conexion.close()

        return id_area

    except IntegrityError as e:
        conexion.rollback()

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un area tematica con el nombre: {nueva_area.nombre}"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

    finally:
        cursor.close()
        conexion.close()

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar área temática",
    description="Eliminar una área temática específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_area_tematica(
    id: int,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM area_tematica WHERE id = %s", (id,))
        conexion.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Área temática no encontrada")

        cursor.close()
        conexion.close()

        return None

    except IntegrityError as e:
        conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )


@router.patch(
    "/{id}",
    response_model=AreaTematica,
    summary="Modificar área temática",
    description="Modificar el contenido de una área temática con id pasado por parametro. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def modificar_area_tematica(
    id: int,
    area_update: UpdateAreaTematica,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        query = """
            UPDATE area_tematica
            SET nombre = %s
            WHERE id = %s
        """

        cursor.execute(query, (area_update.nombre, id))
        conexion.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Área temática no encontrada"
            )

        cursor.close()
        conexion.close()

        return {
            "id": id,
            "nombre": area_update.nombre
        }

    except IntegrityError:
        conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "",
    response_model=List[AreaTematica],
    summary="Obtener áreas temáticas",
    description="Obtiene todas las áreas temáticas. Accesible para todos los administradores.",
    tags=[router.tags[0]] 
)
def get_area_tematicas(user = Depends(allow_any_admin)):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM area_tematica")
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
    response_model=AreaTematica,
    summary="Obtener area tematica por id",
    description="Obtiene el nombre del area tematica a partir de su id. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_area_tematica_id(
    id: int,
    user = Depends(allow_any_admin)
):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM area_tematica WHERE id = %s", (id,))
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
        conexion.close()
