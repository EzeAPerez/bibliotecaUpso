from fastapi import APIRouter, HTTPException, Depends, Form, Request, status, Cookie, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import Optional
from services.auth_services import AuthService
from repositories.auth_repo import AuthRepository
from services.email_templates import *
from models.auth import *
from core.security import *
from core.roles import *
from core.crypto import *

service = AuthService()

router = APIRouter(
    prefix="",
    tags=["auth"]
)

FRONTEND_BASE_URL = "https://dev/biblioteca"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/login")
async def login(
    response: Response,
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    otp_code: Optional[str] = Form(None)
):
    return await service.login(
        response,
        request,
        form.username,
        form.password,
        otp_code
    )
# --- ENDPOINTS AUXILIARES (Cambio Pass y Setup 2FA) ---

@router.post("/complete-change-password", tags=["Autenticación"])
async def complete_change_password(
    username: str = Form(...),
    old_password: str = Form(...),
    new_password: str = Form(...)
):
    user = AuthRepository.get_user_by_username(username)
    if not user or not pwd_context.verify(old_password, user['password']):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if user['must_change_password'] == 0:
        return {"detail": "No necesitas cambiar la contraseña."}

    # Hash y guardar
    new_hash = pwd_context.hash(new_password)
    AuthRepository.update_password_changed(user['id'], new_hash)
    
    return {"detail": "Contraseña actualizada. Por favor inicia sesión."}

@router.post("/generate-2fa-qr", tags=["Autenticación"])
async def generate_2fa(username: str = Form(...), password: str = Form(...)):

    """Genera el secreto y la URL para el QR"""
    user = AuthRepository.get_user_by_username(username)
    # Validamos pass de nuevo por seguridad
    if not user or not pwd_context.verify(password, user['password']):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Generar secreto
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    # 4. Generar la URI desde la instancia
    uri = totp.provisioning_uri(name=user['correo'], issuer_name="MiBiblioteca")
    
    # Devolvemos el secreto y la URI (El frontend debe generar el QR con la URI)
    return {"secret": secret, "otpauth_url": uri}

@router.post("/confirm-2fa-setup", tags=["Autenticación"])
async def confirm_2fa(
    username: str = Form(...),
    secret: str = Form(...),
    code: str = Form(...)
):
    """El usuario escanea el QR y manda un código para confirmar que funciona"""
    user = AuthRepository.get_user_by_username(username)
    if not user: raise HTTPException(status_code=404)

    # Validar que el código coincida con el secreto que acabamos de generar
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
         raise HTTPException(status_code=400, detail="Código incorrecto. Intenta de nuevo.")

    # Si es correcto, guardamos el secreto en la BD y activamos el 2FA
    AuthRepository.enable_2fa_for_user(user['id'], secret)
    
    return {"detail": "2FA activado correctamente. Por favor inicia sesión."}

@router.post("/refresh", tags=["Autenticación"])
async def refresh_access_token(user: Dict[str, Any] = Depends(get_current_user_from_refresh_token_cookie)):
    return await AuthService.refresh(user)

@router.post("/logout", tags=["Autenticación"])
async def logout(response: Response, refresh_token: str = Cookie(None)):
    return await AuthService.logout(response, refresh_token)

@router.post("/forgot-password", tags=["Autenticación"])
async def forgot_password(
    background_tasks: BackgroundTasks,
    username: str = Form(...) # Recibimos solo el usuario
):
    """
    Inicia el flujo de recuperación. Envía un correo con link al usuario.
    """
    # 1. Buscar usuario
    user = AuthRepository.get_user_by_username(username)
    
    # 2. Validación de Seguridad (Silent fail)
    if not user:
        return {"detail": "Si el usuario existe, se ha enviado un correo de recuperación."}

    # 3. Generar Token Seguro
    token = AuthRepository.create_password_reset_token(user['nombre'])
    
    # 4. Construir el Link para el Frontend
    reset_link = f"{FRONTEND_BASE_URL}/reset-password?token={token}"

    # 5. Enviar Correo
    email_context = {
        "username": user['nombre'],
        "reset_link": reset_link
    }
    
    background_tasks.add_task(
        send_email_template, 
        subject="Recuperar tu Contraseña", 
        email_to=[user['correo']], 
        template_name="password_recovery.html",
        template_body=email_context
    )

    return {"detail": "Si el usuario existe, se ha enviado un correo de recuperación."}

@router.post("/reset-password-confirm", tags=["Autenticación"])
async def reset_password_confirm(data: PasswordResetConfirm, background_tasks: BackgroundTasks):
    """
    Recibe el token y la nueva contraseña.
    Valida el token y actualiza la BD.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El enlace de recuperación es inválido o ha expirado.",
    )

    try:
        # 1. Decodificar el Token
        # Esto valida automáticamente la firma y la fecha de expiración (15 min)
        payload = jwt.decode(data.token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        # 2. Validaciones Extra de Seguridad
        if username is None:
            raise credentials_exception
            
        # IMPORTANTE: Verificar que sea un token de RESET y no uno de LOGIN robado
        if token_type != "password_reset":
            raise HTTPException(status_code=400, detail="Tipo de token inválido para esta operación.")

        # 3. Hashear la nueva contraseña
        new_hash = pwd_context.hash(data.new_password)

        # 4. Guardar en Base de Datos
        success = AuthRepository.update_password_by_username(username, new_hash)
        
        if not success:
            raise HTTPException(status_code=500, detail="Error al actualizar la contraseña.")
        
        user_data = AuthRepository.get_user_by_username(username)
    
        background_tasks.add_task(
            send_email_template,
            subject="Aviso de Seguridad: Contraseña modificada",
            email_to=[user_data['correo']],
            template_name="password_changed.html",
            template_body={"username": username}
        )

        return {"detail": "Contraseña actualizada correctamente. Por favor inicia sesión."}

    except JWTError:
        # Si el token expiró o fue manipulado, cae aquí
        raise credentials_exception

@router.post("/register/student", tags=["Gestión Usuarios"])
async def register_student(student: StudentRegister, background_tasks: BackgroundTasks):
    """
    Registra un nuevo alumno validando sus datos contra Moodle.
    """
    print(f"DEBUG: Intento de registro: {student.username}")

    # PASO 1: Verificar si ya existe localmente en biblioteca_db
    local_user = AuthRepository.get_user_by_username(student.username)
    if local_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este usuario ya está registrado en la biblioteca."
        )

    # PASO 2: Validar contra la base de datos de Moodle
    # (Se conecta a 172.30.8.113 y consulta mdl_user)
    is_valid_moodle = AuthRepository.validate_moodle_student(student.username, student.email)
    
    if not is_valid_moodle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Datos no válidos. No encontramos un estudiante activo en el Campus (Moodle) con ese Usuario y Correo."
        )

    # PASO 3: Hashear contraseña y Crear usuario local
    hashed_password = pwd_context.hash(student.password)
    
    success = AuthRepository.create_local_student(
        username=student.username, 
        password_hash=hashed_password, 
        email=student.email, 
        id_sede=student.id_sede
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error interno al crear el usuario."
        )
    
    email_context = {
        "username": student.username,
        "login_url": "https://biblioteca.upso.edu.ar/login" # La URL de tu Frontend (React/Vue)
    }
    
    # Agregamos la tarea en segundo plano
    background_tasks.add_task(
        send_email_template, 
        subject="¡Bienvenido a la Biblioteca UPSO!", 
        email_to=[student.email], 
        template_name="registration_success.html", # Nombre del archivo
        template_body=email_context
    )

    return {"detail": "Registro exitoso. Ya puedes iniciar sesión en la biblioteca."}

@router.get("/users/me", tags=["Usuarios"])
async def read_users_me(current_user: Dict[str, Any] = Depends(allow_everyone)):
    """
    Devuelve la información del usuario actual y su sesión.
    
    Seguridad aplicada:
    1. Token JWT válido.
    2. Sesión activa en BD (si haces logout, esto falla).
    3. IP Validada (si la cookie fue robada y usada en otra IP, esto falla).
    4. IP Desencriptada (Fernet la desencriptó antes de llegar aquí).
    """
    
    # Mapeo simple de roles para que el front muestre el nombre y no el número
    role_names = {1: "SuperAdmin", 2: "Admin Sede", 3: "Alumno"}
    role_name = role_names.get(current_user["id_rol"], "Desconocido")

    return {
        "profile": {
            "id": current_user["id"],
            "username": current_user["nombre"],
            "email": current_user["correo"],
            "role_id": current_user["id_rol"],
            "role_name": role_name,
            "2fa_active": bool(current_user["is_2fa_enabled"]) # True/False
        },
        "session": {
            "current_ip": current_user["ip_address"], # <--- Aquí ya la ves desencriptada (Ej: 192.168.1.50)
            "user_agent": current_user["user_agent"], # Ej: Mozilla/5.0...
            "session_id": current_user["session_token"]
        }
    }
