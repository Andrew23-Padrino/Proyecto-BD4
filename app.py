import os
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from services.libro_service import LibroService
from services.usuario_service import UsuarioService
from services.prestamo_service import PrestamoService
from services.exceptions import BibliotecaError
from models.libro import Libro
from models.usuario import Usuario

app = FastAPI(title="Biblioteca API", description="API REST para el Sistema de Gestión de Biblioteca")

# -------------------------------------------------------------
# MODELOS DE ENTRADA (PYDANTIC SCHEMAS)
# -------------------------------------------------------------
class LibroCreate(BaseModel):
    isbn: str = Field(..., example="978-3-16-148410-0")
    titulo: str = Field(..., example="El Quijote")
    autor: str = Field(..., example="Miguel de Cervantes")
    anio_publicacion: int = Field(..., example=1605)
    cantidad_disponible: int = Field(..., gte=0, example=5)
    categoria: str = Field(default="Sin Categoría", example="Novela")

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., example="Juan Perez")
    correo: str = Field(..., example="juan@example.com")

class PrestamoCreate(BaseModel):
    id_usuario: int = Field(..., example=1)
    isbn: str = Field(..., example="978-3-16-148410-0")
    dias_prestamo: int = Field(default=7, gt=0, example=7)


# -------------------------------------------------------------
# RUTAS DE LA API (/api)
# -------------------------------------------------------------

@app.get("/api/dashboard")
def get_dashboard():
    """Retorna las métricas del sistema y últimas transacciones."""
    try:
        libros = LibroService.listar_todos()
        usuarios = UsuarioService.listar_todos()
        activos = PrestamoService.listar_prestamos(solo_activos=True)
        historico = PrestamoService.listar_prestamos(solo_activos=False)
        
        # Calcular stock total físico
        stock_total = sum(l.cantidad_disponible for l in libros)
        
        # Formatear la actividad reciente (últimos 5 préstamos registrados)
        actividad = []
        for p in historico[:5]:
            f_prest = p['fecha_prestamo'].strftime('%Y-%m-%d') if p['fecha_prestamo'] else 'N/A'
            actividad.append({
                "id": p["id"],
                "nombre_usuario": p["nombre_usuario"],
                "titulo_libro": p["titulo_libro"],
                "fecha_prestamo": f_prest,
                "estado": p["estado"]
            })
            
        return {
            "total_libros": len(libros),
            "stock_total": stock_total,
            "total_usuarios": len(usuarios),
            "prestamos_pendientes": len(activos),
            "actividad_reciente": actividad
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")


@app.get("/api/libros")
def get_libros(q: str = Query(None, description="Búsqueda por título, autor o categoría")):
    """Lista todos los libros o filtra por un término de búsqueda."""
    try:
        if q:
            libros = LibroService.buscar_libros(q)
        else:
            libros = LibroService.listar_todos()
            
        return [
            {
                "isbn": l.isbn,
                "titulo": l.titulo,
                "autor": l.autor,
                "anio_publicacion": l.anio_publicacion,
                "cantidad_disponible": l.cantidad_disponible,
                "categoria": l.categoria
            } for l in libros
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/libros", status_code=21)
def create_libro(libro_in: LibroCreate):
    """Registra un nuevo libro en el catálogo."""
    try:
        nuevo_l = Libro(
            isbn=libro_in.isbn,
            titulo=libro_in.titulo,
            autor=libro_in.autor,
            anio_publicacion=libro_in.anio_publicacion,
            cantidad_disponible=libro_in.cantidad_disponible,
            categoria=libro_in.categoria
        )
        LibroService.registrar_libro(nuevo_l)
        return {"status": "ok", "message": "Libro registrado con éxito"}
    except BibliotecaError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/usuarios")
def get_usuarios():
    """Lista todos los miembros de la biblioteca."""
    try:
        usuarios = UsuarioService.listar_todos()
        return [
            {
                "id": u.id,
                "nombre": u.nombre,
                "correo": u.correo,
                "fecha_registro": u.fecha_registro.strftime('%Y-%m-%d %H:%M') if u.fecha_registro else 'Pendiente'
            } for u in usuarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/usuarios", status_code=21)
def create_usuario(usuario_in: UsuarioCreate):
    """Registra un nuevo miembro."""
    try:
        nuevo_u = Usuario(nombre=usuario_in.nombre, correo=usuario_in.correo)
        nuevo_id = UsuarioService.registrar_usuario(nuevo_u)
        return {"status": "ok", "id": nuevo_id, "message": "Usuario registrado con éxito"}
    except BibliotecaError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prestamos")
def get_prestamos(solo_activos: bool = False):
    """Retorna el listado de préstamos activos o históricos."""
    try:
        prestamos = PrestamoService.listar_prestamos(solo_activos=solo_activos)
        result = []
        for p in prestamos:
            f_prest = p['fecha_prestamo'].strftime('%Y-%m-%d') if p['fecha_prestamo'] else 'N/A'
            f_venc = p['fecha_devolucion_esperada'].strftime('%Y-%m-%d') if p['fecha_devolucion_esperada'] else 'N/A'
            result.append({
                "id": p["id"],
                "id_usuario": p["id_usuario"],
                "nombre_usuario": p["nombre_usuario"],
                "isbn": p["isbn"],
                "titulo_libro": p["titulo_libro"],
                "fecha_prestamo": f_prest,
                "fecha_devolucion_esperada": f_venc,
                "estado": p["estado"]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prestamos", status_code=21)
def create_prestamo(prestamo_in: PrestamoCreate):
    """Registra una solicitud de préstamo de libro."""
    try:
        id_prestamo = PrestamoService.registrar_prestamo(
            id_usuario=prestamo_in.id_usuario,
            isbn=prestamo_in.isbn,
            dias_prestamo=prestamo_in.dias_prestamo
        )
        return {"status": "ok", "id": id_prestamo, "message": "Préstamo registrado con éxito"}
    except BibliotecaError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prestamos/devolver/{id_prestamo}")
def devolver_prestamo(id_prestamo: int):
    """Registra la devolución de un libro prestado."""
    try:
        PrestamoService.registrar_devolucion(id_prestamo)
        return {"status": "ok", "message": "Devolución registrada con éxito, stock actualizado"}
    except BibliotecaError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# MONTAJE DEL FRONTEND ESTATICO
# -------------------------------------------------------------
# Asegurar que existe la carpeta frontend para evitar fallos de montaje
if not os.path.exists("frontend"):
    os.makedirs("frontend")

# Servir index.html y assets estáticos
# Esta línea se monta al final para que no tape las rutas de la API (/api)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


# Ejecutar el servidor Uvicorn si se corre el archivo directamente
if __name__ == "__main__":
    print("Iniciando Servidor Web en http://127.0.0.1:8000")
    uvicorn.run("app.py:app", host="127.0.0.1", port=8000, reload=True)
