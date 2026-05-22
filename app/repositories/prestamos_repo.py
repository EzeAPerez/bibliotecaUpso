from db.database import get_connection
from mysql.connector import IntegrityError
from repositories.reserva_repo import ReservaRepository

class PrestamosRepository:

    @staticmethod
    def obtener(where_clauses=[], params=[], page=1, limit=10):

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        offset = (page - 1) * limit
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT 
            *
        FROM prestamos
        {where_sql}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
        """

        try: 
            cursor.execute(query, (*params, limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(prestamo_data: dict):
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()

        try: 
            sql = """
                INSERT INTO prestamos(
                    id_ejemplar, id_reserva, id_user, 
                    id_sede, fecha_prestamo, fecha_devolucion, 
                    id_estado
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                """
            
            cursor.execute(sql, (
                prestamo_data.id_ejemplar, 
                prestamo_data.id_reserva, 
                prestamo_data.id_user,
                prestamo_data.id_sede,
                prestamo_data.fecha_prestamo,
                prestamo_data.fecha_devolucion, 
                prestamo_data.id_estado
            ))

            id_prestamo = cursor.lastrowid

            conexion.commit()

            return id_prestamo
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    
    @staticmethod
    def actualizar(id: int, campos: dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE prestamos SET {set_clause} WHERE id = %s"
            
            cursor.execute(sql, (*campos.values(), id))
            conexion.commit()

            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM prestamos WHERE id = %s", (id,))

            return cursor.fetchone()
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def actualizarEstado(id, id_estado, conexion= None):
        
        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()

        cursor = conexion.cursor(dictionary=True)

        try: 

            sql = """
                    UPDATE prestamos
                    SET id_estado = %s
                    WHERE id = %s
                """

            cursor.execute(sql, (id_estado, id))

            if own_connection: conexion.commit()

            if cursor.rowcount == 0:
                    return None

            cursor.execute("SELECT * FROM prestamos WHERE id= %s", (id, ))
            
            return cursor.fetchone()
        
        except IntegrityError as e:

            if own_connection: conexion.rollback()
            raise e

        finally:

            cursor.close()
            if own_connection: conexion.close()

    @staticmethod
    def eliminar(id: int):
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("DELETE FROM prestamos WHERE id = %s", (id,))
            
            eliminado = cursor.rowcount > 0

            conexion.commit()
            
            return eliminado
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def contar(where_clauses=None, params=None):
        where_clauses = where_clauses or []
        params = params or []

        conexion = get_connection()
        cursor = conexion.cursor()

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT COUNT(DISTINCT id)
            FROM prestamos
            {where_sql}
        """

        cursor.execute(query, params)
        total = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        return total
    
    @staticmethod
    def crear_por_reserva(
        reserva_data,
        conexion=None
    ):
        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()

        cursor = conexion.cursor()

        try:
            sql = """
                INSERT INTO prestamos(
                    id_ejemplar,
                    id_reserva,
                    id_user,
                    id_sede,
                    fecha_prestamo,
                    fecha_vencimiento,
                    id_estado
                )
                SELECT
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW(),
                    DATE_ADD(
                        NOW(),
                        INTERVAL r.cantidad_dias DAY
                    ),
                    %s
                FROM restricciones r
                WHERE r.id = %s
            """

            cursor.execute(sql, (
                reserva_data["id_ejemplar"],
                reserva_data["id"],
                reserva_data["id_user"],
                reserva_data["id_sede"],
                1,
                1
            ))

            id_prestamo = cursor.lastrowid

            # Solo commit si creó la conexión
            if own_connection:
                conexion.commit()

            return id_prestamo

        except IntegrityError as e:

            if own_connection:
                conexion.rollback()

            raise e

        except Exception:

            if own_connection:
                conexion.rollback()

            raise

        finally:
            cursor.close()

            if own_connection:
                conexion.close()