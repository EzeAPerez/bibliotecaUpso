from repositories.subarea_tematica import SubAreaRepository

class SubAreaService:
    
    @staticmethod
    def obtener_por_id(id: int):
        rows = SubAreaRepository.obtener(
            ["id = %s"],
            [id]
        )

        if rows:
            return rows[0]
        else:
            return None
       