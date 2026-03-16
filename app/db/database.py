from sqlmodel import SQLModel, create_engine, Session
import mysql.connector
from mysql.connector import Error

DATABASE_URL = "mysql+pymysql://root@localhost:3306/bibliotecaUpso"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def get_connection():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bibliotecaUpso",
            port=3306
        )
        return conexion

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None