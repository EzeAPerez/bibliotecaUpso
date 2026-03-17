from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


"""
Pruebas para el endpoint POST /sedes:
1. test_crear_sede: Verifica que se pueda crear una nueva sede con datos válidos.
2. test_crear_sede_repetida: Verifica que no se pueda crear una sede con datos que ya existen.
"""

def test_crear_sede():
    # 1. Primero hacés login para obtener el token
    login = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "1234"
        }
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    # 2. Usás el token en el header de cada request
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/sedes",
        json={"nombre": "Sede Test"},
        headers=headers  
    )

    assert response.status_code == 201
    id = response.json()

    response = client.get(
        f"/sedes/{id}",
        headers=headers  
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Sede Test"

    response = client.delete(
        f"/sedes/{id}",
        headers=headers  
    )
    assert response.status_code == 204


def test_obtener_sedes():
    response = client.get("/sedes")
    assert response.status_code == 200


def test_obtener_sede_id():
    response = client.get(f"/sedes/{1}")

    assert response.status_code == 200
    assert response.json()["nombre"] == "Bahia Blanca"
    assert response.json()["direccion"] == "Ciudad de cali 320" 

def test_crear_sede_repetida():
    response = client.post(
        "/sedes",
        json={
            "nombre": "Sede Test",
            "direccion": "Calle Falsa 123"
        }
    )

    assert response.status_code == 409
    assert response.json()['detail'] == "Ya existe una sede con esos datos."

def test_eliminar_sede():
    response = client.post("/sedes", json={
        "nombre": "Sede Delete",
        "direccion": "Test"
    })

    sede_id = response.json()["id"]

    delete_response = client.delete(f"/sedes/{sede_id}")

    assert delete_response.status_code == 204

def test_eliminar_sede_no_existente():
    response = client.delete(f"/sedes/{999999999}")

    assert response.status_code == 404
    assert response.json()['detail']=="Sede no encontrada"

def test_eliminar_sede_con_libros_asociados():
    sede_id = 1

    delete_response = client.delete(f"/sedes/{sede_id}")

    assert delete_response.status_code == 400
    assert delete_response.json()["detail"] == "No se puede eliminar la sede porque tiene libros asociados"

def test_modificar_sede():
    response = client.post("/sedes", json={
        "nombre": "Sede Modificar",
        "direccion": "Test"
    })

    sede_id = response.json()['id']

    modificado_response = client.patch(f"/sedes/{sede_id}",  json={
        "nombre": "Sede modificada 2",
        "direccion": "Direccion modificada"
    })

    sede = modificado_response.json()

    assert modificado_response.status_code == 200
    assert sede["nombre"] == "Sede modificada 2"
    assert sede["direccion"] == "Direccion modificada"

def test_modificar_sede_repetida():
    response = client.post("/sedes", json={
        "nombre": "Sede Modificar Repetida 3",
        "direccion": "Test 3"
    })

    sede_id = response.json()['id']

    modificado_response = client.patch(f"/sedes/{sede_id}",  json={
        "nombre": "Bahia Blanca",
        "direccion": "Ciudad de cali 320"
    }) 

    assert modificado_response.status_code == 409
    assert modificado_response.json()['detail'] == "Ya existe una sede con esos datos."
    client.delete(f"/sedes/{sede_id}")

def test_modificar_sede_no_existente():
    response = client.patch(f"/sedes/{99999999}", json={
        "nombre": "Sede no existente",
        "direccion": "Direccion no existente"
    })

    assert response.status_code == 404
    assert response.json()['detail'] == "Sede no encontrada"
