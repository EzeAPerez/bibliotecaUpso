from db.database import *
import datetime
from core.config import JWT_REFRESH_TOKEN_EXPIRES
from core.crypto import *


class AuthRepository:

    @staticmethod
    def get_user_by_username(username: str):
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor(dictionary=True)
            # AÑADIDO: Seleccionamos las nuevas columnas
            query = """
                SELECT id, nombre, password, correo, id_rol, 
                    must_change_password, is_2fa_enabled, two_factor_secret 
                FROM userscp WHERE nombre = %s
            """
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            if conexion: conexion.close()

    @staticmethod
    def create_user_session(user_id, jti, ip, user_agent, expires):
        conexion = None
        try:
            # ENCRIPTAMOS LA IP ANTES DE GUARDAR
            encrypted_ip = encrypt_data(ip)
            
            expires = datetime.datetime.now() + JWT_REFRESH_TOKEN_EXPIRES
            conexion = get_connection()
            cursor = conexion.cursor()
            query = """
                INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            # Guardamos encrypted_ip en lugar de ip
            cursor.execute(query, (user_id, jti, encrypted_ip, user_agent, expires))
            conexion.commit()
            cursor.close()
        except Exception as e:
            print(f"Error creando sesión: {e}")
        finally:
            if conexion: conexion.close()

    @staticmethod
    def get_session_data(jti: str):
        """Devuelve datos de la sesión (IP, user_agent, etc) y del usuario asociado"""
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT u.id, u.nombre, u.password, u.correo, u.id_rol, u.is_2fa_enabled,
                    s.session_token,   -- <--- ESTO ES LO QUE TE FALTA AGREGAR
                    s.ip_address, s.user_agent
                FROM user_sessions s
                JOIN userscp u ON s.user_id = u.id
                WHERE s.session_token = %s
            """
            cursor.execute(query, (jti,))
            data = cursor.fetchone()
            cursor.close()
            if data and data['ip_address']:
                decrypted_ip = decrypt_data(data['ip_address'])
                data['ip_address'] = decrypted_ip
            return data
        except Exception as e:
            print(f"Error obteniendo datos de sesión: {e}")
            return None
        finally:
            if conexion: conexion.close()

    @staticmethod
    def clear_user_session_token(jti: str):
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM user_sessions WHERE session_token = %s", (jti,))
            conexion.commit()
            cursor.close()
        except Exception as e:
            print(f"Error eliminando sesión: {e}")
        finally:
            if conexion: conexion.close()

        @staticmethod
        def count_active_sessions(user_id: int) -> int:
            conexion = None
            try:
                conexion = get_connection()
                cursor = conexion.cursor()
                cursor.execute("SELECT COUNT(*) FROM user_sessions WHERE user_id = %s", (user_id,))
                count = cursor.fetchone()[0]
                cursor.close()
                return count
            except Exception as e:
                print(f"Error contando sesiones: {e}")
                return 0
            finally:
                if conexion: conexion.close()

    @staticmethod
    def delete_oldest_session(user_id: int):
        """Borra la sesión más antigua de un usuario para liberar espacio."""
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            # Ordenamos por fecha de creación ascendente (la más vieja primero) y borramos 1
            query = """
                DELETE FROM user_sessions 
                WHERE user_id = %s 
                ORDER BY created_at ASC 
                LIMIT 1
            """
            cursor.execute(query, (user_id,))
            conexion.commit()
            cursor.close()
            print(f"DEBUG: Sesión más antigua eliminada para el usuario ID {user_id} (Rotación automática).")
        except Exception as e:
            print(f"Error rotando sesiones: {e}")
        finally:
            if conexion: conexion.close()
    
    @staticmethod
    def update_password_by_username(username: str, new_password_hash: str):
        """
        Actualiza la contraseña, quita la obligación de cambio y borra sesiones viejas.
        """
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            
            # 1. Obtener ID del usuario primero (para borrar sesiones luego)
            cursor.execute("SELECT id FROM userscp WHERE nombre = %s", (username,))
            row = cursor.fetchone()
            if not row:
                return False
            user_id = row[0]

            # 2. Actualizar Contraseña
            query_update = """
                UPDATE userscp 
                SET password = %s, must_change_password = 0 
                WHERE id = %s
            """
            cursor.execute(query_update, (new_password_hash, user_id))
            
            # 3. Borrar TODAS las sesiones activas (Seguridad: Force Logout)
            # Como cambió la clave, invalidamos los tokens viejos en otros dispositivos.
            cursor.execute("DELETE FROM user_sessions WHERE user_id = %s", (user_id,))
            
            conexion.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error actualizando password reset: {e}")
            return False
        finally:
            if conexion: conexion.close()

    @staticmethod
    # NUEVO: Guardar secreto 2FA y activarlo
    def enable_2fa_for_user(user_id: int, secret: str):
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            query = "UPDATE userscp SET two_factor_secret = %s, is_2fa_enabled = 1 WHERE id = %s"
            cursor.execute(query, (secret, user_id))
            conexion.commit()
            cursor.close()
        except Exception as e:
            print(f"Error activando 2FA: {e}")
        finally:
            if conexion: conexion.close()

    @staticmethod
    # NUEVA FUNCIÓN: Verificar cuántas sesiones tiene el usuario
    def count_active_sessions(user_id: int) -> int:
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_sessions WHERE user_id = %s", (user_id,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            print(f"Error contando sesiones: {e}")
            return 0
        finally:
            if conexion: conexion.close()

    @staticmethod
    # MODIFICADA: Validar sesión buscando en la nueva tabla
    def get_user_by_session_token(jti: str):
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor(dictionary=True)
            # Hacemos JOIN para traer los datos del usuario si el token es válido
            query = """
                SELECT u.id, u.nombre, u.password, u.correo, u.id_rol 
                FROM user_sessions s
                JOIN userscp u ON s.user_id = u.id
                WHERE s.session_token = %s
            """
            cursor.execute(query, (jti,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            print(f"Error validando sesión: {e}")
            return None
        finally:
            if conexion: conexion.close()

    @staticmethod
    def get_session_data(jti: str):
        """Devuelve datos de la sesión (IP, user_agent, etc) y del usuario asociado"""
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT u.id, u.nombre, u.password, u.correo, u.id_rol, u.is_2fa_enabled,
                    s.session_token,   -- <--- ESTO ES LO QUE TE FALTA AGREGAR
                    s.ip_address, s.user_agent
                FROM user_sessions s
                JOIN userscp u ON s.user_id = u.id
                WHERE s.session_token = %s
            """
            cursor.execute(query, (jti,))
            data = cursor.fetchone()
            cursor.close()
            if data and data['ip_address']:
                decrypted_ip = decrypt_data(data['ip_address'])
                data['ip_address'] = decrypted_ip
            return data
        except Exception as e:
            print(f"Error obteniendo datos de sesión: {e}")
            return None
        finally:
            if conexion: conexion.close()

    @staticmethod
    # MODIFICADA: Eliminar sesión específica (Logout)
    def clear_user_session_token(jti: str):
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM user_sessions WHERE session_token = %s", (jti,))
            conexion.commit()
            cursor.close()
        except Exception as e:
            print(f"Error eliminando sesión: {e}")
        finally:
            if conexion: conexion.close()

    @staticmethod
    # NUEVA: (Opcional) Limpiar sesiones expiradas automáticamente
    def clean_expired_sessions():
        """Borra todas las sesiones cuya fecha de expiración ya pasó."""
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            # NOW() es la función de fecha actual en MySQL
            query = "DELETE FROM user_sessions WHERE expires_at < NOW()"
            cursor.execute(query)
            conexion.commit()
            deleted_count = cursor.rowcount
            cursor.close()
            if deleted_count > 0:
                print(f"DEBUG: Mantenimiento completado. {deleted_count} sesiones expiradas eliminadas.")
        except Exception as e:
            print(f"Error limpiando sesiones expiradas: {e}")
        finally:
            if conexion: conexion.close()

    @staticmethod
    # 2. ROTACIÓN: Borrar la sesión más vieja de un usuario específico
    def delete_oldest_session(user_id: int):
        """Borra la sesión más antigua de un usuario para liberar espacio."""
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            # Ordenamos por fecha de creación ascendente (la más vieja primero) y borramos 1
            query = """
                DELETE FROM user_sessions 
                WHERE user_id = %s 
                ORDER BY created_at ASC 
                LIMIT 1
            """
            cursor.execute(query, (user_id,))
            conexion.commit()
            cursor.close()
            print(f"DEBUG: Sesión más antigua eliminada para el usuario ID {user_id} (Rotación automática).")
        except Exception as e:
            print(f"Error rotando sesiones: {e}")
        finally:
            if conexion: conexion.close()

    @staticmethod
    # 1. FUNCIÓN DE VALIDACIÓN CONTRA MOODLE
    def validate_moodle_student(username: str, email: str) -> bool:
        """
        Conecta a la BD de Moodle y verifica si existe un usuario
        con ese username y email exactos en la tabla mdl_user.
        """
        conexion = None
        try:
            print(f"DEBUG: Verificando en Moodle -> User: {username}, Email: {email}")
            conexion = connectionBDmoddle() # Usamos la nueva conexión
            if not conexion:
                return False
                
            cursor = conexion.cursor()
            # Consultamos la tabla mdl_user
            query = "SELECT id FROM mdl_user WHERE username = %s AND email = %s"
            cursor.execute(query, (username, email))
            result = cursor.fetchone()
            cursor.close()
            
            # Si devuelve algo, es True (Existe y coincide). Si es None, es False.
            return result is not None
            
        except Exception as e:
            print(f"Error validando con Moodle: {e}")
            return False
        finally:
            if conexion and conexion.is_connected():
                conexion.close()

    @staticmethod
    # 2. FUNCIÓN PARA CREAR EL ESTUDIANTE LOCALMENTE
    def create_local_student(username: str, password_hash: str, email: str, id_sede: int):
        """
        Crea el usuario en userscp con los valores por defecto para alumnos:
        Rol = 3 (Alumno)
        must_change_password = 0
        is_2fa_enabled = 0
        """
        conexion = None
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            
            query = """
                INSERT INTO userscp 
                (nombre, password, correo, id_sede, id_rol, must_change_password, is_2fa_enabled) 
                VALUES (%s, %s, %s, %s, 3, 0, 0)
            """
            # Nota: El '3' hardcodeado es el ID del rol Alumno
            # Nota: Los '0' son para no obligar cambio de pass ni 2FA
            
            cursor.execute(query, (username, password_hash, email, id_sede))
            conexion.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error creando estudiante local: {e}")
            return False
        finally:
            if conexion:
                conexion.close()
