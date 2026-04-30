from db.database import get_connection
from mysql.connector import IntegrityError

class AreaTematicaRepository:

    @staticmethod
    def obtener(where_clauses=[]):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        try:
            cursor.execute(f"SELECT * FROM area_tematica {where_sql}")
            resultados = cursor.fetchall()

            return resultados
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(area_data: dict):
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()

        try:
            query = """
                INSERT INTO area_tematica (
                    nombre
                )
                VALUES (%s)
                """
            
            cursor.execute(query, (area_data.nombre,))

            id_area = cursor.lastrowid
            
            conexion.commit()

            return id_area
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def modificar(id:int, area_data:dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        try:
            query = """
                UPDATE area_tematica
                SET nombre = %s
                WHERE id = %s
            """

            cursor.execute(query, (area_data.nombre, id))
            conexion.commit()

            if cursor.rowcount == 0:
                return None
            
            return {
                "id": id,
                "nombre": area_data.nombre
            }

        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def eliminar(id:int):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("DELETE FROM area_tematica WHERE id = %s", (id,))
            eliminado = cursor.rowcount > 0
            conexion.commit()

            return eliminado

        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

