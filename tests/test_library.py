import unittest
from unittest.mock import MagicMock, patch
from services.exceptions import (
    UsuarioNoEncontradoError,
    LibroNoEncontradoError,
    SinStockError,
    BibliotecaError
)
from services.prestamo_service import PrestamoService
from services.libro_service import LibroService
from models.libro import Libro

class TestLibraryService(unittest.TestCase):
    """
    Pruebas unitarias para validar las reglas de negocio de los servicios de biblioteca
    mediante el uso de simulaciones (mocks) para evitar requerir una base de datos MySQL activa.
    """

    @patch('services.prestamo_service.DatabaseConnection')
    def test_registrar_prestamo_usuario_no_existe(self, mock_db_conn):
        """Valida que lanzar UsuarioNoEncontradoError cuando el usuario no existe."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = (mock_conn, mock_cursor)
        
        # Simular que la consulta del usuario retorna None (no encontrado)
        mock_cursor.fetchone.return_value = None
        
        with self.assertRaises(UsuarioNoEncontradoError):
            PrestamoService.registrar_prestamo(999, "978-3-16-148410-0")

    @patch('services.prestamo_service.DatabaseConnection')
    def test_registrar_prestamo_libro_no_existe(self, mock_db_conn):
        """Valida que lanzar LibroNoEncontradoError cuando el libro no existe."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = (mock_conn, mock_cursor)
        
        # Simular que el usuario existe pero el libro retorna None
        mock_cursor.fetchone.side_effect = [
            {"nombre": "Carlos Perez"}, # Retorno para usuario
            None                        # Retorno para libro
        ]
        
        with self.assertRaises(LibroNoEncontradoError):
            PrestamoService.registrar_prestamo(1, "978-9-99-999999-9")

    @patch('services.prestamo_service.DatabaseConnection')
    def test_registrar_prestamo_sin_stock(self, mock_db_conn):
        """Valida que lanzar SinStockError cuando el stock disponible es menor o igual a 0."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = (mock_conn, mock_cursor)
        
        # Simular que el usuario existe y el libro tiene stock = 0
        mock_cursor.fetchone.side_effect = [
            {"nombre": "Carlos Perez"},
            {"titulo": "El Quijote", "cantidad_disponible": 0}
        ]
        
        with self.assertRaises(SinStockError):
            PrestamoService.registrar_prestamo(1, "978-3-16-148410-0")

    def test_registrar_libro_anio_invalido_negativo(self):
        """Valida que se lance BibliotecaError al registrar un libro con año <= 0."""
        libro = Libro("978-3-16-148410-0", "Test Title", "Test Author", 0, 5)
        with self.assertRaises(BibliotecaError) as ctx:
            LibroService.registrar_libro(libro)
        self.assertEqual(str(ctx.exception), "El año de publicación debe ser mayor a 0.")

    def test_registrar_libro_anio_invalido_futuro(self):
        """Valida que se lance BibliotecaError al registrar un libro con año en el futuro."""
        import datetime
        future_year = datetime.datetime.now().year + 1
        libro = Libro("978-3-16-148410-0", "Test Title", "Test Author", future_year, 5)
        with self.assertRaises(BibliotecaError) as ctx:
            LibroService.registrar_libro(libro)
        self.assertIn("no puede ser mayor al año actual", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
