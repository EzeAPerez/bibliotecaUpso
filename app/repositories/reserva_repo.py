from db.database import get_connection
from mysql.connector import IntegrityError

class ReservaRepository: 

    @staticmethod
    def obtener(where_clauses=[], params=[], page=1, limit=10):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        offset = (page - 1) * limit
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT 
            *
        FROM reserva
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
    def obtener_detallado(where_clauses=[], params=[], page=1, limit=10):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        offset = (page - 1) * limit

        where_sql = (
            "WHERE " + " AND ".join(where_clauses)
            if where_clauses
            else ""
        )

        query = f"""
        SELECT 
            r.id,
            r.id_obra,
            o.titulo,
            o.subtitulo,
            o.autor,

            r.id_ejemplar,
            e.codigo_fisico,

            r.id_sede,
            s.nombre AS nombre_sede,

            r.fecha_solicitud,
            r.fecha_confirmacion,
            r.fecha_retiro,

            r.id_estado,
            es.estado AS nombre_estado

        FROM reserva r

        JOIN obras o 
            ON r.id_obra = o.id

        LEFT JOIN ejemplar e 
            ON r.id_ejemplar = e.id

        JOIN sedes s 
            ON r.id_sede = s.id

        JOIN estado_reserva es 
            ON r.id_estado = es.id

        {where_sql}

        ORDER BY r.id DESC

        LIMIT %s OFFSET %s
        """

        try:
            cursor.execute(query, (*params, limit, offset))
            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()  


    """
    Original con los datos del usuarios. 
        SELECT 
            r.id,
            r.id_obra,
            o.titulo,
            o.autor,

            r.id_ejemplar,
            e.codigo_ejemplar,

            u.id AS id_user,
            u.email,

            r.id_sede,
            s.nombre AS nombre_sede,

            r.fecha_solicitud,
            r.fecha_confirmacion,
            r.fecha_retiro,

            r.id_estado,
            es.nombre AS nombre_estado

        FROM reserva r

        JOIN obras o 
            ON r.id_obra = o.id

        LEFT JOIN ejemplar e 
            ON r.id_ejemplar = e.id

        JOIN usuario u 
            ON r.id_user = u.id

        JOIN sedes s 
            ON r.id_sede = s.id

        JOIN estado_reserva es 
            ON r.id_estado = es.id

        {where_sql}

        ORDER BY r.id DESC

        LIMIT %s OFFSET %s
    """

    @staticmethod
    def crear(reserva_data: dict):
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()

        try: 
            sql = """
                INSERT INTO reserva (
                    id_obra,
                    id_ejemplar,
                    id_user,
                    id_sede,
                    fecha_solicitud,
                    fecha_confirmacion,
                    fecha_retiro,
                    id_estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                reserva_data.id_obra,
                reserva_data.id_ejemplar,
                reserva_data.id_user,
                reserva_data.id_sede,
                reserva_data.fecha_solicitud,
                reserva_data.fecha_confirmacion,
                reserva_data.fecha_retiro,
                reserva_data.id_estado
            )

            cursor.execute(sql, valores)

            conexion.commit()

            return cursor.lastrowid

        except Exception as e:
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
            sql = f"UPDATE reserva SET {set_clause} WHERE id = %s"

            cursor.execute(sql, (*campos.values(), id))
            conexion.commit()

            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM reserva WHERE id = %s", (id,))

            return cursor.fetchone()
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally: 
            cursor.close()
            conexion.close()
    
    @staticmethod
    def eliminar(id: int):
        conexion = get_connection()
        cursor = conexion.cursor()

        try:
            cursor.execute("DELETE FROM reserva WHERE id = %s", (id,))
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
            FROM reserva
            {where_sql}
        """

        cursor.execute(query, params)
        total = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        return total