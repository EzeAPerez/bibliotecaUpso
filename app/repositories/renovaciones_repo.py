from db.database import get_connection
from mysql.connector import IntegrityError
from repositories.reserva_repo import ReservaRepository

class RenovacionesRepository:

    @staticmethod
    def obtener(where_clauses=[], params=[], page=1, limit=10):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        offset = (page - 1) * limit

        where_sql = (
            "WHERE " + " AND ".join(where_clauses)
            if where_clauses
            else ""
        )

        query= f"""
        SELECT
            r.id,
            r.fecha_renovacion,
            r.fecha_vencimiento_anterior,
            r.fecha_vencimiento_nueva,

            p.id AS id_prestamo,
            p.id_user,

            o.id AS id_obra,
            o.titulo,
            o.subtitulo,

            e.id AS id_ejemplar,
            e.codigo_fisico

        FROM renovaciones r
        INNER JOIN prestamos p
            ON r.id_prestamo = p.id
        INNER JOIN ejemplar e
            ON p.id_ejemplar = e.id
        INNER JOIN obras o
            ON e.id_obra = o.id; 
        
        {where_sql}

        ORDER BY p.id DESC

        LIMIT %s OFFSET %s

            """
        try:
            cursor.execute(query, (*params, limit, offset))
            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()  
    
    @staticmethod
    def crear(renovacion_data: dict):
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()

        try: 
            sql = """
                INSERT INTO renovaciones(
                    id_prestamo, 
                    fecha_renovacion, 
                    fecha_vencimiento_anterior,
                    fecha_vencimiento_nueva
                )
                VALUES(%s, %s, %s, %s)
                """
            
            cursor.execute(sql, (
                renovacion_data.id_prestamo,
                renovacion_data.fecha_renovacion,
                renovacion_data.fecha_vencimiento_anterior, 
                renovacion_data.fecha_vencimiento_nueva
            ))

            id_renovacion = cursor.lastrowid

            conexion.commit()

            return id_renovacion
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear_automatico(data, conexion=None):
        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()

        cursor = conexion.cursor(dictionary=True)

        try:
            sql = """
                INSERT INTO renovaciones(
                    id_prestamo,
                    fecha_renovacion,
                    fecha_vencimiento_anterior,
                    fecha_vencimiento_nueva
                )
                SELECT
                    %s,
                    NOW(),
                    %s,
                    DATE_ADD(
                        %s,
                        INTERVAL r.cantidad_dias DAY
                    )
                FROM restricciones r
                WHERE r.id = %s
            """

            cursor.execute(
                sql,
                (
                    data["id"],
                    data["fecha_vencimiento"],
                    data["fecha_vencimiento"],
                    1
                )
            )

            id_renovacion = cursor.lastrowid

            cursor.execute(
                """
                SELECT
                    id,
                    id_prestamo,
                    fecha_renovacion,
                    fecha_vencimiento_anterior,
                    fecha_vencimiento_nueva
                FROM renovaciones
                WHERE id = %s
                """,
                (id_renovacion,)
            )

            renovacion = cursor.fetchone()

            if own_connection:
                conexion.commit()

            return renovacion

        except IntegrityError:
            if own_connection:
                conexion.rollback()
            raise

        except Exception:
            if own_connection:
                conexion.rollback()
            raise

        finally:
            cursor.close()

            if own_connection:
                conexion.close()

    
    @staticmethod
    def actualizar(id: int, campos: dict, conexion):
        
        cursor = conexion.cursor(dictionary=True)

        try:
            if not campos:

                cursor.execute(
                    "SELECT * FROM renovaciones WHERE id = %s",
                    (id,)
                )

                prestamo = cursor.fetchone()

                if not prestamo:
                    raise LookupError(
                        "Renovacion no encontrada"
                    )

                return prestamo
             
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE renovaciones SET {set_clause} WHERE id = %s"
            
            cursor.execute(sql, (*campos.values(), id))
            
            cursor.execute("SELECT * FROM renovaciones WHERE id = %s", (id,))

            prestamo = cursor.fetchone()

            if not prestamo:
                raise LookupError(
                    "Renovacion no encontrada"
                )

            return prestamo
        
        except IntegrityError as e:
            raise e
        finally:
            cursor.close()
    

    @staticmethod
    def eliminar(id: int):
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("DELETE FROM renovaciones WHERE id = %s", (id,))
            
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
            FROM renovaciones
            {where_sql}
        """

        cursor.execute(query, params)
        total = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        return total