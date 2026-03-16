from errno import errorcode

from fastapi import APIRouter, HTTPException, FastAPI, Depends, Request, status
from sqlmodel import Enum
from db.database import get_connection 
from typing import Any, Dict, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from mysql.connector import IntegrityError, errorcode
from jose import jwt, JWTError

router = APIRouter(
    prefix="/login",
    tags=["auth"]
) 

# autorizacion de usuarios
JWT_SECRET_KEY = "TU_SECRET_KEY"
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    if form_data.username != "admin" or form_data.password != "1234":
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    payload = {
        "sub": form_data.username,
        "jti": "123456"
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_session_data(jti: str):
    """
    Busca la sesión en la base de datos por JTI.
    Debe devolver algo como:

    {
        "id_usuario": 1,
        "nombre": "Ezequiel",
        "id_rol": 1,
        "ip_address": "127.0.0.1"
    }
    """

    # EJEMPLO SIMULADO
    # En tu caso esto debería consultar la BD
    fake_session = {
        "id_usuario": 1,
        "nombre": "Ezequiel",
        "id_rol": 3,
        "ip_address": "127.0.0.1"
    }

    return fake_session

async def get_current_active_user(
    request: Request, # Para leer la IP actual
    token: str = Depends(oauth2_scheme) # Para leer el Bearer Token
) -> Dict[str, Any]:
    """
    Esta función protege las rutas. Verifica:
    1. Que el JWT sea válido.
    2. Que la sesión exista en BD (Revocación instantánea).
    3. Que la IP coincida (Anti-Robo de Token).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales o la sesión expiró.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # A. Decodificar JWT
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti") # Necesitamos el JTI del access token

        if username is None or jti is None:
            raise credentials_exception
            
        # B. Consultar la BD (Aquí ocurre la desencriptación interna)
        session_data = get_session_data(jti)
        
        if session_data is None:
            # Si no hay datos, significa que la sesión fue borrada (Logout o Rotación)
            # Aunque el JWT siga "vivo" por fecha, lo rechazamos. ¡Seguridad total!
            raise HTTPException(status_code=401, detail="Sesión revocada o expirada.")

        # C. VALIDACIÓN DE IP (El Check Final)
        current_ip = request.client.host
        stored_ip = session_data['ip_address'] # Ya viene desencriptada por la función

        if current_ip != stored_ip:
            print(f"ALERTA: Token usado desde IP distinta. Original: {stored_ip}, Actual: {current_ip}")
            # Opcional: Podrías borrar la sesión aquí si eres muy estricto
            raise HTTPException(status_code=401, detail="IP no reconocida. Inicia sesión nuevamente.")

        return session_data

    except JWTError:
        raise credentials_exception


class RoleChecker:
    def __init__(self, allowed_roles: List[int]):
        """
        Recibe la lista de IDs de roles permitidos.
        Ej: [1] para solo SuperAdmin, [1, 2] para Admins.
        """
        self.allowed_roles = allowed_roles

    def __call__(self, user: Dict[str, Any] = Depends(get_current_active_user)):
        """
        Esta función se ejecuta cuando llamas a la ruta.
        1. FastAPI ejecuta 'get_current_active_user' (Valida Token, IP, Sesión).
        2. Recibe el usuario validado.
        3. Verifica si el 'id_rol' está en la lista permitida.
        """
        if user["id_rol"] not in self.allowed_roles:
            print(f"ALERTA: Usuario {user['nombre']} (Rol {user['id_rol']}) intentó acceder a ruta protegida.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="No tienes permisos suficientes para realizar esta acción."
            )
        return user

# --- DEFINICIÓN DE PERMISOS REUTILIZABLES ---
# Definimos las "reglas" una sola vez para usarlas en las rutas
allow_super_admin = RoleChecker([1])          # Solo ID 1
allow_any_admin   = RoleChecker([1, 2])       # ID 1 y 2
allow_students    = RoleChecker([3])          # Solo Alumnos
allow_everyone    = RoleChecker([1, 2, 3])    # Todos los roles (1, 2 y 3)


@router.get("/test-auth")
def test(user = Depends(allow_everyone)):
    return {
        "mensaje": "usuario autenticado",
        "user": user
    }

@router.get("/ruta-admin")
def test(user = Depends(allow_any_admin)):
    return {
        "mensaje": "usuario autenticado",
        "user": user
    }