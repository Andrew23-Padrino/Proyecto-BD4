import pymysql
import datetime
from database.connection import DatabaseConnection
from models.libro import Libro
from services.exceptions import LibroDuplicadoError, LibroNoEncontradoError, BibliotecaError

class LibroService:
    """Clase encargada del CRUD y la lógica de negocio asociada a los Libros."""

    @staticmethod
    def registrar_libro(libro: Libro) -> bool:
        """
        Inserta un nuevo libro en la base de datos.
        Lanza LibroDuplicadoError si el ISBN ya existe.
        """
        current_year = datetime.datetime.now().year
        if libro.anio_publicacion <= 0:
            raise BibliotecaError("El año de publicación debe ser mayor a 0.")
        if libro.anio_publicacion > current_year:
            raise BibliotecaError(f"El año de publicación ({libro.anio_publicacion}) no puede ser mayor al año actual ({current_year}).")

        query = """
            INSERT INTO libros (isbn, titulo, autor, anio_publicacion, cantidad_disponible, categoria)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            with DatabaseConnection() as (conn, cursor):
                cursor.execute(query, (
                    libro.isbn,
                    libro.titulo,
                    libro.autor,
                    libro.anio_publicacion,
                    libro.cantidad_disponible,
                    libro.categoria
                ))
                conn.commit()
                return True
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:  # Código de error MySQL para duplicado
                raise LibroDuplicadoError(f"El libro con ISBN '{libro.isbn}' ya está registrado en el sistema.")
            raise e

    @staticmethod
    def buscar_por_isbn(isbn: str) -> Libro:
        """
        Busca un libro específico por su código ISBN.
        Lanza LibroNoEncontradoError si no existe.
        """
        query = "SELECT * FROM libros WHERE isbn = %s"
        with DatabaseConnection() as (conn, cursor):
            cursor.execute(query, (isbn,))
            row = cursor.fetchone()
            if not row:
                raise LibroNoEncontradoError(f"No se encontró ningún libro registrado con el ISBN '{isbn}'.")
            return Libro.from_dict(row)

    @staticmethod
    def buscar_libros(termino: str) -> list:
        """
        Busca libros que coincidan parcialmente por título, autor o categoría.
        """
        query = """
            SELECT * FROM libros 
            WHERE titulo LIKE %s OR autor LIKE %s OR categoria LIKE %s
        """
        like_term = f"%{termino}%"
        with DatabaseConnection() as (conn, cursor):
            cursor.execute(query, (like_term, like_term, like_term))
            rows = cursor.fetchall()
            return [Libro.from_dict(row) for row in rows]

    @staticmethod
    def listar_todos() -> list:
        """
        Obtiene la lista de todos los libros en la base de datos.
        """
        query = "SELECT * FROM libros ORDER BY titulo"
        with DatabaseConnection() as (conn, cursor):
            cursor.execute(query)
            rows = cursor.fetchall()
            return [Libro.from_dict(row) for row in rows]
