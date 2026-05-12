from sqlmodel import create_engine, Session
import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conexion = mysql.connector.connect(
                host ="127.0.0.1",
                user ="root",
                passwd ="admin123",
                database = "bibliotecadb"
            )
        return conexion

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def connectionBDmoddle():
    try:
        mydb = mysql.connector.connect(
            host ="172.30.8.113",
            user ="biblioteca",
            passwd ="qB28*4YETk#9",
            database = "moodle",
            ssl_disabled = True
        )

        if mydb.is_connected():
            print ("Conexion exitosa a BD")
            return mydb

    except mysql.connector.Error as err:
        print(f"Error en la conexion a BD: {err}")
        return None