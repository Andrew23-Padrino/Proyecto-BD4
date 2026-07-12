import sys
from datetime import datetime
from database import inicializar_base_de_datos
from models import Libro, Usuario
from services import (
    LibroService,
    UsuarioService,
    PrestamoService,
    BibliotecaError
)

def menu_principal():
    print("\n" + "=" * 50)
    print("        SISTEMA DE GESTIÓN DE BIBLIOTECA")
    print("=" * 50)
    print("  1. Registrar un nuevo libro")
    print("  2. Buscar libros (por título, autor o categoría)")
    print("  3. Listar todos los libros")
    print("  4. Registrar un nuevo usuario / miembro")
    print("  5. Listar todos los usuarios")
    print("  6. Registrar préstamo de un libro")
    print("  7. Registrar devolución de un libro")
    print("  8. Listar préstamos activos")
    print("  9. Ver historial completo de préstamos")
    print(" 10. Inicializar / Re-crear base de datos")
    print("  0. Salir de la aplicación")
    print("=" * 50)

def registrar_libro_cli():
    print("\n--- REGISTRAR NUEVO LIBRO ---")
    isbn = input("ISBN (ej. 978-3-16-148410-0): ").strip()
    if not isbn:
        print("[ERROR] El ISBN es obligatorio.")
        return
    
    titulo = input("Título: ").strip()
    if not titulo:
        print("[ERROR] El título es obligatorio.")
        return
        
    autor = input("Autor: ").strip()
    if not autor:
        print("[ERROR] El autor es obligatorio.")
        return
        
    try:
        anio = int(input("Año de publicación (ej. 2021): ").strip())
        cantidad = int(input("Cantidad inicial disponible en biblioteca: ").strip())
        if cantidad < 0:
            print("[ERROR] La cantidad no puede ser negativa.")
            return
    except ValueError:
        print("[ERROR] El año y la cantidad deben ser números enteros válidos.")
        return
        
    categoria = input("Categoría (dejar vacío para 'Sin Categoría'): ").strip()
    if not categoria:
        categoria = "Sin Categoría"
        
    libro = Libro(isbn, titulo, autor, anio, cantidad, categoria)
    
    try:
        LibroService.registrar_libro(libro)
        print(f"\n[ÉXITO] El libro '{titulo}' ha sido registrado con éxito.")
    except BibliotecaError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR INESPERADO] {e}")

def buscar_libros_cli():
    print("\n--- BUSCAR LIBROS ---")
    termino = input("Ingrese el título, autor o categoría a buscar: ").strip()
    if not termino:
        print("[ERROR] Debe ingresar un término de búsqueda.")
        return
        
    try:
        libros = LibroService.buscar_libros(termino)
        if not libros:
            print("\nNo se encontraron libros que coincidan con la búsqueda.")
        else:
            print(f"\nSe encontraron {len(libros)} coincidencia(s):")
            print("-" * 80)
            for idx, libro in enumerate(libros, 1):
                print(f"{idx}. {libro}")
            print("-" * 80)
    except Exception as e:
        print(f"\n[ERROR INESPERADO] No se pudo completar la búsqueda: {e}")

def listar_libros_cli():
    print("\n--- LISTADO GENERAL DE LIBROS ---")
    try:
        libros = LibroService.listar_todos()
        if not libros:
            print("No hay libros registrados en el inventario.")
        else:
            print("-" * 80)
            for libro in libros:
                print(libro)
            print("-" * 80)
    except Exception as e:
        print(f"\n[ERROR INESPERADO] No se pudo obtener el listado: {e}")

def registrar_usuario_cli():
    print("\n--- REGISTRAR NUEVO MIEMBRO ---")
    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("[ERROR] El nombre es obligatorio.")
        return
        
    correo = input("Correo electrónico único: ").strip()
    if not correo:
        print("[ERROR] El correo electrónico es obligatorio.")
        return
        
    usuario = Usuario(nombre, correo)
    try:
        nuevo_id = UsuarioService.registrar_usuario(usuario)
        print(f"\n[ÉXITO] Miembro '{nombre}' registrado. ID asignado: {nuevo_id}")
    except BibliotecaError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR INESPERADO] {e}")

def listar_usuarios_cli():
    print("\n--- LISTADO GENERAL DE MIEMBROS ---")
    try:
        usuarios = UsuarioService.listar_todos()
        if not usuarios:
            print("No hay usuarios registrados en el sistema.")
        else:
            print("-" * 80)
            for usuario in usuarios:
                print(usuario)
            print("-" * 80)
    except Exception as e:
        print(f"\n[ERROR INESPERADO] No se pudo obtener el listado de usuarios: {e}")

def registrar_prestamo_cli():
    print("\n--- REGISTRAR PRÉSTAMO DE LIBRO ---")
    try:
        id_usuario = int(input("ID del usuario (miembro): ").strip())
    except ValueError:
        print("[ERROR] El ID del usuario debe ser un número entero.")
        return
        
    isbn = input("ISBN del libro a prestar: ").strip()
    if not isbn:
        print("[ERROR] El ISBN del libro es obligatorio.")
        return
        
    try:
        dias_prestamo = input("Duración del préstamo en días (presione Enter para usar 7 días): ").strip()
        if not dias_prestamo:
            dias_prestamo = 7
        else:
            dias_prestamo = int(dias_prestamo)
            if dias_prestamo <= 0:
                print("[ERROR] La duración debe ser mayor a 0 días.")
                return
    except ValueError:
        print("[ERROR] Los días de préstamo deben ser un número entero.")
        return
        
    try:
        id_prestamo = PrestamoService.registrar_prestamo(id_usuario, isbn, dias_prestamo)
        print(f"\n[ÉXITO] Préstamo creado exitosamente con el ID: {id_prestamo}")
    except BibliotecaError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR INESPERADO] No se pudo realizar el préstamo: {e}")

def registrar_devolucion_cli():
    print("\n--- REGISTRAR DEVOLUCIÓN DE LIBRO ---")
    try:
        id_prestamo = int(input("ID del préstamo a devolver: ").strip())
    except ValueError:
        print("[ERROR] El ID del préstamo debe ser un número entero.")
        return
        
    try:
        PrestamoService.registrar_devolucion(id_prestamo)
        print(f"\n[ÉXITO] La devolución se registró correctamente. Se ha restituido 1 unidad del libro al stock.")
    except BibliotecaError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR INESPERADO] No se pudo registrar la devolución: {e}")

def listar_prestamos_cli(solo_activos=False):
    titulo = "PRÉSTAMOS ACTIVOS (PENDIENTES)" if solo_activos else "HISTORIAL COMPLETO DE PRÉSTAMOS"
    print(f"\n--- {titulo} ---")
    try:
        prestamos = PrestamoService.listar_prestamos(solo_activos)
        if not prestamos:
            print("No hay registros que mostrar.")
            return
            
        print("-" * 120)
        print(f"{'ID':<6} | {'Usuario':<25} | {'ISBN':<15} | {'Título del Libro':<35} | {'F. Préstamo':<12} | {'F. Venc.':<12} | {'Estado':<10}")
        print("-" * 120)
        for p in prestamos:
            f_prest = p['fecha_prestamo'].strftime('%Y-%m-%d') if p['fecha_prestamo'] else 'N/A'
            f_venc = p['fecha_devolucion_esperada'].strftime('%Y-%m-%d') if p['fecha_devolucion_esperada'] else 'N/A'
            
            nombre_u = p['nombre_usuario'][:23]
            titulo_l = p['titulo_libro'][:33]
            
            print(f"{p['id']:<6} | {nombre_u:<25} | {p['isbn']:<15} | {titulo_l:<35} | {f_prest:<12} | {f_venc:<12} | {p['estado']:<10}")
        print("-" * 120)
    except Exception as e:
        print(f"\n[ERROR INESPERADO] No se pudo obtener la lista de préstamos: {e}")

def main():
    print("Cargando Sistema de Gestión de Biblioteca...")
    
    # Intento inicial de conexión para validar el estado del servidor MySQL y el esquema
    try:
        from database.connection import DatabaseConnection
        with DatabaseConnection() as (conn, cursor):
            # Probar si la base de datos existe y se puede consultar
            cursor.execute("SELECT 1")
        print("[INFO] Conexión exitosa a MySQL y la base de datos.")
    except Exception:
        print("\n[ADVERTENCIA] No se pudo establecer conexión inicial con la base de datos.")
        print("Esto puede deberse a que no existe o a que el servidor MySQL no está activo.")
        inicializar = input("¿Desea intentar inicializar la base de datos ahora? (s/n): ").strip().lower()
        if inicializar == 's':
            inicializar_base_de_datos()
            
    while True:
        menu_principal()
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            registrar_libro_cli()
        elif opcion == "2":
            buscar_libros_cli()
        elif opcion == "3":
            listar_libros_cli()
        elif opcion == "4":
            registrar_usuario_cli()
        elif opcion == "5":
            listar_usuarios_cli()
        elif opcion == "6":
            registrar_prestamo_cli()
        elif opcion == "7":
            registrar_devolucion_cli()
        elif opcion == "8":
            listar_prestamos_cli(solo_activos=True)
        elif opcion == "9":
            listar_prestamos_cli(solo_activos=False)
        elif opcion == "10":
            confirmar = input("\n[ATENCIÓN] ¿Está seguro de que desea (re)inicializar la base de datos?\n"
                               "Esto eliminará todas las tablas e información existente. (s/n): ").strip().lower()
            if confirmar == 's':
                inicializar_base_de_datos()
        elif opcion == "0":
            print("\nSaliendo del sistema. ¡Que tenga un excelente día!")
            sys.exit(0)
        else:
            print("\n[ERROR] Opción no reconocida. Por favor, intente del 0 al 10.")
            
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
