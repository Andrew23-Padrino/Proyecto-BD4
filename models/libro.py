class Libro:
    """Clase que representa la entidad Libro."""
    def __init__(self, isbn: str, titulo: str, autor: str, anio_publicacion: int, cantidad_disponible: int, categoria: str = "Sin Categoría"):
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.anio_publicacion = anio_publicacion
        self.cantidad_disponible = cantidad_disponible
        self.categoria = categoria

    def __str__(self):
        return f"Libro [ISBN: {self.isbn}] '{self.titulo}' - {self.autor} ({self.anio_publicacion}) | Stock: {self.cantidad_disponible} | Cat: {self.categoria}"

    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia de Libro a partir de un diccionario proveniente de la base de datos."""
        if not data:
            return None
        return cls(
            isbn=data.get('isbn'),
            titulo=data.get('titulo'),
            autor=data.get('autor'),
            anio_publicacion=data.get('anio_publicacion'),
            cantidad_disponible=data.get('cantidad_disponible'),
            categoria=data.get('categoria', 'Sin Categoría')
        )
