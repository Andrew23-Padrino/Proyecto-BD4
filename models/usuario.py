from datetime import datetime

class Usuario:
    """Clase que representa la entidad Usuario/Miembro."""
    def __init__(self, nombre: str, correo: str, id_usuario: int = None, fecha_registro: datetime = None):
        self.id = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.fecha_registro = fecha_registro

    def __str__(self):
        id_str = self.id if self.id else "Nuevo"
        fecha_str = self.fecha_registro.strftime('%Y-%m-%d %H:%M') if self.fecha_registro else "Pendiente"
        return f"Usuario [ID: {id_str}] {self.nombre} - Correo: {self.correo} (Registrado: {fecha_str})"

    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia de Usuario a partir de un diccionario proveniente de la base de datos."""
        if not data:
            return None
        return cls(
            id_usuario=data.get('id'),
            nombre=data.get('nombre'),
            correo=data.get('correo'),
            fecha_registro=data.get('fecha_registro')
        )
