from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    password: str
    session_token: str = None

class StudentRegister(BaseModel):
    username: str      # Debe coincidir con Moodle
    email: EmailStr    # Debe coincidir con Moodle
    password: str      # Nueva contraseña para TU sistema
    id_sede: int       # Sede seleccionada

class PasswordResetConfirm(BaseModel):
    token: str          # El token largo que venía en la URL
    new_password: str   # La nueva contraseña que escribió el usuario