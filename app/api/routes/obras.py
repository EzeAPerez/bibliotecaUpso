from errno import errorcode

from fastapi import APIRouter, HTTPException, Depends, status
from models.obras import ObraCreate, ObraUpdate, Obras, ObraDetallada
from db.database import get_connection 
from typing import List
from mysql.connector import IntegrityError, errorcode

from core.security import (
    allow_everyone,
    allow_super_admin
)

def obtener_obras_base(where_clauses=[], params=[], page=1, limit=10):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    offset = (page - 1) * limit

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    query = f"""
    SELECT 
        o.id,
        o.codigo_fisico,
        o.id_tipo_material,
        tm.tipo AS tipo_material,
        o.titulo,
        o.subtitulo,
        o.formato,
        o.anio,
        o.autor,
        o.ubicacion_fisica,
        o.anio_ingreso,
        o.tipo_de_ingreso,
        o.id_sede,
        s.nombre AS nombre_sede,
        o.id_estado,

        o.isbn,
        o.edicion,
        o.tomo,
        o.editorial,

        o.issn,
        o.volumen,
        o.numero,

        o.institucion,
        o.nivel_academico,

        at.id AS area_id,
        at.nombre AS area_nombre,
        st.id AS subarea_id,
        st.nombre AS subarea_nombre

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

    cursor.execute(query, (*params, limit, offset))
    rows = cursor.fetchall()

    cursor.close()
    conexion.close()

    return rows

def procesar_obras(rows):

    obras = {}

    for r in rows:

        obra_id = r["id"]

        if obra_id not in obras:
            obras[obra_id] = {**r, "areas": []}

            obras[obra_id].pop("area_id")
            obras[obra_id].pop("area_nombre")
            obras[obra_id].pop("subarea_id")
            obras[obra_id].pop("subarea_nombre")

        if r["area_id"]:

            area = next(
                (a for a in obras[obra_id]["areas"] if a["id"] == r["area_id"]),
                None
            )

            if not area:
                area = {
                    "id": r["area_id"],
                    "nombre": r["area_nombre"],
                    "subareas": []
                }
                obras[obra_id]["areas"].append(area)

            if r["subarea_id"]:
                area["subareas"].append({
                    "id": r["subarea_id"],
                    "nombre": r["subarea_nombre"]
                })

    return list(obras.values())

router = APIRouter(
    prefix="/obras",
    tags=["obras"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=int,
    summary="Crear obra",
    description="Crear una nueva obra en la base de datos. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def crear_obra(
    obra: ObraCreate,
    user = Depends(allow_super_admin)
):

    nueva_obra = Obras.model_validate(obra)
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

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
            nueva_obra.codigo_fisico,
            nueva_obra.id_tipo_material,
            nueva_obra.titulo,
            nueva_obra.subtitulo,
            nueva_obra.formato,
            nueva_obra.anio,
            nueva_obra.autor,
            nueva_obra.ubicacion_fisica,
            nueva_obra.anio_ingreso,
            nueva_obra.tipo_de_ingreso,
            nueva_obra.id_sede,
            nueva_obra.id_estado,
            nueva_obra.isbn,
            nueva_obra.edicion,
            nueva_obra.tomo,
            nueva_obra.editorial,
            nueva_obra.issn,
            nueva_obra.volumen,
            nueva_obra.numero,
            nueva_obra.institucion,
            nueva_obra.nivel_academico
        ))

        id_obra = cursor.lastrowid

        if obra.subareas:
            for id_subarea in obra.subareas:
                cursor.execute("""
                    INSERT INTO obra_subarea_tematica (id_obra, id_subarea)
                    VALUES (%s, %s)
                """, (id_obra, id_subarea))

        conexion.commit()

        return id_obra

    except IntegrityError as e:
        conexion.rollback()

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un libro con el codigo: {nueva_obra.codigo_fisico}"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

    finally:
        cursor.close()
        conexion.close()


@router.patch(
    "/{id}", 
    status_code=status.HTTP_200_OK,
    response_model=Obras,
    summary="Modificar obra",
    description="Modificar el contenido de una obra con id pasado por parametro. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
    )
def modificar_obras(
    id: int,
    obra_update: ObraUpdate,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()
    
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM obras WHERE id = %s", (id,))
    obra = cursor.fetchone()

    if not obra:
        cursor.close()
        conexion.close()
        raise HTTPException(status_code=404, detail="Obra no encontrada")

    try:

        campos = []
        valores = []

        data = obra_update.model_dump(exclude_unset=True)

        for campo, valor in data.items():
            campos.append(f"{campo} = %s")
            valores.append(valor)

        if not campos:
            raise HTTPException(
                status_code=400,
                detail="No se enviaron campos para actualizar"
            )

        sql = f"""
            UPDATE obras
            SET {', '.join(campos)}
            WHERE id = %s
        """

        valores.append(id)

        cursor.execute(sql, valores)
        conexion.commit()

        cursor.execute("SELECT * FROM obras WHERE id = %s", (id,))
        obra_actualizada = cursor.fetchone()

        return obra_actualizada
    
    except IntegrityError as e:

        conexion.rollback()

        if e.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una obra con el codigo: {obra_update.codigo_fisico}"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {e.msg}"
        )

    finally:
        cursor.close()
        conexion.close() 

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar obra",
    description="Eliminar una obra específica de la base de datos por su ID. Solo accesible para SuperAdmin.",
    tags=[router.tags[0]]
)
def eliminar_obras(
    id: int,
    user = Depends(allow_super_admin)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM obra_subarea_tematica WHERE id_obra = %s", (id,))
        conexion.commit()
        
        cursor.execute("DELETE FROM obras WHERE id = %s", (id,))
        conexion.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Obra no encontrada")

        cursor.close()
        conexion.close()

        return None

    except IntegrityError as e:
        conexion.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos."
        )

@router.get(
    "", 
    response_model=list[ObraDetallada],
    tags=[router.tags[0]],
    summary="Obtener obras detallada",
    description="Obtener todas las obras con detalles de las subareas y areas. Accesible para todos los usuarios."
)
def get_obras(
    page: int = 1, 
    limit: int = 10,
    user = Depends(allow_everyone)
    ):

    rows = obtener_obras_base(page=page, limit=limit)

    return procesar_obras(rows)

@router.get(
    "/estado/{id_estado}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por estado",
    description="Obtener todas las obras de un estado de la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_estado(
    id_estado: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
    ):
    rows = obtener_obras_base(
        where_clauses=[
            "o.id_estado = %s"
        ],
        params=[id_estado],
        page=page,
        limit=limit
    )

    return procesar_obras(rows)

@router.get(
    "/tipo/{id_tipo}",
    status_code=status.HTTP_200_OK,
    response_model=List[ObraDetallada],
    summary="Obtener obras por tipo",
    description="Obtener todas las obras de un tipo la base de datos, con limite y numero de pagina. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_tipo(
    id_tipo: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    rows = obtener_obras_base(
        where_clauses=[
            "o.id_tipo_material = %s"
        ],
        params=[id_tipo],
        page=page,
        limit=limit
    )

    return procesar_obras(rows)

@router.get(
    "/{id}",
    response_model=ObraDetallada,
    summary="Obtener una obra por ID",
    description="Obtener una obra específica de la base de datos por su ID. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_id(
    id: int,
    user = Depends(allow_everyone)
):
    rows = obtener_obras_base(
        where_clauses=[
            "o.id = %s"
        ],
        params=[id]
    )
    if rows:
        return procesar_obras(rows)[0]
    else:
        raise HTTPException(status_code=404, detail="Obra no encontrada")

@router.get(
    "/codigo/{codigo:path}",
    response_model=ObraDetallada,
    summary="Obtener una obra por código",
    description="Obtener una obra específica de la base de datos por su código. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_codigo(
    codigo: str,
    user = Depends(allow_everyone)
):
    rows = obtener_obras_base(
        where_clauses=[
            "o.codigo_fisico = %s"
        ],
        params=[codigo]
    )
    if rows:
        return procesar_obras(rows)[0]
    else:
        raise HTTPException(status_code=404, detail="Obra no encontrada")

@router.get(
    "/buscar/",
    response_model=List[ObraDetallada],
    summary="Buscar una obra especifica.",
    description="Buscar y obtener obras a partir del filtro de busqueda. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_buscar(
    q: str,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    like = f"%{q}%"
    rows = obtener_obras_base(
        where_clauses=[
            "(o.titulo LIKE %s OR o.subtitulo LIKE %s OR o.autor LIKE %s OR at.nombre LIKE %s OR st.nombre LIKE %s)",
        ],
        params=[like, like, like, like, like],
        page=page,
        limit=limit
    )

    return procesar_obras(
        rows
    )


@router.get(
    "/area_tematica/{id_area}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por area tematica",
    description="Obtener todas las obras almacenadas en la base de datos de un area tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_area_tematica(
    id_area: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    rows = obtener_obras_base(
        where_clauses=[
            "at.id = %s"
        ],
        params=[id_area],
        page=page,
        limit=limit
    )

    return procesar_obras(
        rows
    )


@router.get(
    "/subarea_tematica/{id_subarea}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por subarea tematica",
    description="Obtener todas las obras almacenadas en la base de datos de un subarea tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_sub_area_tematica(
    id_subarea: int,
    page: int = 1,
    limit: int = 10,
    user = Depends(allow_everyone)
):
    rows = obtener_obras_base(
        where_clauses=[
            "st.id = %s"
        ],
        params=[id_subarea],
        page=page,
        limit=limit
    )

    return procesar_obras(
        rows
    )

@router.get(
    "/sede/{id_sede}",
    response_model=List[ObraDetallada],
    summary="Obtener obras por sede",
    description="Obtener todas las obras almacenadas en la base de datos de una sede expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_obras_sede(
    id_sede: int,
    page: int = 1,
    limit: int =10,
    user = Depends(allow_everyone)
):
    rows = obtener_obras_base(
        where_clauses=[
            "o.id_sede = %s"
        ],
        params=[id_sede],
        page=page,
        limit=limit
    )

    return procesar_obras(
        rows
    )

@router.get(
    "/cantidad",
    response_model=int,
    summary="Obtener la cantidad de obras",
    description="Obtener la cantidad de obras almacenadas en la base de datos. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cant_obras(
    user = Depends(allow_everyone)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) FROM obras")
    
    count = cursor.fetchone()
    
    cursor.close()
    conexion.close()

    return count['COUNT(*)']

@router.get(
    "/buscar/cantidad",
    response_model=int,
    summary="Cantidad de obras segun filtro de busqueda",
    description="Obtener la cantidad de obras almacenadas en la base de datos segun el filtro de busqueda. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cantidad_obras_buscar(
    q: str,
    user = Depends(allow_everyone)
):
    conexion = get_connection()

    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor()

    query = """
        SELECT COUNT(DISTINCT o.id)
        FROM obras o
        JOIN sedes s ON o.id_sede = s.id
        LEFT JOIN obra_subarea_tematica ost ON o.id = ost.id_obra
        LEFT JOIN subarea_tematica st ON ost.id_subarea = st.id
        LEFT JOIN area_tematica at ON st.id_area_tematica = at.id
        WHERE 
            o.titulo LIKE %s 
            OR o.autor LIKE %s 
            OR o.codigo_fisico LIKE %s 
            OR o.subtitulo LIKE %s 
            OR at.nombre LIKE %s 
            OR st.nombre LIKE %s
    """

    params = (f"%{q}%",) * 6
    cursor.execute(query, params)

    total = cursor.fetchone()[0]

    cursor.close()
    conexion.close()

    return total

@router.get(
    "/tipo/{id_tipo}/cantidad",
    response_model=int,
    summary="Obtener la cantidad de obras de un tipo",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un tipo expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cant_obras_tipo(
    id_tipo: int,
    user = Depends(allow_everyone)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexcion")

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) FROM obras WHERE id_tipo_material=%s", (id_tipo,))

    count = cursor.fetchone()

    cursor.close()
    conexion.close()

    return count['COUNT(*)']


@router.get(
    "/estado/{id_estado}/cantidad",
    response_model=int,
    summary="Obtener la cantidad de obras de un estado",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un estado expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cant_obras_tipo(
    id_estado: int,
    user = Depends(allow_everyone)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexcion")

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) FROM obras WHERE id_estado=%s", (id_estado,))

    count = cursor.fetchone()

    cursor.close()
    conexion.close()

    return count['COUNT(*)']


@router.get(
    "/area_tematica/{id_area}/cantidad",
    response_model=int,
    summary="Cantidad de obras por area tematica",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un area tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cantidad_obras_area_tematica(
    id_area: int,
    user = Depends(allow_everyone)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor()

    query = """
         SELECT COUNT(DISTINCT o.id)
        FROM obras o
        JOIN obra_subarea_tematica ost ON o.id = ost.id_obra
        WHERE ost.id_subarea = %s
    """

    cursor.execute(query, (id_area,))
    total = cursor.fetchone()[0]

    cursor.close()
    conexion.close()

    return total

@router.get(
    "/sub_area_tematica/{id_subarea}/cantidad",
    response_model=int,
    summary="Cantidad de obras por subarea tematica",
    description="Obtener la cantidad de obras almacenadas en la base de datos de un subarea tematica expecifico. Accesible para todos los usuarios.",
    tags=[router.tags[0]]
)
def get_cantidad_obras_sub_area_tematica(
    id_subarea: int,
    user = Depends(allow_everyone)
):
    conexion = get_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor()

    query = """
        SELECT COUNT(DISTINCT o.id)
        FROM obras o
        JOIN obra_subarea_tematica ost ON o.id = ost.id_obra
        JOIN subarea_tematica st ON ost.id_subarea = st.id
        WHERE st.id_area_tematica = %s
    """

    cursor.execute(query, (id_subarea,))
    total = cursor.fetchone()[0]

    cursor.close()
    conexion.close()

    return total