from repositories.prestamos_repo import PrestamosRepository
from repositories.ejemplar_repo import EjemplarRepository
from db.database import get_connection
from mysql.connector import IntegrityError 

class PrestamosService: 

    @staticmethod
    def obtener_por_id(id:int):
        rows = PrestamosRepository.obtener(
            where_clauses=["id = %s"],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None
            
    @staticmethod
    def obtener_por_sede(id_sede: int, page=1, limit=10):
        rows = PrestamosRepository.obtener(
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
        rows = PrestamosRepository.obtener(
            where_clauses=[
                "id_user = %s"
            ],
            params=[id_user],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def actualizar(id, data):
        conexion = get_connection()

        try:
            id_estado = data.pop("id_estado", None)

            result = PrestamosRepository.actualizar(id, data, conexion)

            response_estado = None
        
            if id_estado is not None and id_estado != result["id_estado"]:
                response_estado = (
                    PrestamosService.modificar_estado(
                        id, id_estado, conexion
                    )
                )
            
            conexion.commit()
            
            return {
                "prestamo": result,
                "estado": response_estado
            }
        
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close


    @staticmethod
    def modificar_estado(id, id_estado, conexion=None):

        own_connection = conexion is None

        if own_connection:
            conexion = get_connection()
            
        try:
            prestamo_modificado = (
                PrestamosRepository.actualizarEstado(
                    id,
                    id_estado,
                    conexion
                )
            )

            response = {
                "Nuevo estado prestamo": id_estado,
                "mensaje": (
                    f"Se modificó correctamente "
                    f"el estado del prestamo {id}"
                )
            }

            # Estado Activo
            if id_estado == 1:
                EjemplarRepository.actualizar_estado(
                    conexion,
                    prestamo_modificado["id_ejemplar"],
                    3
                )

                response["mensaje"] = (
                    "Estado actualizado del prestamo y estado del ejemplar actualizado."
                )

            # Estado vencido
            elif id_estado == 2:

                EjemplarRepository.actualizar_estado(
                    conexion,
                    prestamo_modificado["id_ejemplar"],
                    4
                )

                response["mensaje"] = (
                    "Estado actualizado del prestamo y estado del ejemplar actualizado."
                )

            # Estado finalizado
            elif id_estado == 3:
                EjemplarRepository.actualizar_estado(
                    conexion,
                    prestamo_modificado["id_ejemplar"],
                    1
                )

                response["mensaje"] = (
                    "Estado actualizado del prestamo y estado del ejemplar actualizado."
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

        except Exception:
            if own_connection:
                conexion.rollback()

            raise

        finally:
            if own_connection:
                conexion.close()