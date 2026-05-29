from db.database import get_connection
from mysql.connector import IntegrityError

class TrasladosRepository: 

    @staticmethod
    def obtener(where_clauses=[], params=[], page=1, limit=10):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        offset = (page - 1) * limit
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT
            t.id,

            t.id_ejemplar,
            e.codigo_fisico AS codigo_ejemplar,

            o.titulo AS titulo_obra,
            o.subtitulo AS subtitulo_obra,

            t.id_reserva,

            t.id_sede_origen,
            so.nombre AS nombre_sede_origen,

            t.id_sede_destino,
            sd.nombre AS nombre_sede_destino,

            t.fecha_solicitud,
            t.fecha_entrega,

            t.encargado,
            t.observaciones,

            t.id_estado,
            et.estado AS nombre_estado

        FROM traslados t

        LEFT JOIN ejemplar e
            ON t.id_ejemplar = e.id

        LEFT JOIN obras o
            ON e.id_obra = o.id

        LEFT JOIN sedes so
            ON t.id_sede_origen = so.id

        LEFT JOIN sedes sd
            ON t.id_sede_destino = sd.id

        LEFT JOIN estado_traslados et
            ON t.id_estado = et.id
        
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
    def crear(traslados_data: dict):

        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor(dictionary=True)

        try:

            # -----------------------------------------
            # VALIDAR RESERVA ACTIVA
            # -----------------------------------------
            sql_validacion = """
                SELECT id
                FROM traslados
                WHERE id_ejemplar = %s
                AND id_estado IN (1, 2)
                LIMIT 1
            """

            cursor.execute(
                sql_validacion,
                (traslados_data.id_ejemplar,)
            )

            reserva_existente = cursor.fetchone()

            if reserva_existente:
                raise ValueError(
                    "El ejemplar ya posee una reserva activa."
                )

            # -----------------------------------------
            # CREAR TRASLADO
            # -----------------------------------------
            sql = """
                INSERT INTO traslados (
                    id_ejemplar,
                    id_reserva,
                    id_sede_origen,
                    id_sede_destino,
                    fecha_solicitud,
                    fecha_entrega,
                    encargado,
                    observaciones,
                    id_estado
                )
                VALUES (
                    %s, %s, %s, %s,
                    NOW(),
                    %s, %s, %s, %s
                )
            """

            valores = (
                traslados_data.id_ejemplar,
                traslados_data.id_reserva,
                traslados_data.id_sede_origen,
                traslados_data.id_sede_destino,
                traslados_data.fecha_entrega,
                traslados_data.encargado,
                traslados_data.observaciones,
                traslados_data.id_estado
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
    def crear_por_reserva(conexion, id_reserva, id_sede):
        cursor = conexion.cursor()

        try: 
            sql = """
                INSERT INTO traslados (
                    id_reserva,
                    id_sede_destino,
                    fecha_solicitud,
                    id_estado
                )
                VALUES (%s, %s, NOW(), 1)
            """

            valores = (
                id_reserva,
                id_sede
            )

            cursor.execute(sql, valores)

            return cursor.lastrowid

        except Exception as e:
            raise e

        finally:
            cursor.close()
    
    @staticmethod
    def actualizar(id: int, campos: dict, conexion = None):
        
        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()
        
        cursor = conexion.cursor(dictionary=True)


        try:
            campos.pop("id_estado", None)

            if not campos:

                cursor.execute(
                    "SELECT * FROM traslados WHERE id = %s",
                    (id,)
                )

                traslado = cursor.fetchone()

                if not traslado:
                    raise LookupError(
                        "Traslado no encontrada"
                    )

                return traslado
            
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE traslados SET {set_clause} WHERE id = %s"

            cursor.execute(sql, (*campos.values(), id))
            
            cursor.execute("SELECT * FROM traslados WHERE id = %s", (id,))

            traslado = cursor.fetchone()

            if own_connection:
                conexion.commit()

            if not traslado:
                raise LookupError(
                    "Traslado no encontrada"
                )

            return traslado
        
        except IntegrityError as e:

            if own_connection:
                conexion.rollback()

            raise e

        except Exception as e:

            if own_connection:
                conexion.rollback()

            raise e

        finally:

            cursor.close()

            if own_connection:
                conexion.close()

    @staticmethod
    def actualizarEstado(
        id,
        id_estado,
        conexion=None
    ):

        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()

        cursor = conexion.cursor(dictionary=True)

        try:

            # -----------------------------------------
            # OBTENER ESTADO ACTUAL
            # -----------------------------------------
            cursor.execute(
                """
                SELECT *
                FROM traslados
                WHERE id = %s
                """,
                (id,)
            )

            traslado = cursor.fetchone()

            if not traslado:
                return None

            estado_actual = traslado["id_estado"]

            # -----------------------------------------
            # VALIDAR TRANSICIONES
            # -----------------------------------------

            # estados finales
            if estado_actual in [3, 4]:
                raise ValueError(
                    "El traslado ya se encuentra finalizado."
                )

            # validación extra
            if (
                id_estado in [2, 4]
                and traslado["id_ejemplar"] is None
            ):
                raise ValueError(
                    "El traslado requiere un ejemplar asignado."
                )

            # -----------------------------------------
            # UPDATE
            # -----------------------------------------
            sql = """
                UPDATE traslados
                SET id_estado = %s
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (id_estado, id)
            )

            if own_connection:
                conexion.commit()

            # -----------------------------------------
            # RETORNAR ACTUALIZADO
            # -----------------------------------------
            cursor.execute(
                """
                SELECT *
                FROM traslados
                WHERE id = %s
                """,
                (id,)
            )

            return cursor.fetchone()

        except IntegrityError as e:

            if own_connection:
                conexion.rollback()

            raise e

        except Exception as e:

            if own_connection:
                conexion.rollback()

            raise e

        finally:

            cursor.close()

            if own_connection:
                conexion.close()


    @staticmethod
    def eliminar(id: int):
        conexion = get_connection()
        cursor = conexion.cursor()

        try:
            cursor.execute("DELETE FROM traslados WHERE id = %s", (id,))
            eliminado = cursor.rowcount > 0

            conexion.commit()
            
            return eliminado

        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()