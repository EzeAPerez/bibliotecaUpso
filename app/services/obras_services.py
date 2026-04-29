from repositories.obras_repo import ObraRepository
from models.obras import ObraCreate, ObraUpdate, Obras, ObraDetallada

class ObraService:
    
    @staticmethod
    def procesar_obras(rows):
        """Procesa y estructura las obras"""
        obras = {}
        for r in rows:
            obra_id = r["id"]
            if obra_id not in obras:
                obras[obra_id] = {**r, "areas": []}
                obras[obra_id].pop("area_id", None)
                obras[obra_id].pop("area_nombre", None)
                obras[obra_id].pop("subarea_id", None)
                obras[obra_id].pop("subarea_nombre", None)
            
            if r.get("area_id"):
                area = next((a for a in obras[obra_id]["areas"] if a["id"] == r["area_id"]), None)
                if not area:
                    area = {"id": r["area_id"], "nombre": r["area_nombre"], "subareas": []}
                    obras[obra_id]["areas"].append(area)
                
                if r.get("subarea_id"):
                    area["subareas"].append({"id": r["subarea_id"], "nombre": r["subarea_nombre"]})
        
        return list(obras.values())

    @staticmethod
    def obtener_todas(page=1, limit=10):
        rows = ObraRepository.obtener_base(page=page, limit=limit)
        return ObraService.procesar_obras(rows)
    
    @staticmethod
    def obtener_por_estado(id_estado: int, page=1, limit=10):
        rows = ObraRepository.obtener_base(
            where_clauses=["o.id_estado = %s"],
            params=[id_estado],
            page=page, limit=limit
        )
        return ObraService.procesar_obras(rows)

    @staticmethod
    def obtener_por_tipo(id_tipo: int, page=1, limit=10):
        rows = ObraRepository.obtener_base(
            where_clauses=[
                "o.id_tipo_material = %s"
            ],
            params=[id_tipo],
            page=page,
            limit=limit
        )
        return ObraService.procesar_obras(rows)
    
    @staticmethod
    def obtener_por_id(id : int):
        rows = ObraRepository.obtener_base(
            where_clauses=[
                "o.id = %s"
            ],
            params=[id]
        )
        if rows:
            return ObraService.procesar_obras(rows)[0]
        else: 
            None
       
    @staticmethod
    def obtener_por_codigo(codigo : str):
        rows = ObraRepository.obtener_base(
            where_clauses=[
                "o.codigo_fisico = %s"
            ],
            params=[codigo]
        )
        if rows:
            return ObraService.procesar_obras(rows)[0]
        else:
            return None
        
    @staticmethod
    def obtener_por_busqueda(q: str, page=1, limit=10):
        like = f"%{q}%"
        rows = ObraRepository.obtener_base(
            where_clauses=[
                "(o.titulo LIKE %s OR o.subtitulo LIKE %s OR o.autor LIKE %s OR at.nombre LIKE %s OR st.nombre LIKE %s)",
            ],
            params=[like, like, like, like, like],
            page=page,
            limit=limit
        )

        return ObraService.procesar_obras(rows)

    @staticmethod
    def obtener_por_area_tematica(id_area: int, page:int, limit:int):
        rows = ObraRepository.obtener_base(
            where_clauses=[
                "at.id = %s"
            ],
            params=[id_area],
            page=page,
            limit=limit
        )

        return ObraService.procesar_obras(rows)
    
    @staticmethod
    def obtener_por_sub_area_tematica(id_subarea:int, page:int, limit:int):
        rows = ObraRepository.obtener_base(
            where_clauses=[
                "st.id = %s"
            ],
            params=[id_subarea],
            page=page,
            limit=limit
        )

        return ObraService.procesar_obras(rows)
    
    @staticmethod
    def obtener_por_sede(id_sede:int, page:int, limit:int):
        rows = ObraRepository.obtener_base(
            where_clauses=[
                "o.id_sede = %s"
            ],
            params=[id_sede],
            page=page,
            limit=limit
        )

        return ObraService.procesar_obras(rows)

    @staticmethod
    def contar_obras():
        return ObraRepository.contar()

    @staticmethod
    def contar_por_tipo(id_tipo):
        return ObraRepository.contar(
            ["o.id_tipo_material = %s"],
            [id_tipo]
        )

    @staticmethod
    def contar_por_estado(id_estado):
        return ObraRepository.contar(
            ["o.id_estado = %s"],
            [id_estado]
        )

    @staticmethod
    def contar_por_sede(id_sede):
        return ObraRepository.contar(
            ["o.id_sede = %s"],
            [id_sede]
        )

    @staticmethod
    def contar_por_subarea(id_subarea):
        return ObraRepository.contar(
            ["ost.id_subarea = %s"],
            [id_subarea]
        )

    @staticmethod
    def contar_por_area(id_area):
        return ObraRepository.contar(
            ["st.id_area_tematica = %s"],
            [id_area]
        )

    @staticmethod
    def contar_por_busqueda(q):
        like = f"%{q}%"
        return ObraRepository.contar(
            [
                "(o.titulo LIKE %s OR o.autor LIKE %s OR o.codigo_fisico LIKE %s OR o.subtitulo LIKE %s OR at.nombre LIKE %s OR st.nombre LIKE %s)"
            ],
            [like, like, like, like, like, like]
        )