from db.database import get_connection
from mysql.connector import IntegrityError

class EjemplarRepository:

    @staticmethod
    def obtener(where_clauses=[], params=[], page=1, limit=10):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        offset = (page - 1) * limit
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
                SELECT * FROM ejemplar 
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
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
                SELECT
                    e.id,
                    e.id_obra,
                    e.codigo_fisico,
                    e.formato,
                    f.nombre AS nombre_formato,
                    e.url,
                    e.tipo_de_ingreso,
                    ti.nombre AS nombre_tipo_ingreso,
                    e.anio_ingreso,
                    e.ubicacion_fisica,

                    s.id AS sede_id,
                    s.nombre AS sede_nombre,

                    ee.id AS estado_id,
                    ee.estado AS estado_nombre,

                    o.id AS obra_id,
                    o.id_tipo_material,

                    tm.tipo AS tipo_material,

                    o.titulo,
                    o.subtitulo,
                    o.anio,
                    o.autor,

                    o.isbn,
                    o.edicion,
                    o.editorial,
                    o.tomo,

                    o.issn,
                    o.volumen,
                    o.numero,

                    o.institucion,
                    o.nivel_academico,
                    na.nombre AS nombre_nivel_academico,

                    at.id AS area_id,
                    at.nombre AS area_nombre,

                    st.id AS subarea_id,
                    st.nombre AS subarea_nombre

                FROM ejemplar e

                JOIN obras o
                    ON e.id_obra = o.id

                LEFT JOIN formato f
                    ON e.formato = f.id
                
                LEFT JOIN tipo_ingreso ti
                    ON e.tipo_de_ingreso = ti.id
                
                JOIN tipo_material tm
                    ON o.id_tipo_material = tm.id

                LEFT JOIN sedes s
                    ON e.id_sede = s.id

                JOIN estado_ejemplar ee
                    ON e.id_estado = ee.id

                LEFT JOIN obra_subarea_tematica ost
                    ON o.id = ost.id_obra

                LEFT JOIN nivel_academico na
                    ON o.nivel_academico = na.id
                LEFT JOIN subarea_tematica st
                    ON ost.id_subarea = st.id

                LEFT JOIN area_tematica at
                    ON st.id_area_tematica = at.id

                {where_sql}

                ORDER BY e.id DESC
                LIMIT %s OFFSET %s
            """
        try:
            cursor.execute(query, (*params, limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(data_ejemplar: dict):
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()

        try:
            sql = """
                INSERT INTO ejemplar(
                    id_obra, codigo_fisico, formato, 
                    url, tipo_de_ingreso, anio_ingreso, id_sede, 
                    ubicacion_fisica, id_estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
            cursor.execute(sql, (
                data_ejemplar.id_obra, 
                data_ejemplar.codigo_fisico, 
                data_ejemplar.formato,
                data_ejemplar.url,
                data_ejemplar.tipo_de_ingreso,
                data_ejemplar.anio_ingreso,
                data_ejemplar.id_sede,
                data_ejemplar.ubicacion_fisica, 
                data_ejemplar.id_estado
            ))

            id_ejemplar = cursor.lastrowid

            conexion.commit()
            
            return id_ejemplar
        
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def actualizar(id: int, campos: dict):
        """Actualiza campos específicos"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        try:
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE ejemplar SET {set_clause} WHERE id = %s"
            
            cursor.execute(sql, (*campos.values(), id))
            conexion.commit()

            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM ejemplar WHERE id = %s", (id,))

            return cursor.fetchone()
            
        except IntegrityError as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def eliminar(id: int):
        """Elimina obra y subareas asociadas"""
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("DELETE FROM ejemplar WHERE id = %s", (id,))
            
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
            FROM ejemplar
            {where_sql}
        """

        cursor.execute(query, params)
        total = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        return total

    @staticmethod
    def bloquear_disponibles(conexion, id_obra):

        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT id, id_sede
            FROM ejemplar
            WHERE id_obra = %s
            AND id_estado = 1
            FOR UPDATE
        """

        cursor.execute(sql, (id_obra,))

        return cursor.fetchall()

    
    @staticmethod
    def actualizar_estado(conexion, id, id_estado):
    
        cursor = conexion.cursor(dictionary=True)
        
        try:
            sql = f"UPDATE ejemplar SET id_estado = %s WHERE id = %s"
            
            cursor.execute(sql, (id_estado, id))

            if cursor.rowcount == 0:
                return None
            
            return cursor.rowcount
            
        except IntegrityError as e:
            raise e

        finally:
            cursor.close()

    