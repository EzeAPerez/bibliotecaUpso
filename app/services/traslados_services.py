from repositories.traslados_repo import TrasladosRepository
from mysql.connector import IntegrityError 
from db.database import get_connection
from services.reserva_services import ReservaService

class TrasladosService:

    @staticmethod
    def modificar_estado(
        id: int,
        id_estado: int,
        conexion = None
    ):

        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()
            
        try:
            traslado_modificado = (
                TrasladosRepository.actualizarEstado(
                    id,
                    id_estado,
                    conexion
                )
            )

            if not traslado_modificado:

                raise LookupError(
                    "Traslado no encontrado o no válido."
                )

            response = {
                "Nuevo estado traslado": id_estado,
                "reserva": None,
                "mensaje": (
                    f"Se modificó correctamente "
                    f"el estado del traslado {id}"
                )
            }

            if (
                id_estado == 2
                and traslado_modificado["id_reserva"] is not None
            ):
                reserva_response = (
                    ReservaService.actualizar_admin(
                        traslado_modificado["id_reserva"],
                        {
                            "id_estado" : 5,
                            "id_ejemplar" : traslado_modificado["id_ejemplar"]
                         },
                        conexion=conexion
                    )
                )


                response["reserva"] = reserva_response

                response["mensaje"] = (
                    "El traslado fue confirmado y "
                    "la reserva actualizada correctamente."
                )

            elif (
                id_estado == 3
                and traslado_modificado["id_reserva"] is not None
            ):

                reserva_response = (
                    ReservaService.modificar_estado(
                        traslado_modificado["id_reserva"],
                        6,
                        conexion=conexion
                    )
                )

                response["reserva"] = reserva_response

                response["mensaje"] = (
                    "El traslado fue cancelado y "
                    "la reserva actualizada correctamente."
                )

            if own_connection:
                conexion.commit()

            return response

        except IntegrityError as e:
            if own_connection:
                conexion.rollback()

            raise ValueError(
                f"El estado del traslado no puede ser modificado porque no cumple las politicas. {e}"
            )

        except Exception as e:
            if own_connection:
                conexion.rollback()

            raise e

        finally:
            if own_connection:
                conexion.close()

    @staticmethod
    def actualizar(id: int, data: dict):
        
        conexion = get_connection()

        try:

            conexion.start_transaction()

            id_estado = data.pop("id_estado", None)


            result = TrasladosRepository.actualizar(
                id,
                data,
                conexion=conexion
            )

            response_estado = None

            if id_estado is not None and id_estado != result["id_estado"]:

                response_estado = (
                    TrasladosService.modificar_estado(
                        id,
                        id_estado,
                        conexion=conexion
                    )
                )
                

            conexion.commit()

            return {
                "traslado": result,
                "estado": response_estado
            }

        except Exception as e:

            conexion.rollback()
            raise e

        finally:

            conexion.close()