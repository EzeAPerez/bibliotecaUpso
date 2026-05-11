import uuid
from fastapi import HTTPException, status
from core.config import *
from core.security import *
from repositories.auth_repo import AuthRepository
from core.crypto import *

class AuthService:

    async def login(self, response, request, username, password, otp_code):

        AuthRepository.clean_expired_sessions()

        user = AuthRepository.get_user_by_username(username)

        if not user or not pwd_context.verify(password, user["password"]):
            raise HTTPException(401, "Credenciales inválidas")

        if user["must_change_password"] == 1:
            raise HTTPException(
                403,
                detail={"action": "CHANGE_PASSWORD_REQUIRED"}
            )

        if user["id_rol"] in [1, 2] and user["is_2fa_enabled"] == 0:
            raise HTTPException(
                403,
                detail={"action": "SETUP_2FA_REQUIRED", "temp_user_id": user["id"]}
            )

        if user["is_2fa_enabled"] == 1:
            if not otp_code:
                raise HTTPException(422, "Código requerido")

            if not verify_totp_code(user["two_factor_secret"], otp_code):
                raise HTTPException(401, "Código inválido")

        if AuthRepository.count_active_sessions(user["id"]) >= 4:
            AuthRepository.delete_oldest_session(user["id"])

        jti = str(uuid.uuid4())

        AuthRepository.create_user_session(
            user["id"],
            jti,
            get_real_client_ip(request),
            request.headers.get("user-agent")
        )

        access_token = create_jwt_token(
            {"sub": user["nombre"], "jti": jti, "token_type": "access"},
            JWT_ACCESS_TOKEN_EXPIRES
        )

        refresh_token = create_jwt_token(
            {"sub": user["nombre"], "jti": jti, "token_type": "refresh"},
            JWT_REFRESH_TOKEN_EXPIRES
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    async def refresh(self, user):
        """
        Genera un nuevo access token a partir del refresh token (cookie).
        """

        # 🔒 IMPORTANTE: mantener el mismo jti (session_token)
        access_token_payload = {
            "sub": user["nombre"],
            "token_type": "access",
            "jti": user["session_token"]
        }

        new_access_token = create_jwt_token(
            access_token_payload,
            JWT_ACCESS_TOKEN_EXPIRES
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": JWT_ACCESS_TOKEN_EXPIRES.total_seconds(),
            "user": {
                "id": user["id"],
                "nombre": user["nombre"],
                "correo": user.get("correo"),
                "role_id": user["id_rol"],
                "2fa_active": bool(user.get("is_2fa_enabled", 0))
            }
        }

    
    async def logout(self, response, refresh_token: str):
        """
        Invalida refresh token y elimina cookie.
        """

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token."
            )

        try:
            payload = jwt.decode(
                refresh_token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM]
            )

            jti = payload.get("jti")

            if not jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de refresco no válido."
                )

            AuthRepository.clear_user_session_token(jti)

            response.delete_cookie("refresh_token")

            return {"detail": "Logout exitoso."}

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado."
            )