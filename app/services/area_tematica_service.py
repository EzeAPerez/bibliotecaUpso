from repositories.area_tematica_repo import AreaTematicaRepository

class AreaTematicaService:
    
    @staticmethod 
    def obtener_por_id(id=int):
        rows = AreaTematicaRepository.obtener(
            where_clauses=[
                "id = %s"
            ],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None