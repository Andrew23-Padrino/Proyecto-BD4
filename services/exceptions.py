class BibliotecaError(Exception):
    """Excepción base para el sistema de biblioteca."""
    pass

class LibroDuplicadoError(BibliotecaError):
    """Se lanza al intentar registrar un libro con un ISBN que ya existe."""
    pass

class LibroNoEncontradoError(BibliotecaError):
    """Se lanza cuando no se encuentra un libro por su ISBN."""
    pass

class UsuarioDuplicadoError(BibliotecaError):
    """Se lanza al intentar registrar un usuario con un correo que ya existe."""
    pass

class UsuarioNoEncontradoError(BibliotecaError):
    """Se lanza cuando no se encuentra el usuario."""
    pass

class SinStockError(BibliotecaError):
    """Se lanza al intentar prestar un libro que no tiene ejemplares disponibles."""
    pass

class PrestamoNoEncontradoError(BibliotecaError):
    """Se lanza cuando no se encuentra el registro de préstamo."""
    pass

class PrestamoYaDevueltoError(BibliotecaError):
    """Se lanza cuando se intenta devolver un préstamo que ya fue cerrado/devuelto."""
    pass
