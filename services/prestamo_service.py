from datetime import date, timedelta
import pymysql
from database.connection import DatabaseConnection
from services.exceptions import (
    UsuarioNoEncontradoError,
    LibroNoEncontradoError,
    SinStockError,
    PrestamoNoEncontradoError,
    PrestamoYaDevueltoError
)

class PrestamoService:
    """Clase encargada de la lógica transaccional asociada a Préstamos y Devoluciones."""

    @staticmethod
    def registrar_prestamo(id_usuario: int, isbn: str, dias_prestamo: int = 7) -> int:
        """
        Registra el préstamo de un libro de forma transaccional (ACID).
        - Verifica si el usuario existe.
        - Verifica si el libro existe y bloquea la fila (FOR UPDATE) para evitar race conditions.
        - Comprueba que haya stock suficiente.
        - Inserta el préstamo en estado 'Activo'.
        - Descuenta 1 unidad de stock en libros.
        - Confirma los cambios (COMMIT).
        """
        hoy = date.today()
        fecha_devolucion = hoy + timedelta(days=dias_prestamo)

        with DatabaseConnection() as (conn, cursor):
            # 1. Verificar existencia del usuario
            cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (id_usuario,))
            if not cursor.fetchone():
                raise UsuarioNoEncontradoError(f"El usuario con ID '{id_usuario}' no está registrado.")

            # 2. Verificar existencia del libro y bloquear fila para escritura concorrente
            cursor.execute("SELECT titulo, cantidad_disponible FROM libros WHERE isbn = %s FOR UPDATE", (isbn,))
            libro_row = cursor.fetchone()
            if not libro_row:
                raise LibroNoEncontradoError(f"El libro con ISBN '{isbn}' no está registrado.")

            # 3. Validar disponibilidad de stock
            stock_actual = libro_row['cantidad_disponible']
            if stock_actual <= 0:
                raise SinStockError(
                    f"No hay unidades disponibles de '{libro_row['titulo']}' (ISBN: {isbn}) para préstamo."
                )

            # 4. Registrar préstamo
            query_prestamo = """
                INSERT INTO prestamos (id_usuario, isbn, fecha_prestamo, fecha_devolucion_esperada, estado)
                VALUES (%s, %s, %s, %s, 'Activo')
            """
            cursor.execute(query_prestamo, (id_usuario, isbn, hoy, fecha_devolucion))
            prestamo_id = cursor.lastrowid

            # 5. Disminuir el stock en 1
            query_stock = "UPDATE libros SET cantidad_disponible = cantidad_disponible - 1 WHERE isbn = %s"
            cursor.execute(query_stock, (isbn,))

            # Confirmar transacción
            conn.commit()
            return prestamo_id

    @staticmethod
    def registrar_devolucion(id_prestamo: int) -> bool:
        """
        Registra la devolución de un libro de forma transaccional.
        - Verifica el préstamo en base al ID y bloquea su fila.
        - Valida que el préstamo esté en estado 'Activo'.
        - Actualiza el estado a 'Devuelto'.
        - Devuelve 1 unidad al stock del libro correspondiente.
        - Confirma los cambios (COMMIT).
        """
        with DatabaseConnection() as (conn, cursor):
            # 1. Obtener y bloquear el préstamo
            cursor.execute("SELECT isbn, estado FROM prestamos WHERE id = %s FOR UPDATE", (id_prestamo,))
            prestamo_row = cursor.fetchone()
            if not prestamo_row:
                raise PrestamoNoEncontradoError(f"No existe ningún registro de préstamo con el ID '{id_prestamo}'.")

            # 2. Validar que no se haya devuelto ya
            if prestamo_row['estado'] == 'Devuelto':
                raise PrestamoYaDevueltoError(f"El préstamo con ID '{id_prestamo}' ya figura como 'Devuelto'.")

            isbn_libro = prestamo_row['isbn']

            # 3. Actualizar estado del préstamo
            cursor.execute("UPDATE prestamos SET estado = 'Devuelto' WHERE id = %s", (id_prestamo,))

            # 4. Aumentar el stock del libro en 1
            cursor.execute(
                "UPDATE libros SET cantidad_disponible = cantidad_disponible + 1 WHERE isbn = %s",
                (isbn_libro,)
            )

            # Confirmar transacción
            conn.commit()
            return True

    @staticmethod
    def listar_prestamos(solo_activos: bool = False) -> list:
        """
        Retorna la lista de préstamos con información extendida (nombres de usuario y libros).
        """
        query = """
            SELECT p.id, p.id_usuario, u.nombre AS nombre_usuario, p.isbn, l.titulo AS titulo_libro, 
                   p.fecha_prestamo, p.fecha_devolucion_esperada, p.estado
            FROM prestamos p
            JOIN usuarios u ON p.id_usuario = u.id
            JOIN libros l ON p.isbn = l.isbn
        """
        if solo_activos:
            query += " WHERE p.estado = 'Activo'"
        query += " ORDER BY p.fecha_prestamo DESC, p.id DESC"

        with DatabaseConnection() as (conn, cursor):
            cursor.execute(query)
            return cursor.fetchall()
