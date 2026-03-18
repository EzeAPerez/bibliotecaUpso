from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

"""
Pruebas para el endpoint POST /subarea_tematica:
1. test_crear_subarea_tematica: Verifica que se pueda crear una nueva subarea tematica con datos válidos.
2. test_crear_subarea_repetida: Verifica que no se pueda crear una subarea tematica con datos que ya existen.
3. test_crear_subarea_area_no_existente: Verifica que no se pueda crear una subarea tematica con un area que no existe.
"""

def test_crear_subarea_tematica(auth_headers):
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

    response = client.get(
        f"/subarea_tematica/{id_subarea}",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Subarea Tematica Test"
    assert data["id_area_tematica"] == id_area

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

def test_crear_subarea_tematica_repetida(auth_headers):
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

    response = client.post(
        "/subarea_tematica",
        json={"nombre": "Subarea Tematica Test", "id_area_tematica": id_area},
        headers=auth_headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == f"Ya existe un subarea tematica con el nombre: Subarea Tematica Test y {id_area}"

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

def test_crear_subarea_area_no_existente(auth_headers):
    response = client.post(
        "/subarea_tematica",
        json={"nombre": "Subarea Tematica Test", "id_area_tematica": 999},
        headers=auth_headers 
    )
    assert response.status_code == 400

"""
Pruebas para el endpoint PATCH /subarea_tematica/{id}:
1. test_modificar_subarea_tematica: Verifica que se pueda modificar una subarea tematica existente con datos válidos.
2. test_modificar_subarea_tematica_no_existente: Verifica que no se pueda modificar una subarea tematica que no existe.
3. test_modificar_subarea_tematica_repetida: Verifica que no se pueda modificar una subarea tematica con un nombre que ya existe.
"""

def test_modificar_subarea_tematica(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre": "Area Tematica Test"},
        headers=auth_headers 
    )
    assert response.status_code == 201
    id_area = response.json()
    
    response = client.post(
        "/subarea_tematica",
        json={"nombre": "Subarea Tematica a modificar", "id_area_tematica": id_area},
        headers=auth_headers 
    )
    assert response.status_code == 201
    id_subarea = response.json()

    response = client.patch(
        f"/subarea_tematica/{id_subarea}",
        json={"nombre": "Subarea Tematica Modificada", "id_area_tematica": id_area},
        headers=auth_headers 
    )
    assert response.status_code == 200
    assert response.json()['nombre'] == "Subarea Tematica Modificada"

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

def test_modificar_subarea_tematica_no_existente(auth_headers):
    response = client.patch(
        f"/subarea_tematica/{999}",
        json={"nombre": "Subarea Tematica Modificada", "id_area_tematica": 1},
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Subarea tematica no encontrada."

def test_modificar_subarea_tematica_repetida(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre": "Area Tematica Test"},
        headers=auth_headers 
    )
    assert response.status_code == 201
    id_area = response.json()

    response = client.post(
        "/subarea_tematica", 
        json={"nombre": "Subarea Tematica Repetida", "id_area_tematica": id_area},
        headers=auth_headers
    )
    assert response.status_code == 201
    id_subarea_1 = response.json()
    
    response = client.post(
        "/subarea_tematica",
        json={"nombre": "Subarea tematica a Modificar", "id_area_tematica": id_area},
        headers=auth_headers 
    )
    
    assert response.status_code == 201
    id_subarea_2 = response.json()
    
    modificado_response = client.patch(
        f"/subarea_tematica/{id_subarea_2}",
        json={"nombre": "Subarea Tematica Repetida", "id_area_tematica": id_area},
        headers=auth_headers 
    )

    assert modificado_response.status_code == 409
    assert modificado_response.json()['detail'] == f"Ya existe un subarea tematica con el nombre: Subarea Tematica Repetida y {id_area}"

    response = client.delete(
        f"/subarea_tematica/{id_subarea_1}",
        headers=auth_headers  
    )
    assert response.status_code == 204

    response = client.delete(
        f"/subarea_tematica/{id_subarea_2}",
        headers=auth_headers  
    )
    assert response.status_code == 204

    response = client.delete(
        f"/area_tematica/{id_area}",
        headers=auth_headers  
    )
    assert response.status_code == 204

"""
Pruebas para el endpoint DELETE /subarea_tematica/{id}:
1. test_eliminar_subarea_tematica: Verifica que se pueda eliminar un subarea tematica existente.
2. test_eliminar_subarea_tematica_no_existente: Verifica que no se pueda eliminar un subarea tematica que no existe.
3. test_eliminar_subarea_tematica_asociada: Verifica que no se pueda eliminar un subarea tematica que está asociada a una obra.
"""

def test_eliminar_subarea_tematica(auth_headers):
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

def test_eliminar_area_tematica_no_existente(auth_headers):
    response = client.delete(
        f"/subarea_tematica/{999999}",
        headers=auth_headers  
    )
    assert response.status_code == 404
    assert response.json()['detail'] == "Subárea temática no encontrada."

def test_eliminar_subarea_tematica_asociada(auth_headers):
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

    response = client.post(
        "/obras",
        json={
            "id_tipo_material": 1,
            "codigo_fisico": "codigo_test",
            "titulo": "Obra Test",
            "id_sede": 1,
            "id_estado": 1,
            "subareas": [id_subarea]
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    obra_id = response.json()

    response = client.delete(
        f"/subarea_tematica/{id_subarea}",
        headers=auth_headers  
    )
    assert response.status_code == 400
    assert response.json()['detail'] == "Error de integridad en la base de datos."

    response = client.delete(
        f"/obras/{obra_id}",
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


"""
Pruebas para el endpoint GET /subarea_tematica:
1. test_obtener_subarea_tematica: Verifica que se puedan obtener todas las subareas tematicas.
"""
def test_obtener_subarea_tematica(auth_headers):
    response = client.get(
        "/subarea_tematica",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


"""
Pruebas para el endpoint GET /subarea_tematica/{id}:
1. test_obtener_subarea_tematica_: Verifica que se pueda obtener un subarea tematica existente por su id.
2. test_obtener_subarea_no_existente: Verifica que no se pueda obtener un subarea tematica que no existe.
"""
def test_obtener_subarea_tematica_id(auth_headers):
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

    response = client.get(
        f"/subarea_tematica/{id_subarea}",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Subarea Tematica Test"

    response = client.delete(
        f"/subarea_tematica/{id_subarea}",
        headers=auth_headers
    )

    response = client.delete(
        f"/area_tematica/{id_area}",
        headers=auth_headers  
    )
    assert response.status_code == 204

def test_obtener_area_tematica_id_no_existente(auth_headers):
    
    response = client.get(
        f"/subarea_tematica/{9999}",
        headers=auth_headers  
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Subárea temática no encontrada."
