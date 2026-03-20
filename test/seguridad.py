from fastapi.testclient import TestClient
from app.main import app
from jose import jwt

client = TestClient(app)

JWT_SECRET_KEY = "TU_SECRET_KEY"
JWT_ALGORITHM = "HS256"


def crear_token(payload):
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def test_login_correcto():

    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "1234"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_incorrecto():

    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "mal"
        }
    )

    assert response.status_code == 401

def test_acceso_con_token():

    login = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "1234"
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/login/test-auth",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

def test_sin_token():

    response = client.get("/login/test-auth")

    assert response.status_code == 401

def test_token_invalido():

    response = client.get(
        "/login/test-auth",
        headers={
            "Authorization": "Bearer token_falso"
        }
    )

    assert response.status_code == 401

def test_rol_incorrecto():

    login = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "1234"
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/login/ruta-admin",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403

def test_ip_distinta():

    login = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "1234"
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/login/test-auth",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401