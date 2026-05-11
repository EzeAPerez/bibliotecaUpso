import os
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List, Dict, Any

TEMPLATE_FOLDER = Path(__file__).parent / 'templates'

# Configuración del servidor (IDEALMENTE ESTO VA EN .ENV)
conf = ConnectionConfig(
    # 1. CREDENCIALES (Login) - Tienen que ser las reales
    MAIL_USERNAME = "informatica@upso.edu.ar",
    MAIL_PASSWORD = "VP5LZG9i",        
    # 2. REMITENTE (Lo que ve el usuario)
    MAIL_FROM = "informatica@upso.edu.ar",      
    MAIL_FROM_NAME = "Biblioteca UPSO",           
    # 3. Configuración Técnica
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.uns.edu.ar",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = TEMPLATE_FOLDER,
)

async def send_email_template(subject: str, email_to: List[EmailStr], template_name: str, template_body: Dict[str, Any]):
    """
    Envía un correo usando una plantilla HTML de la carpeta templates.
    """
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        template_body=template_body, 
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    
    try:
        # Usamos send_message indicando el nombre del archivo template
        await fm.send_message(message, template_name=template_name)
        print(f"DEBUG: Correo enviado a {email_to} usando plantilla {template_name}")
    except Exception as e:
        print(f"ERROR: Falló el envío de correo: {e}")