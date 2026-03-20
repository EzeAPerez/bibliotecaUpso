from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

"""
Pruebas para el endpoint POST /obras:
1. test_crear_obras: Verifica que se pueda crear una nueva obra con datos válidos.
2. test_crear_obra_repetida: Verifica que no se pueda crear una obra con datos que ya existen.
"""

def test_crear_obra(auth_headers):
    response = client.post(
        "/obras", 
        json={
            "codigo_fisico" : "obra_nueva",
            "titulo" : "titulo nuevo",
            "id_tipo_material" : 1,
            "id_sede" : 1
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        f"/obras/{id_obra}",
        headers=auth_headers
    ) 
    assert response.status_code == 200
    obra = response.json()

    assert obra["codigo_fisico"] == "obra_nueva"
    assert obra["titulo"] == "titulo nuevo"
    assert obra["id_sede"] == 1
    assert obra["id_estado"] == 1

    client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )

def test_crear_obra_repetida(auth_headers):
    response = client.post(
        "/obras", 
        json={
            "codigo_fisico" : "obra_nueva",
            "titulo" : "titulo nuevo",
            "id_tipo_material" : 1,
            "id_sede" : 1
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    id_obra = response.json()

    response = client.post(
        "/obras", 
        json={
            "codigo_fisico" : "obra_nueva",
            "titulo" : "titulo nuevo",
            "id_tipo_material" : 1,
            "id_sede" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un libro con el codigo: obra_nueva"
    
    client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )

"""
Pruebas para el endpoint PATCH /obras/{id}:
1. test_modificar_obras: Verifica que se pueda modificar una obra existente.
2. test_modificar_obras_no_existente: Verifica que no se pueda modificar una obra que no existe.
3. test_modificar_obras_repetida: Verifica que no se pueda modificar una obra con datos que ya existen.
"""

def test_modificar_obras(auth_headers):
    response = client.post(
        "/obras", 
        json={
            "codigo_fisico" : "obra_modificar",
            "titulo" : "titulo a modificar",
            "id_tipo_material" : 1,
            "id_sede" : 1
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    id_obra = response.json()

    assert response.status_code == 201
    id_obra = response.json()

    response = client.patch(
        f"/obras/{id_obra}", 
        json={
            "titulo": "titulo modificado"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["titulo"] == "titulo modificado"

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_modificar_obra_no_existe(auth_headers):
    response = client.patch(
        f"/obras/{9999}", 
        json={
            "titulo": "titulo modificado"
        },
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Obra no encontrada"

def test_modificar_obras_repetida(auth_headers):
    response = client.post(
        "/obras", 
        json={
            "codigo_fisico" : "obra_original",
            "titulo" : "titulo a modificar",
            "id_tipo_material" : 1,
            "id_sede" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra1 = response.json()

    response = client.post(
        "/obras", 
        json={
            "codigo_fisico" : "obra_modificar",
            "titulo" : "titulo a modificar",
            "id_tipo_material" : 1,
            "id_sede" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra2 = response.json()

    response = client.patch(
        f"/obras/{id_obra2}", 
        json={
            "codigo_fisico": "obra_original"
        },
        headers=auth_headers
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe una obra con el codigo: obra_original"

    response = client.delete(
        f"/obras/{id_obra1}",
        headers=auth_headers
    )
    assert response.status_code == 204

    response = client.delete(
        f"/obras/{id_obra2}",
        headers=auth_headers
    )
    assert response.status_code == 204


"""
Pruebas para el endpoint DELETE /obras/{id}:
1. test_eliminar_obras: Verifica que se pueda eliminar una obras existente.
2. test_eliminar_obras_no_existente: Verifica que no se pueda eliminar una obras que no existe.
"""

def test_eliminar_obras(auth_headers):
    response = client.post("/obras", json={
        "codigo_fisico" : "obra_a_eliminar",
        "titulo" : "titulo a eliminar",
        "id_tipo_material" : 1,
        "id_sede" : 1
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    id_obra = response.json()
    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )

    assert response.status_code == 204

def test_eliminar_obras_no_existente(auth_headers):
    response = client.delete(
        f"/obras/9999999",
        headers=auth_headers    
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Obra no encontrada"


"""
Pruebas para el endpoint GET /obras:
1. test_obtener_obras: Verifica que se puedan obtener todas las obras.
"""
def test_obtener_obras(auth_headers):
    response = client.get(
        "/obras",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


"""
Pruebas para el endpoint GET /obras/estados/{id_estado}
1. test_obtener_obras_estados: Verificar que se puedan obtener todas las obras con determinado id estado.
2. test_obtener_obras_estados_no_existente: Verificar que no se obtengan obras con un id estado que no existe.
"""

def test_obtener_obras_estados(auth_headers):
    response = client.post("/obras", json={
        "codigo_fisico" : "obra_a_eliminar",
        "titulo" : "titulo a eliminar",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        "/obras/estado/1",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(obras["id_estado"] == 1 for obras in data)

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204


def test_obtener_obras_estados_no_existente(auth_headers):
    response = client.get(
        "/obras/estado/999",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []


"""
Pruebas para el endpoint GET /obras/tipo/{id_tipo}
1. test_obtener_obras_tipo: Verificar que se puedan obtener todas las obras con determinado id tipo.
2. test_obtener_obras_tipo_no_existente: Verificar que no se obtengan obras con un id tipo que no existe.
"""

def test_obtener_obras_tipo(auth_headers):
    response = client.post("/obras", json={
        "codigo_fisico" : "obra_a_eliminar",
        "titulo" : "titulo a eliminar",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        f"/obras/tipo/{1}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(obras["id_tipo_material"] == 1 for obras in data)

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_obtener_obras_tipo_no_existente(auth_headers):
    response = client.get(
        f"/obras/tipo/{999}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []


"""
Pruebas para el endpoint GET /obras/{id}:
1. test_obtener_obras_id: Verifica que se pueda obtener una obra existente por su id.
2. test_obtener_obras_id_no_existente: Verifica que no se pueda obtener una sede que no existe.
"""
def test_obtener_obras_id(auth_headers):
    response = client.post("/obras", json={
        "codigo_fisico" : "obra_test",
        "titulo" : "titulo test",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["codigo_fisico"] == "obra_test"

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_obtener_obras_id_no_existente(auth_headers):
    response = client.get(
        f"/obras/{99999999}",
        headers=auth_headers  
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Obra no encontrada"

"""
Pruebas para el endpoint GET /obras/codigo/{id}:
1. test_obtener_obras_codigo: Verifica que se pueda obtener una obra existente por su codigo.
2. test_obtener_obras_codigo_no_existente: Verifica que no se pueda obtener una sede que no existe.
"""
def test_obtener_obras_codigo(auth_headers):
    response = client.post("/obras", json={
        "codigo_fisico" : "obra_test",
        "titulo" : "titulo test",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        "/obras/codigo/obra_test",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == id_obra
    assert response.json()["codigo_fisico"] == "obra_test"

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_obtener_obras_codigo_no_existente(auth_headers):
    response = client.get(
        "/obras/codigo/codigo_falso",
        headers=auth_headers  
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Obra no encontrada"


"""
Pruebas para el endpoint GET /obras/buscar/:
1. test_buscar_obras: Verifica que se puedan buscar obras por diferentes campos.
"""
def test_buscar_obras(auth_headers):
    response = client.post("/obras", json={
        "codigo_fisico" : "obra_test",
        "titulo" : "titulo test",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        "/obras/buscar/",
        params={"q": "test"},
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(obras["id"] == id_obra for obras in data)

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers  
    )
    assert response.status_code == 204


"""
Pruebas para el endpoint GET /obras/area_tematica/{id_area}
1. test_obtener_obras_area_tematica: Verificar que se puedan obtener todas las obras con determinado id del area tematica.
2. test_obtener_obras_area_tematica_no_existente: Verificar que no se obtengan obras con un id de area tematica que no existe.
"""

def test_obtener_obras_area_tematica(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre": "Area Tematica Test"},
        headers=auth_headers 
    )
    assert response.status_code == 201
    id_area = response.json()

    response = client.post(
        "/subarea_tematica",
        json={"nombre": "Subarea Tematica Test", "id_area_tematica": id_area},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id_subarea = response.json()

    response = client.post("/obras", json={
        "codigo_fisico" : "obra_a_eliminar",
        "titulo" : "titulo a eliminar",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1,
        "subareas": [id_subarea]
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        f"/obras/area_tematica/{id_area}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(
        any(area["id"] == id_area for area in obra["areas"])
        for obra in data
    )
    
    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204

    response = client.delete(
       f"/subarea_tematica/{id_subarea}",
       headers=auth_headers
    )
    assert response.status_code == 204

    response = client.delete(
        f"/area_tematica/{id_area}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_obtener_obras_area_tematica_no_existente(auth_headers):
    response = client.get(
        "/obras/area_tematica/999",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []

"""
Pruebas para el endpoint GET /obras/subarea_tematica/{id_subarea}
1. test_obtener_obras_subarea_tematica: Verificar que se puedan obtener todas las obras con determinado id del subarea tematica.
2. test_obtener_obras_subarea_tematica_no_existente: Verificar que no se obtengan obras con un id de subarea tematica que no existe.
"""

def test_obtener_obras_subarea_tematica(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre": "Area Tematica Test"},
        headers=auth_headers 
    )
    assert response.status_code == 201
    id_area = response.json()

    response = client.post(
        "/subarea_tematica",
        json={"nombre": "Subarea Tematica Test", "id_area_tematica": id_area},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id_subarea = response.json()

    response = client.post("/obras", json={
        "codigo_fisico" : "obra_a_eliminar",
        "titulo" : "titulo a eliminar",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1,
        "subareas": [id_subarea]
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        f"/obras/subarea_tematica/{id_subarea}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(
    any(
        any(subarea["id"] == id_subarea for subarea in area["subareas"])
        for area in obra["areas"]
        )
        for obra in data
    )

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204

    response = client.delete(
       f"/subarea_tematica/{id_subarea}",
       headers=auth_headers
    )
    assert response.status_code == 204

    response = client.delete(
        f"/area_tematica/{id_area}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_obtener_obras_subarea_tematica_no_existente(auth_headers):
    response = client.get(
        "/obras/subarea_tematica/999",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []

"""
Pruebas para el endpoint GET /obras/sedes/{id_subarea}
1. test_obtener_obras_sedes: Verificar que se puedan obtener todas las obras con determinado id de la sede.
2. test_obtener_obras_sede_no_existente: Verificar que no se obtengan obras con un id de una sede que no existe.
"""

def test_obtener_obras_sedes(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Test"},
        headers=auth_headers
    )
    assert response.status_code == 201
    id_sede = response.json()

    response = client.post("/obras", json={
        "codigo_fisico" : "obra_a_eliminar",
        "titulo" : "titulo a eliminar",
        "id_tipo_material" : 1,
        "id_sede" : id_sede,
        "id_estado" : 1,
        "subareas": []
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        f"/obras/sede/{id_sede}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(obras["id_sede"] == id_sede for obras in data)

    response = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 204

    response = client.delete(
        f"/sedes/{id_sede}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_obtener_obras_sede_no_existente(auth_headers):
    response = client.get(
        "/obras/sede/999",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []

"""
Pruebas para el endpoint GET /obras/cantidad
1. test_obtener_cantidad_obras: Verificar que se puedan obtener la cantidad de todas las obras.
"""

def test_obtener_cantidad_obras(auth_headers):
    response = client.get(
        "/obras",
        headers=auth_headers
    )
    assert response.status_code == 200
    cantidadObras = len(response.json())

    response = client.get(
        "/obras/cantidad/",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == cantidadObras

"""
Pruebas para el endpoint GET /obras/buscar/cantidad
1. test_obtener_cantidad_obras_buscar: Verificar que se puedan obtener la cantidad de todas las obras filtrando con el buscar.
"""
def test_obtener_cantidad_obras_buscar(auth_headers):
    response = client.post("/obras", json={
        "codigo_fisico" : "obra_test",
        "titulo" : "titulo test",
        "id_tipo_material" : 1,
        "id_sede" : 1,
        "id_estado" : 1
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.get(
        "/obras/buscar/",
        params={"q": "test"},
        headers=auth_headers  
    )
    assert response.status_code == 200
    cantidadObras = len(response.json())

    response = client.get(
        "/obras/buscar/cantidad",
        params={"q" : "test"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == cantidadObras

    resposne = client.delete(
        f"/obras/{id_obra}",
        headers=auth_headers
    )
    assert response.status_code == 200


"""
Pruebas para el endpoint GET /obras/tipo/{id_tipo}/cantidad
1. test_obtener_cantidad_obras_tipo: Verificar que se puedan obtener la cantidad de todas las obras filtrando con el tipo de material.
"""

def test_obtener_cantidad_obras_tipo(auth_headers):
    response = client.get(
        f"/obras/tipo/{1}",
        headers=auth_headers
    )
    assert response.status_code == 200
    cantidadObras = len(response.json())

    response = client.get(
        f"/obras/tipo/{1}/cantidad",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == cantidadObras

"""
Pruebas para el endpoint GET /obras/estado/{id_estado}/cantidad
1. test_obtener_cantidad_obras_estado: Verificar que se puedan obtener la cantidad de todas las obras filtrando con el estdo.
"""

def test_obtener_cantidad_obras_estado(auth_headers):
    response = client.get(
        f"/obras/estado/{1}",
        headers=auth_headers
    )
    assert response.status_code == 200
    cantidadObras = len(response.json())

    response = client.get(
        f"/obras/estado/{1}/cantidad",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == cantidadObras


"""
Pruebas para el endpoint GET /obras/area_tematica/{id_area}/cantidad
1. test_obtener_cantidad_obras_area: Verificar que se puedan obtener la cantidad de todas las obras filtrando con el area tematica.
"""

def test_obtener_cantidad_obras_area(auth_headers):
    response = client.get(
        f"/obras/area_tematica/{1}",
        headers=auth_headers
    )
    assert response.status_code == 200
    cantidadObras = len(response.json())

    response = client.get(
        f"/obras/area_tematica/{1}/cantidad",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == cantidadObras


"""
Pruebas para el endpoint GET /obras/subarea_tematica/{id_area}/cantidad
1. test_obtener_cantidad_obras_subarea: Verificar que se puedan obtener la cantidad de todas las obras filtrando con el subarea tematica.
"""

def test_obtener_cantidad_obras_area(auth_headers):
    response = client.get(
        f"/obras/subarea_tematica/{1}",
        headers=auth_headers
    )
    assert response.status_code == 200
    cantidadObras = len(response.json())

    response = client.get(
        f"/obras/subarea_tematica/{1}/cantidad",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == cantidadObras
