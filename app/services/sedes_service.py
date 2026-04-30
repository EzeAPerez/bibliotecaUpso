from repositories.sedes_repo import SedesRepository

class SedesService:

    @staticmethod
    def obtener_por_id(id : int):
        rows = SedesRepository.obtener(
            where_clauses=[
                "id = %s"
            ],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None
    
    @staticmethod
    def obtener_por_buscar(q:str):
        like = f"%{q}%"
        rows = SedesRepository.obtener(
            where_clauses=[
                "nombre LIKE %s"
            ],
            params=[like]
        )
        return rows