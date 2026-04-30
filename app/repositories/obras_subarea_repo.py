from db.database import get_connection
from mysql.connector import IntegrityError, errorcode

class ObraSubareaRepository:

    @staticmethod
    def obtener():
        conexion = get_connection()
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
            result = cursor.fetchall()

            return result
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def asignar(obra_subarea: dict):
        conexion = get_connection()
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
            raise e
        finally:
            cursor.close()
            conexion.close()

    def modificar(obra_subarea: dict):
        conexion = get_connection()
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

            return cursor.rowcount
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    def eliminar(id_obra: int, id_subarea):
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()

        try:
            query = """
                DELETE FROM obra_subarea_tematica
                WHERE id_obra = %s AND id_subarea = %s
                """
            
            cursor.execute(query, (id_obra, id_subarea))
            conexion.commit()

            return cursor.rowcount
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()