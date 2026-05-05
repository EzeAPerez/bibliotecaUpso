from db.database import get_connection
from mysql.connector import IntegrityError

class SubAreaRepository:
    
    @staticmethod
    def obtener(where_clauses=[], params=[]):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""


        try:
            cursor.execute(f"SELECT * FROM subarea_tematica {where_sql}", (*params,))
            resultados = cursor.fetchall()

            return resultados
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        
        finally:
            cursor.close()
            conexion.close()
    
    @staticmethod
    def crear(subarea: dict):
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()

        try:
            query = """
            INSERT INTO subarea_tematica (
                nombre,
                id_area_tematica
            )
            VALUES (%s, %s)
            """
        
            cursor.execute(query, (subarea.nombre, subarea.id_area_tematica))

            id_subarea = cursor.lastrowid
            conexion.commit()
            
            return id_subarea

        except IntegrityError as e:
            conexion.rollback()
            raise e
        
        finally:
            cursor.close()
            conexion.close()
    

    @staticmethod
    def modificar(id: int, campos: dict):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try: 
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f" UPDATE subarea_tematica SET {set_clause} WHERE id = %s"

            cursor.execute(sql, (*campos.values(), id))
            conexion.commit()

            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM subarea_tematica WHERE id = %s", (id,))
            
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
            cursor.execute("DELETE FROM subarea_tematica WHERE id = %s", (id,))

            eliminado = cursor.rowcount > 0

            conexion.commit()

            return eliminado
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()