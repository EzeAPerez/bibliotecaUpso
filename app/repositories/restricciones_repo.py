from db.database import get_connection
from mysql.connector import IntegrityError, errorcode

class RestriccionesRepository:

    @staticmethod
    def obtener():
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = f"""
                SELECT * FROM restricciones
            """
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()
        
    @staticmethod
    def modificar(campos: dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        try:
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE prestamos SET {set_clause} WHERE id = 1"
            cursor.execute(sql, (*campos.values(), ))
            
            conexion.commit()
            
            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM restricciones WHERE id = 1",)

            return cursor.fetchone()
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()
