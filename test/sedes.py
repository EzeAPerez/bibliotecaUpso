from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

"""
Pruebas para el endpoint POST /sedes:
1. test_crear_sede: Verifica que se pueda crear una nueva sede con datos válidos.
2. test_crear_sede_repetida: Verifica que no se pueda crear una sede con datos que ya existen.
"""

def test_crear_sede(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Test"},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id = response.json()

    response = client.get(
        f"/sedes/{id}",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Sede Test"

    response = client.delete(
        f"/sedes/{id}",
        headers=auth_headers  
    )
    assert response.status_code == 204

def test_crear_sede_repetida(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Test"},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id = response.json()

    response = client.post(
        "/sedes",
        json={"nombre": "Sede Test"},
        headers=auth_headers 
    )

    assert response.status_code == 409

    response = client.delete(
        f"/sedes/{id}",
        headers=auth_headers  
    )
    assert response.status_code == 204


"""
Pruebas para el endpoint PATCH /sedes/{id}:
1. test_modificar_sede: Verifica que se pueda modificar una sede existente.
2. test_modificar_sede_no_existente: Verifica que no se pueda modificar una sede que no existe.
3. test_modificar_sede_repetida: Verifica que no se pueda modificar una sede con datos que ya existen.
"""
def test_modificar_sede(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Modificar"},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id = response.json()

    modificado_response = client.patch(
        f"/sedes/{id}",
        json={"nombre": "Sede Modificada"},
        headers=auth_headers 
    )

    assert modificado_response.status_code == 200
    data = modificado_response.json()
    assert data["nombre"] == "Sede Modificada"

    response = client.delete(
        f"/sedes/{id}",
        headers=auth_headers  
    )
    assert response.status_code == 204

def test_modificar_sede_no_existente(auth_headers):
    response = client.patch(
        f"/sedes/{99999999}",
        json={"nombre": "Sede No Existente"},
        headers=auth_headers 
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Sede no encontrada."

def test_modificar_sede_repetida(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Modificar Repetida"},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id_sede_1 = response.json()

    response = client.post(
        "/sedes",
        json={"nombre": "Sede a Modificar"},
        headers=auth_headers 
    )
    
    assert response.status_code == 201
    id_sede_2 = response.json()
    
    modificado_response = client.patch(
        f"/sedes/{id_sede_2}",
        json={"nombre": "Sede Modificar Repetida"},
        headers=auth_headers 
    )

    assert modificado_response.status_code == 409
    assert modificado_response.json()['detail'] == "Ya existe una sede con esos datos."

    response = client.delete(
        f"/sedes/{id_sede_1}",
        headers=auth_headers  
    )
    assert response.status_code == 204

    response = client.delete(
        f"/sedes/{id_sede_2}",
        headers=auth_headers  
    )
    assert response.status_code == 204


"""
Pruebas para el endpoint DELETE /sedes/{id}:
1. test_eliminar_sede: Verifica que se pueda eliminar una sede existente.
2. test_eliminar_sede_no_existente: Verifica que no se pueda eliminar una sede que no existe.
3. test_eliminar_sede_con_obras_asociados: Verifica que no se pueda eliminar una sede que tiene obras asociadas.
"""

def test_eliminar_sede(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Eliminar"},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id = response.json()

    response = client.delete(
        f"/sedes/{id}",
        headers=auth_headers  
    )
    assert response.status_code == 204

def test_eliminar_sede_no_existente(auth_headers):
    response = client.delete(
        f"/sedes/{99999999}",
        headers=auth_headers  
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Sede no encontrada"

def test_eliminar_sede_con_obras_asociados(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Eliminar"},
        headers=auth_headers 
    )
    assert response.status_code == 201
    sede_id = response.json()
    
    response = client.post(
        "/obras",
        json={
            "id_tipo_material": 1,
            "codigo_fisico": "codigo_test",
            "titulo": "Obra Test",
            "id_sede": sede_id,
            "id_estado": 1,
            "subareas": [1]
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    obra_id = response.json()

    response = client.delete(
        f"/sedes/{sede_id}",
        headers=auth_headers  
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "No se puede eliminar la sede porque tiene obras asociadas"

    response = client.delete(
        f"/obras/{obra_id}",
        headers=auth_headers  
    )
    assert response.status_code == 204

    response = client.delete(
        f"/sedes/{sede_id}",
        headers=auth_headers  
    )
    assert response.status_code == 204


"""
Pruebas para el endpoint GET /sedes:
1. test_obtener_sedes: Verifica que se puedan obtener todas las sedes.
"""
def test_obtener_sedes(auth_headers):
    response = client.get(
        "/sedes",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

"""
Pruebas para el endpoint GET /sedes/{id}:
1. test_obtener_sede_id: Verifica que se pueda obtener una sede existente por su id.
2. test_obtener_sede_id_no_existente: Verifica que no se pueda obtener una sede que no existe.
"""
def test_obtener_sede_id(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Obtener"},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id = response.json()

    response = client.get(
        f"/sedes/{id}",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Sede Obtener"

    response = client.delete(
        f"/sedes/{id}",
        headers=auth_headers  
    )
    assert response.status_code == 204

def test_obtener_sede_id_no_existente(auth_headers):
    response = client.get(
        f"/sedes/{99999999}",
        headers=auth_headers  
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Sede no encontrada"

"""
Pruebas para el endpoint GET /sedes/buscar/:
1. test_buscar_sedes: Verifica que se puedan buscar sedes por su nombre.
"""
def test_buscar_sedes(auth_headers):
    response = client.post(
        "/sedes",
        json={"nombre": "Sede Buscar"},
        headers=auth_headers 
    )

    assert response.status_code == 201
    id = response.json()

    response = client.get(
        "/sedes/buscar/",
        params={"q": "Buscar"},
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(sede["id"] == id for sede in data)

    response = client.delete(
        f"/sedes/{id}",
        headers=auth_headers  
    )
    assert response.status_code == 204