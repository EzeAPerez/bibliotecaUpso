from db.database import get_connection
from mysql.connector import IntegrityError, errorcode

class SedesRepository:

    @staticmethod
    def obtener(where_clauses=[], params=[]):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
                SELECT * FROM sedes
                {where_sql}
            """
        try:
            cursor.execute(query, (*params,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(sede:dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO sedes (
                    nombre
                )
                VALUES (%s)
                """
            
            cursor.execute(query, (sede.nombre,))

            id = cursor.lastrowid
            conexion.commit()

            return id
        
        finally:
            cursor.close()
            conexion.close()
        
    @staticmethod
    def modificar(id:int, sede:dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        try:
            query = """
                UPDATE sedes
                SET nombre = %s
                WHERE id = %s
            """

            cursor.execute(query, (sede.nombre, id))
            conexion.commit()
            
            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM sedes WHERE id = %s", (id,))

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
            cursor.execute("DELETE FROM sedes WHERE id = %s", (id,))
            eliminado = cursor.rowcount > 0

            conexion.commit()

            return eliminado
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()