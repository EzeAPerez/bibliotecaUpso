from db.database import get_connection
from mysql.connector import IntegrityError, errorcode

class FormatoRepository:

    @staticmethod
    def obtener():
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = f"""
                SELECT * FROM formato
            """
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(formato:dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO formato (
                    nombre
                )
                VALUES (%s)
                """
            
            cursor.execute(query, (formato.nombre,))

            id = cursor.lastrowid
            conexion.commit()

            return id
        
        finally:
            cursor.close()
            conexion.close()
        
    @staticmethod
    def modificar(id:int, formato:dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        try:
            query = """
                UPDATE formato
                SET nombre = %s
                WHERE id = %s
            """

            cursor.execute(query, (formato.nombre, id))
            conexion.commit()
            
            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM formato WHERE id = %s", (id,))

            return cursor.fetchone()
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def eliminar(id:int):
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("DELETE FROM formato WHERE id = %s", (id,))
            eliminado = cursor.rowcount > 0

            conexion.commit()

            return eliminado
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()