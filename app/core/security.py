from fastapi import Depends, HTTPException, Request, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Dict, Any
import datetime
from typing import Dict, Any
from jose import JWTError, jwt
from core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from repositories.auth_repo import AuthRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_jwt_token(data: Dict[str, Any], expires_delta: datetime.timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_real_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    return request.client.host


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
        session_data = AuthRepository.get_session_data(jti)
        
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

async def get_current_user_from_refresh_token_cookie(
    request: Request, # <--- Necesitamos el Request para ver la IP actual
    refresh_token: str = Cookie(None)
) -> Dict[str, Any]:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión inválida o expirada.",
    )
    
    if not refresh_token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        jti: str = payload.get("jti")
        token_type: str = payload.get("token_type")

        if jti is None or token_type != "refresh":
            raise credentials_exception
        
        # 1. Buscamos la sesión en la BD
        session_data = AuthRepository.get_session_data(jti)
        if session_data is None:
            raise credentials_exception
        
        # 2. VALIDACIÓN DE IP (Anti-Robo de Cookie)
        current_ip = get_real_client_ip(request)
        stored_ip = session_data['ip_address']

        # Si las IPs no coinciden, asumimos robo de sesión
        if current_ip != stored_ip:
            print(f"ALERTA SEGURIDAD: Intento de uso de cookie robada. IP Original: {stored_ip}, IP Actual: {current_ip}")
            # Opcional: Podrías invalidar el token aquí para matar la sesión robada
            AuthRepository.clear_user_session_token(jti)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Cambio de IP detectado. Por seguridad, inicia sesión nuevamente."
            )

        return session_data

    except JWTError:
        raise credentials_exception
    
class RoleChecker:

    def __init__(self, roles: list[int]):
        self.roles = roles

    def __call__(self, user: Dict[str, Any] = Depends(get_current_active_user)):
        if user["id_rol"] not in self.roles:
            print(f"ALERTA: Usuario {user['nombre']} (Rol {user['id_rol']}) intentó acceder a ruta protegida.")
            raise HTTPException(403, "No tienes permisos suficientes para realizar esta acción.")
        return user

allow_super_admin = RoleChecker([1])
allow_any_admin = RoleChecker([1, 2])
allow_students = RoleChecker([3])
allow_everyone = RoleChecker([1, 2, 3])
