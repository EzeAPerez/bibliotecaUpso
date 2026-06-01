from db.database import get_connection
from mysql.connector import IntegrityError
from repositories.renovaciones_repo import RenovacionesRepository
from repositories.prestamos_repo import PrestamosRepository
from repositories.restricciones_repo import RestriccionesRepository
from services.prestamos_service import PrestamosService
class RenovacionesService:

    @staticmethod
    def restricciones(id_user, id_prestamo, conexion):
        cant_prestamos_vencidos = PrestamosRepository.prestamos_vencidos(
            conexion,
            id_user
        )
        cant_renovaciones = RenovacionesRepository.contar(
            where_clauses=["id_prestamo = %s"],
            params=[id_prestamo]
            )
        
        restricciones = RestriccionesRepository.obtener()[0]
        print(cant_prestamos_vencidos, cant_renovaciones)

        if (cant_prestamos_vencidos > 0) or (cant_renovaciones >= restricciones["cantidad_renovaciones"]):
            return False
        else: 
            return True

    @staticmethod
    def crear(prestamos_data):
        conexion = get_connection()
        conexion.autocommit = False

        try: 
            prestamo = PrestamosService.obtener_por_id(prestamos_data["id_prestamo"])
            if not prestamo or (prestamo["id_estado"] != 1 ):
                raise ValueError(
                    "Prestamo no encontrado, o prestamo FINALIZADO / VENCIDO"
                )
            
            restriccion = RenovacionesService.restricciones(prestamo["id_user"], prestamos_data["id_prestamo"], conexion)
            if not restriccion:
                raise ValueError(
                    "No cumple con las restricciones"
                ) 
            
            renovacion = RenovacionesRepository.crear_automatico(prestamo, conexion)
            
            PrestamosRepository.actualizar_vencimiento(prestamos_data["id_prestamo"], renovacion["fecha_vencimiento_nueva"], conexion)
            conexion.commit()            
            return {"mensaje": "Se realizo la renovacion del prestamo, se actualizo la fecha de vencimiento del prestamo."}
        
        except Exception:
            conexion.rollback()

            raise
        finally:
            conexion.close() 


    @staticmethod
    def obtener(page=1, limit=10):
        rows = RenovacionesRepository.obtener(page=page, limit=limit)

        total = RenovacionesRepository.contar()

        return {"items": rows, "total": total}

    @staticmethod
    def obtener_por_id(id: int):
        rows = RenovacionesRepository.obtener(
            where_clauses=["id = %s"],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None
    
    @staticmethod
    def obtener_por_user(id_user: int, page=1, limit=10):
        rows = RenovacionesRepository.obtener(
            where_clauses=[
                "id_user = %s"
            ],
            params=[id_user],
            page=page,
            limit=limit
        )

        return rows