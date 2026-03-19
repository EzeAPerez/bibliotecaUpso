from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

"""
Pruebas para el endpoint POST /obras_subarea:
1. test_crear_obras_subareas: Verifica que se pueda crear una nueva realcaion entre un obra subarea con datos válidos.
2. test_crear_obras_subareas_repetida: Verifica que no se pueda crear una nueva relacion obra subarea con datos que ya existen.
"""

def test_crear_obras_subareas(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre":"Area Tematica Test"},
        headers= auth_headers
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
            "subareas": []
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.post(
        f"/obras_subareas",
        json={"id_obra": id_obra, "id_subarea":id_subarea},
        headers=auth_headers
    )
    assert response.status_code ==201

    response = client.get(
        "/obras_subareas",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(
        obras_subareas["id_obra"] == id_obra and obras_subareas["id_subarea"] == id_subarea
        for obras_subareas in data
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

def test_crear_sede_repetida(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre":"Area Tematica Test"},
        headers= auth_headers
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
            "subareas": []
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.post(
        f"/obras_subareas",
        json={"id_obra": id_obra, "id_subarea":id_subarea},
        headers=auth_headers
    )
    assert response.status_code ==201

    response = client.post(
        f"/obras_subareas",
        json={"id_obra": id_obra, "id_subarea":id_subarea},
        headers=auth_headers
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "La obra ya tiene asignada esa subárea temática"

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


"""
Pruebas para el endpoint PATCH /obras_subareas:
1. test_modificar_obra_subarea: Verifica que se pueda modificar una realcion entre una obra y un subarea existente.
2. test_modificar_obra_subarea_no_existente: Verifica que no se pueda modificar una relacion entre una obra y un subarea que no existe.
3. test_modificar_obra_subarea_repetida: Verifica que no se pueda modificar una relacion entre una obra y un subarea con datos que ya existen.
"""
def test_modificar_obra_subarea(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre":"Area Tematica Test"},
        headers= auth_headers
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
        json={"nombre": "Subarea Tematica Nueva Test", "id_area_tematica": id_area},
        headers=auth_headers 
    )
    assert response.status_code == 201
    id_subarea_nueva = response.json()

    response = client.post(
        "/obras",
        json={
            "id_tipo_material": 1,
            "codigo_fisico": "codigo_test",
            "titulo": "Obra Test",
            "id_sede": 1,
            "id_estado": 1,
            "subareas": []
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.post(
        f"/obras_subareas",
        json={"id_obra": id_obra, "id_subarea":id_subarea},
        headers=auth_headers
    )
    assert response.status_code ==201

    response = client.patch(
        f"/obras_subareas",
        json={
            "id_obra": id_obra,
            "id_subarea": id_subarea,
            "id_subarea_nueva": id_subarea_nueva
        },
        headers=auth_headers 
    )
    assert response.status_code == 200

    response = client.get(
        "/obras_subareas",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(obra_subarea["id_obra"] == id_obra and obra_subarea["id_subarea"] == id_subarea_nueva for obra_subarea in data)

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
        f"/subarea_tematica/{id_subarea_nueva}",
        headers=auth_headers  
    )
    assert response.status_code == 204

    response = client.delete(
        f"/area_tematica/{id_area}",
        headers=auth_headers  
    )
    assert response.status_code == 204

def test_modificar_obra_subarea_no_existente(auth_headers):
    response = client.patch(
        f"/obras_subareas",
        json={
            "id_obra": 999,
            "id_subarea": 999,
            "id_subarea_nueva": 999
        },
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "La ralacion obra subarea tematica no existe"

def test_modificar_obra_subarea_repetida(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre":"Area Tematica Test"},
        headers= auth_headers
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
        json={"nombre": "Subarea Tematica Nueva Test", "id_area_tematica": id_area},
        headers=auth_headers 
    )
    assert response.status_code == 201
    id_subarea_nueva = response.json()

    response = client.post(
        "/obras",
        json={
            "id_tipo_material": 1,
            "codigo_fisico": "codigo_test",
            "titulo": "Obra Test",
            "id_sede": 1,
            "id_estado": 1,
            "subareas": []
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.post(
        f"/obras_subareas",
        json={"id_obra": id_obra, "id_subarea":id_subarea},
        headers=auth_headers
    )
    assert response.status_code ==201

    response = client.post(
        f"/obras_subareas",
        json={"id_obra": id_obra, "id_subarea":id_subarea_nueva},
        headers=auth_headers
    )
    assert response.status_code ==201
    

    response = client.patch(
        f"/obras_subareas",
        json={
            "id_obra": id_obra,
            "id_subarea": id_subarea,
            "id_subarea_nueva": id_subarea_nueva
        },
        headers=auth_headers 
    )
    assert response.status_code == 400

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
        f"/subarea_tematica/{id_subarea_nueva}",
        headers=auth_headers  
    )
    assert response.status_code == 204

    response = client.delete(
        f"/area_tematica/{id_area}",
        headers=auth_headers  
    )
    assert response.status_code == 204


"""
Pruebas para el endpoint DELETE /obras_subareas/{id}:
1. test_eliminar_obra_subarea: Verifica que se pueda eliminar una relación obra-subarea existente.
2. test_eliminar_obra_subarea_no_existente: Verifica que no se pueda eliminar una relación obra-subarea que no existe.
"""

def test_eliminar_obra_subarea(auth_headers):
    response = client.post(
        "/area_tematica",
        json={"nombre":"Area Tematica Test"},
        headers= auth_headers
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
            "subareas": []
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    id_obra = response.json()

    response = client.post(
        f"/obras_subareas",
        json={"id_obra": id_obra, "id_subarea": id_subarea},
        headers=auth_headers
    )
    assert response.status_code == 201

    response = client.delete(
        f"/obras_subareas/{id_obra}/{id_subarea}",
        headers=auth_headers
    )
    assert response.status_code == 204

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

def test_eliminar_obra_subarea_no_existente(auth_headers):
    response = client.delete(
        f"/obras_subareas/{999}/{999}",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "La realcion obra subarea tematica no existe"


"""
Pruebas para el endpoint GET /obras_subareas:
1. test_obtener_obra_subarea: Verifica que se puedan obtener todas las relaciones entre obra y subarea.
"""
def test_obtener_sedes(auth_headers):
    response = client.get(
        "/obras_subareas",
        headers=auth_headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
