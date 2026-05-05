from repositories.area_tematica_repo import AreaTematicaRepository

class AreaTematicaService:

    def __init__(self, repository: AreaTematicaRepository):
        self.repository = repository

    def obtener_por_id(self, id: int):
        rows = self.repository.obtener(
            where_clauses=["id = %s"],
            params=[id]
        )
        return rows[0] if rows else None