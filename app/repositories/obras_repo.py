from db.database import get_connection
from mysql.connector import IntegrityError, errorcode

class ObraRepository:
    
    @staticmethod
    def obtener_base(where_clauses=[], params=[], page=1, limit=10):
        """Consulta base sin procesamiento"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        offset = (page - 1) * limit
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT 
            o.id, o.codigo_fisico, o.id_tipo_material, tm.tipo AS tipo_material,
            o.titulo, o.subtitulo, o.formato, o.anio, o.autor,
            o.ubicacion_fisica, o.anio_ingreso, o.tipo_de_ingreso,
            o.id_sede, s.nombre AS nombre_sede, o.id_estado,
            o.isbn, o.edicion, o.tomo, o.editorial,
            o.issn, o.volumen, o.numero,
            o.institucion, o.nivel_academico,
            at.id AS area_id, at.nombre AS area_nombre,
            st.id AS subarea_id, st.nombre AS subarea_nombre
        FROM obras o
        JOIN sedes s ON o.id_sede = s.id
        JOIN tipo_material tm ON o.id_tipo_material = tm.id
        LEFT JOIN obra_subarea_tematica ost ON o.id = ost.id_obra
        LEFT JOIN subarea_tematica st ON ost.id_subarea = st.id
        LEFT JOIN area_tematica at ON st.id_area_tematica = at.id
        {where_sql}
        ORDER BY o.id DESC
        LIMIT %s OFFSET %s
        """
        
        try:
            cursor.execute(query, (*params, limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()
    
    @staticmethod
    def crear(obra_data: dict, subareas: list):
        """Inserta obra con transacción"""
        conexion = get_connection()
        conexion.autocommit = False
        cursor = conexion.cursor()
        
        try:
            sql = """
                INSERT INTO obras (
                    codigo_fisico, id_tipo_material, titulo, subtitulo,
                    formato, anio, autor, ubicacion_fisica,
                    anio_ingreso, tipo_de_ingreso,
                    id_sede, id_estado, isbn,
                    edicion, tomo, editorial,
                    issn, volumen, numero,
                    institucion, nivel_academico
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

            cursor.execute(sql, (
                obra_data.codigo_fisico,
                obra_data.id_tipo_material,
                obra_data.titulo,
                obra_data.subtitulo,
                obra_data.formato,
                obra_data.anio,
                obra_data.autor,
                obra_data.ubicacion_fisica,
                obra_data.anio_ingreso,
                obra_data.tipo_de_ingreso,
                obra_data.id_sede,
                obra_data.id_estado,
                obra_data.isbn,
                obra_data.edicion,
                obra_data.tomo,
                obra_data.editorial,
                obra_data.issn,
                obra_data.volumen,
                obra_data.numero,
                obra_data.institucion,
                obra_data.nivel_academico
            ))

            id_obra = cursor.lastrowid

            if subareas:
                for id_subarea in subareas:
                    cursor.execute("""
                        INSERT INTO obra_subarea_tematica (id_obra, id_subarea)
                        VALUES (%s, %s)
                    """, (id_obra, id_subarea))

            conexion.commit()

            return id_obra
            
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
            sql = f"UPDATE obras SET {set_clause} WHERE id = %s"
            
            cursor.execute(sql, (*campos.values(), id))
            conexion.commit()

            if cursor.rowcount == 0:
                return None
            
            cursor.execute("SELECT * FROM obras WHERE id = %s", (id,))

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
            cursor.execute("DELETE FROM obra_subarea_tematica WHERE id_obra = %s", (id,))
            cursor.execute("DELETE FROM obras WHERE id = %s", (id,))
            
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
            SELECT COUNT(DISTINCT o.id)
            FROM obras o
            LEFT JOIN obra_subarea_tematica ost ON o.id = ost.id_obra
            LEFT JOIN subarea_tematica st ON ost.id_subarea = st.id
            LEFT JOIN area_tematica at ON st.id_area_tematica = at.id
            {where_sql}
        """

        cursor.execute(query, params)
        total = cursor.fetchone()[0]

        cursor.close()
        conexion.close()

        return total