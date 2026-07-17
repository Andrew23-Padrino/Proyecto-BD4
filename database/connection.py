import pymysql
import os
import config

class DatabaseConnection:
    """
    Administrador de contexto (Context Manager) para gestionar de forma segura
    la apertura, confirmación (commit) y cierre de la conexión y cursor a MySQL.
    """
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        try:
            # Conexión al servidor MySQL configurado
            self.connection = pymysql.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
                charset=config.DB_CHARSET,
                cursorclass=pymysql.cursors.DictCursor  # Retorna resultados como diccionarios
            )
            self.cursor = self.connection.cursor()
            return self.connection, self.cursor
        except pymysql.MySQLError as e:
            print(f"\n[ERROR DE CONEXIÓN] No se pudo establecer conexión con MySQL: {e}")
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Si ocurrió un error y hay una conexión abierta, hacemos rollback por seguridad
        if exc_type is not None and self.connection:
            try:
                self.connection.rollback()
            except Exception:
                pass
        
        # Cerrar el cursor si está abierto
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
        
        # Cerrar la conexión si está abierta
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass


def inicializar_base_de_datos(schema_path=None):
    """
    Conecta al servidor MySQL sin especificar una base de datos para leer el archivo schema.sql 
    y crear tanto la base de datos como las tablas e índices necesarios.
    """
    if schema_path is None:
        # Ruta por defecto
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_path = os.path.join(base_dir, 'database', 'schema.sql')

    print(f"Intentando inicializar la base de datos usando: {schema_path}")
    try:
        # Nos conectamos al servidor sin base de datos específica para poder crearla si no existe
        conn = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            charset=config.DB_CHARSET
        )
        
        with conn.cursor() as cursor:
            with open(schema_path, 'r', encoding='utf-8') as f:
                # Dividir el archivo SQL por punto y coma (;) para ejecutar comando por comando
                sql_content = f.read()
                # Separar comandos omitiendo los comentarios o bloques vacíos
                commands = sql_content.split(';')
                for command in commands:
                    cmd_stripped = command.strip()
                    if cmd_stripped:
                        cursor.execute(cmd_stripped)
            conn.commit()
        conn.close()
        print("[OK] Base de datos y tablas inicializadas con éxito en MySQL.")
        return True
    except pymysql.MySQLError as e:
        print(f"\n[ERROR AL INICIALIZAR BASE DE DATOS] Detalle: {e}")
        return False
    except FileNotFoundError:
        print(f"\n[ERROR] No se encontró el archivo de esquema en: {schema_path}")
        return False
