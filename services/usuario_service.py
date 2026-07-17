import pymysql
from database.connection import DatabaseConnection
from models.usuario import Usuario
from services.exceptions import UsuarioDuplicadoError, UsuarioNoEncontradoError

class UsuarioService:
    """Clase encargada del CRUD y la lógica de negocio asociada a los Usuarios."""

    @staticmethod
    def registrar_usuario(usuario: Usuario) -> int:
        """
        Registra un nuevo usuario en la base de datos.
        Retorna el ID autoincremental asignado al usuario.
        Lanza UsuarioDuplicadoError si el correo ya existe.
        """
        query = "INSERT INTO usuarios (nombre, correo) VALUES (%s, %s)"
        try:
            with DatabaseConnection() as (conn, cursor):
                cursor.execute(query, (usuario.nombre, usuario.correo))
                conn.commit()
                # Obtener el ID autoincrementable generado por MySQL
                nuevo_id = cursor.lastrowid
                usuario.id = nuevo_id
                return nuevo_id
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:  # Código de error MySQL para duplicado
                raise UsuarioDuplicadoError(f"El correo electrónico '{usuario.correo}' ya está en uso por otro miembro.")
            raise e

    @staticmethod
    def buscar_por_id(id_usuario: int) -> Usuario:
        """
        Busca un usuario en base a su ID único.
        Lanza UsuarioNoEncontradoError si no existe.
        """
        query = "SELECT * FROM usuarios WHERE id = %s"
        with DatabaseConnection() as (conn, cursor):
            cursor.execute(query, (id_usuario,))
            row = cursor.fetchone()
            if not row:
                raise UsuarioNoEncontradoError(f"No se encontró ningún usuario con el ID '{id_usuario}'.")
            return Usuario.from_dict(row)

    @staticmethod
    def buscar_por_correo(correo: str) -> Usuario:
        """
        Busca un usuario por su correo electrónico único.
        Lanza UsuarioNoEncontradoError si no existe.
        """
        query = "SELECT * FROM usuarios WHERE correo = %s"
        with DatabaseConnection() as (conn, cursor):
            cursor.execute(query, (correo,))
            row = cursor.fetchone()
            if not row:
                raise UsuarioNoEncontradoError(f"No existe ningún usuario registrado con el correo '{correo}'.")
            return Usuario.from_dict(row)

    @staticmethod
    def listar_todos() -> list:
        """
        Obtiene la lista de todos los usuarios de la biblioteca.
        """
        query = "SELECT * FROM usuarios ORDER BY nombre"
        with DatabaseConnection() as (conn, cursor):
            cursor.execute(query)
            rows = cursor.fetchall()
            return [Usuario.from_dict(row) for row in rows]
