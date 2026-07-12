from datetime import date

class Prestamo:
    """Clase que representa la entidad Prestamo."""
    def __init__(self, id_usuario: int, isbn: str, fecha_prestamo: date, fecha_devolucion_esperada: date, estado: str = "Activo", id_prestamo: int = None):
        self.id = id_prestamo
        self.id_usuario = id_usuario
        self.isbn = isbn
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion_esperada = fecha_devolucion_esperada
        self.estado = estado

    def __str__(self):
        id_str = self.id if self.id else "Nuevo"
        return (f"Prestamo [ID: {id_str}] | Usuario ID: {self.id_usuario} | Libro ISBN: {self.isbn} "
                f"| Desde: {self.fecha_prestamo} | Hasta: {self.fecha_devolucion_esperada} | Estado: {self.estado}")

    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia de Prestamo a partir de un diccionario proveniente de la base de datos."""
        if not data:
            return None
        return cls(
            id_prestamo=data.get('id'),
            id_usuario=data.get('id_usuario'),
            isbn=data.get('isbn'),
            fecha_prestamo=data.get('fecha_prestamo'),
            fecha_devolucion_esperada=data.get('fecha_devolucion_esperada'),
            estado=data.get('estado', 'Activo')
        )
