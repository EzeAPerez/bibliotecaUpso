from repositories.reserva_repo import ReservaRepository
from mysql.connector import IntegrityError 
from repositories.prestamos_repo import PrestamosRepository
from db.database import get_connection
from repositories.ejemplar_repo import EjemplarRepository
from repositories.traslados_repo import TrasladosRepository

class ReservaService: 

    @staticmethod
    def obtener_por_id(id:int):
        rows = ReservaRepository.obtener(
            where_clauses=["id = %s"],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None
            
### Corregir ###
    @staticmethod
    def obtener_por_busqueda(q: str, page=1, limit=10):
        like = f"%{q}%"
        rows = ReservaRepository.obtener(
            where_clauses=[
                "(o.titulo LIKE %s OR o.subtitulo LIKE %s OR o.autor LIKE %s OR at.nombre LIKE %s OR st.nombre LIKE %s)",
            ],
            params=[like, like, like, like, like],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def obtener_por_sede(id_sede: int, page=1, limit=10):
        rows = ReservaRepository.obtener(
            where_clauses=[
                "id_sede = %s"
            ],
            params=[id_sede],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def obtener_por_user(id_user: int, page=1, limit=10):
        rows = ReservaRepository.obtener(
            where_clauses=[
                "id_user = %s"
            ],
            params=[id_user],
            page=page,
            limit=limit
        )

        return rows
    
    
    @staticmethod
    def obtener_detallada_por_id(id:int):
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "r.id = %s"
            ],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None

    @staticmethod
    def obtener_detallada_por_busqueda(q: str, page=1, limit=10):
        like = f"%{q}%"
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "(o.titulo LIKE %s OR o.subtitulo LIKE %s OR o.autor LIKE %s)",
            ],
            params=[like, like, like],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def obtener_detallada_por_sede(id_sede: int, page=1, limit=10):
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "id_sede = %s"
            ],
            params=[id_sede],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def obtener_detallada_por_user(id_user: int, page=1, limit=10):
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "id_user = %s"
            ],
            params=[id_user],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def modificar_estado(
        id: int,
        id_estado: int,
        conexion=None
    ):
        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()

        try:
            reserva_actualizada = ReservaRepository.actualizarEstado(
                id,
                id_estado,
                conexion
            )
            
            response = {
                "nuevo estado": id_estado,
                "prestamo": None,
                "mensaje": "Estado actualizado correctamente."
            }
            if not reserva_actualizada:
                response = {
                    "estado": id_estado,
                    "prestamo": None,
                    "mensaje": "Estado sin actualizar."
                }
            
            if id_estado == 3 and reserva_actualizada:
                reserva_data = ReservaService.obtener_por_id(id)

                EjemplarRepository.actualizar_estado(
                    conexion,
                    reserva_data["id_ejemplar"],
                    3
                )

                id_prestamo = PrestamosRepository.crear_por_reserva(
                    reserva_data,
                    conexion
                )

                response["prestamo"] = {
                    "id": id_prestamo
                }

                response["mensaje"] = (
                    "Estado actualizado y préstamo creado automáticamente."
                )
            elif id_estado == 5 and reserva_actualizada:
                reserva_data = ReservaService.obtener_por_id(id)

                EjemplarRepository.actualizar_estado(
                    conexion,
                    reserva_data["id_ejemplar"],
                    2
                )

                response["mensaje"] = (
                    "Estado actualizado y ejemplar reservado"
                )
            elif id_estado == 6 and reserva_actualizada:
                reserva_data = ReservaService.obtener_detallada_por_id(id)

                EjemplarRepository.actualizar_estado(
                    conexion,
                    reserva_data["id_ejemplar"],
                    1
                )

            if own_connection:
                conexion.commit()

            return response

        except IntegrityError as e:
            if own_connection:
                conexion.rollback()

            raise ValueError(
                f"La reserva debe estar confirmada y tener ejemplar asignado.{e}"
            )

        except Exception:
            if own_connection:
                conexion.rollback()

            raise

        finally:
            if own_connection:
                conexion.close()
        
    @staticmethod
    def actualizar_admin(id: int, data: dict, conexion = None):

        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()

        conexion.cursor(dictionary=True)


        try:

            if own_connection: conexion.start_transaction()

            id_estado = data.pop("id_estado", None)


            result = ReservaRepository.actualizar(
                id,
                data,
                conexion=conexion
            )

            response_estado = None

            if id_estado is not None and id_estado != result["id_estado"]:
                    response_estado = (
                        ReservaService.modificar_estado(
                            id,
                            id_estado,
                            conexion=conexion
                        )
                    )

            if own_connection : conexion.commit()

            return {
                "reserva": result,
                "estado": response_estado
            }

        except Exception:

            if own_connection : conexion.rollback()
            raise

        finally:
            
            if own_connection : conexion.close()

    @staticmethod
    def crear(reserva_data):

        conexion = get_connection()
        conexion.autocommit = False

        try:
            ejemplares = EjemplarRepository.bloquear_disponibles(
                conexion,
                reserva_data["id_obra"]
            )

            reservas_en_espera = (
                ReservaRepository.contar_reservas_en_espera(
                    conexion,
                    reserva_data["id_obra"]
                )
            )

            disponibles = (
                len(ejemplares)
                - reservas_en_espera
            )

            ejemplar_en_sede = next(
                (
                    ejemplar
                    for ejemplar in ejemplares
                    if ejemplar["id_sede"] == reserva_data["id_sede"]
                ),
                None
            )

            if ejemplar_en_sede and disponibles > 0:

                EjemplarRepository.actualizar_estado(
                    conexion,
                    ejemplar_en_sede["id"],
                    2
                )

                id_reserva = ReservaRepository.crear_confirmada(
                    conexion,
                    reserva_data,
                    ejemplar_en_sede["id"]
                )

                conexion.commit()

                return id_reserva

            if disponibles <= 0:

                raise ValueError(
                    "No hay ejemplares disponibles"
                )

            id_reserva = ReservaRepository.crear_en_espera(
                conexion,
                reserva_data
            )

            TrasladosRepository.crear_por_reserva(
                conexion,
                id_reserva,
                reserva_data["id_sede"]
            )

            conexion.commit()

            return id_reserva

        except Exception as e:
            conexion.rollback()
            raise e

        finally:
            conexion.close()