from repositories.ejemplar_repo import EjemplarRepository 

class EjemplarService:
    
    @staticmethod
    def procesar_ejemplares(rows):

        ejemplares = {}

        for r in rows:

            ejemplar_id = r["id"]

            if ejemplar_id not in ejemplares:

                ejemplares[ejemplar_id] = {
                    "id": r["id"],

                    "codigo_fisico": r["codigo_fisico"],
                    "formato": r["formato"],
                    "ubicacion_fisica": r["ubicacion_fisica"],
                    "anio_ingreso": r["anio_ingreso"],
                    "tipo_de_ingreso": r["tipo_de_ingreso"],

                    "id_sede": r["sede_id"],
                    "nombre_sede": r["sede_nombre"],

                    "id_estado": r["estado_id"],
                    "nombres_estado": r["estado_nombre"],

                    "id_obra": r["id_obra"],

                    "id_tipo_material": r["id_tipo_material"],
                    "tipo_material": r["tipo_material"],

                    "titulo": r["titulo"],
                    "subtitulo": r["subtitulo"],
                    "anio": r["anio"],
                    "autor": r["autor"],

                    "isbn": r["isbn"],
                    "edicion": r["edicion"],
                    "tomo": r["tomo"],
                    "editorial": r["editorial"],

                    "issn": r["issn"],
                    "volumen": r["volumen"],
                    "numero": r["numero"],

                    "institucion": r["institucion"],
                    "nivel_academico": r["nivel_academico"],

                    "areas": []
                }

            if r.get("area_id"):

                area = next(
                    (
                        a for a in ejemplares[ejemplar_id]["areas"]
                        if a["id"] == r["area_id"]
                    ),
                    None
                )

                if not area:

                    area = {
                        "id": r["area_id"],
                        "nombre": r["area_nombre"],
                        "subareas": []
                    }

                    ejemplares[ejemplar_id]["areas"].append(area)

                if r.get("subarea_id"):

                    existe_subarea = next(
                        (
                            s for s in area["subareas"]
                            if s["id"] == r["subarea_id"]
                        ),
                        None
                    )

                    if not existe_subarea:

                        area["subareas"].append({
                            "id": r["subarea_id"],
                            "nombre": r["subarea_nombre"]
                        })

        return list(ejemplares.values())

    @staticmethod
    def obtener_por_id(id : int):
        rows = EjemplarRepository.obtener(
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
    def obtener_por_codigo(codigo : str):
        rows = EjemplarRepository.obtener(
            where_clauses=[
                "codigo_fisico = %s"
            ],
            params=[codigo]
        )
        if rows:
            return rows[0]
        else:
            return None
        
    @staticmethod
    def obtener_por_id_obra(id_obra : int, page: int, limit:int):
        rows = EjemplarRepository.obtener(
            where_clauses=[
                "id_obra = %s"
            ],
            params=[id_obra], 
            page=page,
            limit=limit
        )
        return rows
    
    @staticmethod
    def obtener_por_estado(id_estado : int, page: int, limit:int):
        rows = EjemplarRepository.obtener(
            where_clauses=[
                "id_estado = %s"
            ],
            params=[id_estado], 
            page=page,
            limit=limit
        )
        return rows
    
    @staticmethod
    def obtener_por_id_detallado(id : int):
        rows = EjemplarRepository.obtener_detallado(
            where_clauses=[
                "e.id = %s"
            ],
            params=[id]
        )
        if rows:
            return EjemplarService.procesar_ejemplares(rows)[0]
        else: 
            None
       
    @staticmethod
    def obtener_por_codigo_detallado(codigo : str):
        rows = EjemplarRepository.obtener_detallado(
            where_clauses=[
                "codigo_fisico = %s"
            ],
            params=[codigo]
        )
        if rows:
            return EjemplarService.procesar_ejemplares(rows)[0]
        else:
            return None
        
    @staticmethod
    def obtener_por_id_obra_detallado(id_obra : int, page: int, limit:int):
        rows = EjemplarRepository.obtener_detallado(
            where_clauses=[
                "e.id_obra = %s"
            ],
            params=[id_obra], 
            page=page,
            limit=limit
        )
        return EjemplarService.procesar_ejemplares(rows)
    
    @staticmethod
    def obtener_por_estado_detallado(id_estado : int, page: int, limit:int):
        rows = EjemplarRepository.obtener_detallado(
            where_clauses=[
                "id_estado = %s"
            ],
            params=[id_estado], 
            page=page,
            limit=limit
        )
        return EjemplarService.procesar_ejemplares(rows)