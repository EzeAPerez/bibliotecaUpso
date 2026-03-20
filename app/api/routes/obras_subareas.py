from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode
from models.obras_subareas import ObraYSubarea, ObrasySubareasDetallado, ModificarObraYSubarea

from core.security import (
    allow_any_admin,
    allow_super_admin
)

router = APIRouter(
    prefix="/obras_subareas",
    tags=["obras_y_subareas"]
)
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Asignar subárea temática a obra",
    description="Asignar una subárea temática a una obra específica por sus IDs. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def asignar_subarea_obra(
    obra_subarea: ObraYSubarea,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    conexion.autocommit = False
    cursor = conexion.cursor()

    try:
        query = """
            INSERT INTO obra_subarea_tematica (
                id_obra,
                id_subarea
            )
            VALUES (%s, %s)
            """
        
        cursor.execute(query, (obra_subarea.id_obra, obra_subarea.id_subarea))

        conexion.commit()

    except IntegrityError as e:
        conexion.rollback()

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La obra ya tiene asignada esa subárea temática"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

    finally:
        cursor.close()
        conexion.close()

@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    summary="Modificar asignación de subárea temática a obra",
    description="Modificar la asignación de una subárea temática a una obra específica por sus IDs. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def modificar_subarea_obra(
    obra_subarea: ModificarObraYSubarea,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    conexion.autocommit = False
    cursor = conexion.cursor()

    try:
        query = """
            UPDATE obra_subarea_tematica
            SET id_subarea = %s
            WHERE id_obra = %s AND id_subarea = %s
            """
        
        cursor.execute(query, (obra_subarea.id_subarea_nueva, obra_subarea.id_obra, obra_subarea.id_subarea))
        conexion.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="La ralacion obra subarea tematica no existe"
            )
        
        return {"message": "Relación actualizada correctamente"}
    except IntegrityError as e:
        conexion.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

    finally:
        cursor.close()
        conexion.close()

@router.delete(
    "/{id_obra}/{id_subarea}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar subárea temática de obra",
    description="Eliminar la asignación de una subárea temática a una obra específica por sus IDs. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_subarea_obra(
    id_obra: int,
    id_subarea: int,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    conexion.autocommit = False
    cursor = conexion.cursor()

    try:
        query = """
            DELETE FROM obra_subarea_tematica
            WHERE id_obra = %s AND id_subarea = %s
            """
        
        cursor.execute(query, (id_obra, id_subarea))

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="La realcion obra subarea tematica no existe"
            )

        conexion.commit()

    except IntegrityError as e:
        conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

    finally:
        cursor.close()
        conexion.close()

@router.get(
    "",
    response_model=List[ObrasySubareasDetallado],
    summary="Obtener las relaciones entre las obras y las subáreas temáticas",
    description="Obtener todas las relaciones obras subáreas temáticas asignadas. Accesible para todos los administradores.",
    tags=[router.tags[0]]
)
def get_subareas_obra(
    user = Depends(allow_any_admin)
):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                ost.id_obra,
                o.titulo AS nombre_obra,
                ost.id_subarea,
                st.nombre AS nombre_subarea,
                at.id AS id_area,
                at.nombre AS nombre_area
            FROM obra_subarea_tematica ost
            JOIN obras o ON ost.id_obra = o.id
            JOIN subarea_tematica st ON ost.id_subarea = st.id
            JOIN area_tematica at ON st.id_area_tematica = at.id
        """)
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
