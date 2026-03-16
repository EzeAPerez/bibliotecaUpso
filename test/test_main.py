from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_obtener_sedes():
    response = client.get("/sedes")
    assert response.status_code == 200

def test_obtener_sede_id():
    response = client.get(f"/sedes/{1}")

    assert response.status_code == 200
    assert response.json()["nombre"] == "Bahia Blanca"
    assert response.json()["direccion"] == "Ciudad de cali 320" 

def test_crear_sede():
    response = client.post(
        "/sedes",
        json={
            "nombre": "Sede Test",
            "direccion": "Calle Falsa 123"
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert data["nombre"] == "Sede Test"
    assert data["direccion"] == "Calle Falsa 123"
    assert "id" in data

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

def test_crear_libro():
    response = client.post(
        "/libros",
        json={
            "codigo": "LIB12312",
            "titulo": "Libro de Prueba 2",
            "id_sede": 1,
            "id_ubicacion": 1, 
            "id_estado": 1
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert data["codigo"] == "LIB123"
    assert data["titulo"] == "Libro de Prueba"
    assert data["id_sede"] == 1
    assert data["id_ubicacion"] == 1
    assert data["id_estado"] == 1
    assert "id" in data

def test_crear_libro_limite_caracteres():
    # Limite caracteres del atributo 'codigo'
    response1 = client.post(
        "/libros",
        json={
            "codigo": "aAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "titulo": "Libro de Prueba",
            "id_sede": 1,
            "id_ubicacion": 1, 
            "id_estado": 1
        }
    )

    # Limite caracteres del atributo 'titulo'
    response2 = client.post(
        "/libros",
        json={
            "codigo": "a",
            "titulo": "a"*151,
            "id_sede": 1,
            "id_ubicacion": 1, 
            "id_estado": 1
        }
    )
    
    # Limite caracteres del atributo 'isbn'
    response3 = client.post(
        "/libros",
        json={
            "codigo": "a",
            "titulo": "a",
            "isbn": "a"*21,
            "id_sede": 1,
            "id_ubicacion": 1, 
            "id_estado": 1
        }
    )

    assert response1.status_code == 422
    assert response2.status_code == 422
    assert response3.status_code == 422



def test_eliminar_libro():
    response = client.post("/libros", json={
        "codigo": "LIBDELETE",
        "titulo": "Libro a Eliminar",
        "id_sede": 1,
        "id_ubicacion": 1, 
        "id_estado": 1
    })

    libro_id = response.json()["id"]

    delete_response = client.delete(f"/libros/{libro_id}")

    assert delete_response.status_code == 204

def test_eliminar_libro_no_existe():
    delete_response = client.delete("/libros/999999999")

    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Libro no encontrado"


def test_modificar_libro():
    response = client.post("/libros", json={
        "codigo": "LIBMODIFICADO5",
        "titulo": "Libro a Modificar",
        "id_sede": 1,
        "id_ubicacion": 1, 
        "id_estado": 1
    })

    libro_id = response.json()['id']

    modificado_response = client.patch(f"/libros/{libro_id}",  json={
        "titulo": "Titulo modificado"
    })

    libro = modificado_response.json()

    assert modificado_response.status_code == 200
    assert libro["titulo"] == "Titulo modificado"

    client.delete(f"/libros/{libro_id}")

def test_modificar_libro_no_existe():
    modificado_response = client.patch("/libros/999999999",  json={
        "titulo": "Titulo modificado"
    })

    assert modificado_response.status_code == 404
    assert modificado_response.json()["detail"] == "Libro no encontrado"

def test_obtener_libro_id():
    response = client.get("/libros/10")

    assert response.status_code == 200
    assert response.json()["titulo"] == "El Principito"


#----------------- OBRAS ------------------#

## post - /obra
# crear una obra con exito
def test_crear_obra():
    response = client.post("/obra", json={
        "codigo_fisico" : "obra_nueva",
        "titulo" : "titulo nuevo",
        "tipo_material" : "Libro",
        "id_sede" : 1
    })

    assert response.status_code == 201
    data = response.json()

    assert data["codigo_fisico"] == "obra_nueva"
    assert data["titulo"] == "titulo nuevo"
    assert data["id_sede"] == 1
    assert data["id_estado"] == 1
    assert "id" in data

    client.delete(f"/obras/{data["id"]}")

# crear una obra con error - codigo repetido
def test_crear_obra_error():
    response = client.post("/obra", json={
        "codigo_fisico" : "string",
        "titulo" : "titulo nuevo",
        "tipo_material" : "Libro",
        "id_sede" : 1
    })

    assert response.status_code == 409
    assert response.json()['detail'] == "Ya existe un libro con el codigo: string"

## delete - /obras/{id}
# eliminar una obra con exito
def test_eliminar_obra():
    response_crear = client.post("/obra", json={
        "codigo_fisico" : "obra_a_eliminar",
        "titulo" : "titulo a eliminar",
        "tipo_material" : "Libro",
        "id_sede" : 1
    })

    assert response_crear.status_code == 201
    id = response_crear.json()
    print(f"id a eliminar:{id}")
    response = client.delete(f"/obras/{id}")

    assert response.status_code == 204

# eliminar una obra con error - obra no existente
def test_eliminar_obra():
    response = client.delete(f"/obras/9999999")

    assert response.status_code == 404
    assert response.json()['detail'] == "Obra no encontrada"

## patch - /obras/{id}
# modificar obra con exito
def test_modificar_obra():
    response_crear = client.post("/obra", json={
        "codigo_fisico" : "obra_a_modificar",
        "titulo" : "titulo a modificar",
        "tipo_material" : "Libro",
        "id_sede" : 1
    })

    assert response_crear.status_code == 201
    id = response_crear.json()

    print(f"id a modificar:{id}")
    response = client.patch(f"/obras/{id}", json={
        "titulo": "titulo modificado"
    })

    assert response.json()["titulo"] == "titulo modificado"
        
    assert response.status_code == 200

# modificar una obra con error - obra no existente
def test_modificar_obra_no_existe():
    response = client.patch("/obras/16", json={
        "titulo": "titulo modificado"
    })
    print(response.json())
    assert response.status_code == 404
    assert response.json()["detail"] == "Obra no encontrada"

# modificar una obra con error - codifo fisico ya existente
def test_modificar_obra_codigo_existente():
    response = client.patch("/obras/16", json={
        "codigo_fisico": "string"
    })
    print(response.json())
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe una obra con el codigo: string"
