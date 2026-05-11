import pyotp
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import os

# Configuración de cifrado (Carga desde env)
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", b'M3nJ6bV9cQ2wE5rT8yU1iO4pA7sD0fG3hK9lL2zX5vN=') 
cipher_suite = Fernet(ENCRYPTION_KEY)

# Contexto de contraseñas
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# ... (Mantén tu función get_user_by_username igual, PERO quita session_token del SELECT si borraste la columna) ...
def encrypt_data(data: str) -> str:
    """Encripta un string (ej: IP) para guardarlo en la BD."""
    if not data: return None
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    """Desencripta el string traído de la BD."""
    if not token: return None
    try:
        return cipher_suite.decrypt(token.encode()).decode()
    except Exception:
        return "Unknown"
    
def verify_totp_code(secret: str, code: str) -> bool:
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

