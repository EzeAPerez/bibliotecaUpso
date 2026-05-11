from datetime import timedelta

JWT_SECRET_KEY = "SECRET_KEY"
JWT_ALGORITHM = "HS256"

JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

FRONTEND_BASE_URL = "https://dev/biblioteca"

"""
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "b39f150e70c5383a8b41724c311403f56b6b9d62d2950543e59b207a9e623c21")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=7)
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", b'M3nJ6bV9cQ2wE5rT8yU1iO4pA7sD0fG3hK9lL2zX5vN=') 
cipher_suite = Fernet(ENCRYPTION_KEY)
RESET_TOKEN_EXPIRES_MINUTES = 15
"""
