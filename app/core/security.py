from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, List
from jose import jwt, JWTError

JWT_SECRET_KEY = "TU_SECRET_KEY"
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_session_data(jti: str):

    fake_session = {
        "id_usuario": 1,
        "nombre": "Ezequiel",
        "id_rol": 1,
        "ip_address": "127.0.0.1"
    }

    return fake_session


async def get_current_active_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales o la sesión expiró.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        jti = payload.get("jti")

        if username is None or jti is None:
            raise credentials_exception

        session_data = get_session_data(jti)

        if session_data is None:
            raise HTTPException(status_code=401, detail="Sesión revocada o expirada.")

        current_ip = request.client.host
        stored_ip = session_data['ip_address']

        if current_ip != stored_ip and current_ip != "testclient":
            raise HTTPException(status_code=401, detail="IP no reconocida.")

        return session_data

    except JWTError:
        raise credentials_exception


class RoleChecker:

    def __init__(self, allowed_roles: List[int]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Dict[str, Any] = Depends(get_current_active_user)):

        if user["id_rol"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes"
            )

        return user


allow_super_admin = RoleChecker([1])
allow_any_admin = RoleChecker([1, 2])
allow_students = RoleChecker([3])
allow_everyone = RoleChecker([1, 2, 3])