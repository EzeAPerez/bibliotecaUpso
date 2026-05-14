from repositories.reserva_repo import ReservaRepository

class ReservaService: 

    @staticmethod
    def obtener_por_id(id:int):
        rows = ReservaRepository.obtener(
            where_clauses=["id = %s"],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None
            
### Corregir ###
    @staticmethod
    def obtener_por_busqueda(q: str, page=1, limit=10):
        like = f"%{q}%"
        rows = ReservaRepository.obtener(
            where_clauses=[
                "(o.titulo LIKE %s OR o.subtitulo LIKE %s OR o.autor LIKE %s OR at.nombre LIKE %s OR st.nombre LIKE %s)",
            ],
            params=[like, like, like, like, like],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def obtener_por_sede(id_sede: int, page=1, limit=10):
        rows = ReservaRepository.obtener(
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
        rows = ReservaRepository.obtener(
            where_clauses=[
                "id_user = %s"
            ],
            params=[id_user],
            page=page,
            limit=limit
        )

        return rows
    
    
    @staticmethod
    def obtener_detallada_por_id(id:int):
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "r.id = %s"
            ],
            params=[id]
        )
        if rows:
            return rows[0]
        else: 
            None

    @staticmethod
    def obtener_detallada_por_busqueda(q: str, page=1, limit=10):
        like = f"%{q}%"
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "(o.titulo LIKE %s OR o.subtitulo LIKE %s OR o.autor LIKE %s)",
            ],
            params=[like, like, like],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def obtener_detallada_por_sede(id_sede: int, page=1, limit=10):
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "id_sede = %s"
            ],
            params=[id_sede],
            page=page,
            limit=limit
        )

        return rows
    
    @staticmethod
    def obtener_detallada_por_user(id_user: int, page=1, limit=10):
        rows = ReservaRepository.obtener_detallado(
            where_clauses=[
                "id_user = %s"
            ],
            params=[id_user],
            page=page,
            limit=limit
        )

        return rows
    
    