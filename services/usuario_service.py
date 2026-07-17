import pymysql
from database.connection import DatabaseConnection
from models.usuario import Usuario
from services.exceptions import (
    UsuarioDuplicadoError,
    UsuarioNoEncontradoError,
    DNIDuplicadoError,
    UsuarioConPrestamoActivoError,
    BibliotecaError
)

class UsuarioService:
    """Clase encargada del CRUD y la lógica de negocio asociada a los Usuarios."""

    @staticmethod
    def registrar_usuario(usuario: Usuario) -> int:
        """
        Registra un nuevo usuario en la base de datos.
        Retorna el ID autoincremental asignado al usuario.
        Lanza UsuarioDuplicadoError si el correo ya existe.
        Lanza DNIDuplicadoError si el DNI ya existe.
        """
        query = "INSERT INTO usuarios (nombre, correo, dni) VALUES (%s, %s, %s)"
        try:
            with DatabaseConnection() as (conn, cursor):
                cursor.execute(query, (usuario.nombre, usuario.correo, usuario.dni))
                conn.commit()
                # Obtener el ID autoincrementable generado por MySQL
                nuevo_id = cursor.lastrowid
                usuario.id = nuevo_id
                return nuevo_id
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:  # Código de error MySQL para duplicado
                err_msg = e.args[1] if len(e.args) > 1 else str(e)
                if "correo" in err_msg:
                    raise UsuarioDuplicadoError(f"El correo electrónico '{usuario.correo}' ya está en uso por otro miembro.")
                elif "dni" in err_msg:
                    raise DNIDuplicadoError(f"El DNI/cédula '{usuario.dni}' ya está registrado por otro miembro.")
                else:
                    raise BibliotecaError(f"Error de duplicidad: {err_msg}")
            raise e

    @staticmethod
    def modificar_usuario(id_usuario: int, nombre: str, correo: str, dni: str) -> bool:
        """
        Modifica los datos de un usuario existente.
        Lanza UsuarioNoEncontradoError si el ID no existe.
        Lanza UsuarioDuplicadoError o DNIDuplicadoError si hay colisión.
        """
        # Verificar existencia
        UsuarioService.buscar_por_id(id_usuario)

        query = "UPDATE usuarios SET nombre = %s, correo = %s, dni = %s WHERE id = %s"
        try:
            with DatabaseConnection() as (conn, cursor):
                cursor.execute(query, (nombre, correo, dni, id_usuario))
                conn.commit()
                return True
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                err_msg = e.args[1] if len(e.args) > 1 else str(e)
                if "correo" in err_msg:
                    raise UsuarioDuplicadoError(f"El correo electrónico '{correo}' ya está en uso por otro miembro.")
                elif "dni" in err_msg:
                    raise DNIDuplicadoError(f"El DNI/cédula '{dni}' ya está registrado por otro miembro.")
                else:
                    raise BibliotecaError(f"Error de integridad: {err_msg}")
            raise e

    @staticmethod
    def eliminar_usuario(id_usuario: int) -> bool:
        """
        Elimina un usuario si no tiene préstamos activos.
        Lanza UsuarioNoEncontradoError si el ID no existe.
        Lanza UsuarioConPrestamoActivoError si tiene préstamos activos.
        """
        # Verificar existencia
        UsuarioService.buscar_por_id(id_usuario)

        with DatabaseConnection() as (conn, cursor):
            # 1. Verificar si tiene préstamos activos
            cursor.execute("SELECT id FROM prestamos WHERE id_usuario = %s AND estado = 'Activo'", (id_usuario,))
            if cursor.fetchone():
                raise UsuarioConPrestamoActivoError(
                    f"No se puede eliminar el usuario con ID {id_usuario} porque tiene préstamos activos sin devolver."
                )

            # 2. Eliminar préstamos devueltos históricos asociados
            cursor.execute("DELETE FROM prestamos WHERE id_usuario = %s AND estado = 'Devuelto'", (id_usuario,))

            # 3. Eliminar el usuario
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
            conn.commit()
            return True

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
