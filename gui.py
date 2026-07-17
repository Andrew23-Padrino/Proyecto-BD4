import flet as ft
import re
import datetime
from services.libro_service import LibroService
from services.usuario_service import UsuarioService
from services.prestamo_service import PrestamoService
from services.exceptions import BibliotecaError
from models.libro import Libro
from models.usuario import Usuario

def main(page: ft.Page):
    page.title = "Sistema de Gestión de Biblioteca"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    
    # -------------------------------------------------------------
    # VARIABLES DE ESTADO Y PALETA DE COLORES
    # -------------------------------------------------------------
    # Paleta Tailwind/Shadcn
    COLORS = {
        "dark": {
            "bg": "#0f172a",          # slate-900
            "sidebar": "#1e293b",     # slate-800
            "card": "#1e293b",        # slate-800
            "text": "#f8fafc",        # slate-50
            "text_muted": "#94a3b8",  # slate-400
            "border": "#334155",      # slate-700
            "accent": "#3b82f6",      # blue-500
            "success": "#10b981",     # emerald-500
            "danger": "#f43f5e",      # rose-500
            "warning": "#f59e0b"      # amber-500
        },
        "light": {
            "bg": "#f8fafc",          # slate-50
            "sidebar": "#f1f5f9",     # slate-100
            "card": "#ffffff",
            "text": "#0f172a",        # slate-900
            "text_muted": "#64748b",  # slate-500
            "border": "#e2e8f0",      # slate-200
            "accent": "#2563eb",      # blue-600
            "success": "#059669",     # emerald-600
            "danger": "#e11d48",      # rose-600
            "warning": "#d97706"      # amber-600
        }
    }

    # Estado actual
    state = {
        "vista_actual": "dashboard",  # dashboard, libros, usuarios, prestamos
        "is_db_connected": False,
        "books_list": [],
        "users_list": [],
        "active_loans": [],
        "all_loans": []
    }

    # -------------------------------------------------------------
    # COMPONENTES COMUNES Y MÉTODOS DE RETROALIMENTACIÓN
    # -------------------------------------------------------------
    # Spinner de Carga General
    spinner = ft.ProgressRing(width=20, height=20, stroke_width=2.5, visible=False, color="#3b82f6")
    
    def get_color(key: str) -> str:
        mode = "dark" if page.theme_mode == ft.ThemeMode.DARK else "light"
        return COLORS[mode][key]

    def show_toast(message: str, is_error: bool = False, is_warning: bool = False):
        bg_color = get_color("danger") if is_error else (get_color("warning") if is_warning else get_color("success"))
        text_color = "#ffffff"
        
        snack = ft.SnackBar(
            content=ft.Text(message, color=text_color, weight=ft.FontWeight.W_500),
            bgcolor=bg_color,
            duration=4000,
            action="Cerrar",
            action_color="#ffffff"
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def set_loading(loading: bool):
        spinner.visible = loading
        page.update()

    # -------------------------------------------------------------
    # MÉTODOS DE ACCESO A DATOS (CONEXIÓN A SERVICES)
    # -------------------------------------------------------------
    def verificar_conexion() -> bool:
        try:
            # Intentar listar libros de forma rápida para validar conexión
            LibroService.listar_todos()
            state["is_db_connected"] = True
            return True
        except Exception as e:
            state["is_db_connected"] = False
            return False

    def cargar_datos():
        if not state["is_db_connected"]:
            if not verificar_conexion():
                return
        
        try:
            state["books_list"] = LibroService.listar_todos()
            state["users_list"] = UsuarioService.listar_todos()
            state["active_loans"] = PrestamoService.listar_prestamos(solo_activos=True)
            state["all_loans"] = PrestamoService.listar_prestamos(solo_activos=False)
        except Exception as e:
            show_toast(f"Error al sincronizar datos: {str(e)}", is_error=True)

    # -------------------------------------------------------------
    # DIÁLOGOS Y FORMULARIOS (MODALES)
    # -------------------------------------------------------------
    
    # --- MODAL: AGREGAR LIBRO ---
    def guardar_libro(e):
        # Limpiar errores visuales previos
        isbn_input.error_text = None
        titulo_input.error_text = None
        autor_input.error_text = None
        anio_input.error_text = None
        cantidad_input.error_text = None
        
        # Validaciones
        valido = True
        isbn = isbn_input.value.strip()
        titulo = titulo_input.value.strip()
        autor = autor_input.value.strip()
        categoria = categoria_input.value.strip() or "Sin Categoría"
        
        if not isbn:
            isbn_input.error_text = "El ISBN es requerido"
            valido = False
        if not titulo:
            titulo_input.error_text = "El título es requerido"
            valido = False
        if not autor:
            autor_input.error_text = "El autor es requerido"
            valido = False
            
        anio = 0
        try:
            anio = int(anio_input.value.strip())
            current_year = datetime.datetime.now().year
            if anio <= 0:
                anio_input.error_text = "El año debe ser mayor a 0"
                valido = False
            elif anio > current_year:
                anio_input.error_text = f"No puede superar el año actual ({current_year})"
                valido = False
        except ValueError:
            anio_input.error_text = "Debe ser un número entero"
            valido = False

        cantidad = 0
        try:
            cantidad = int(cantidad_input.value.strip())
            if cantidad < 0:
                cantidad_input.error_text = "La cantidad no puede ser negativa"
                valido = False
        except ValueError:
            cantidad_input.error_text = "Debe ser un número entero"
            valido = False
            
        if not valido:
            page.update()
            return
            
        set_loading(True)
        try:
            nuevo_l = Libro(isbn, titulo, autor, anio, cantidad, categoria)
            LibroService.registrar_libro(nuevo_l)
            show_toast(f"Libro '{titulo}' registrado con éxito.")
            modal_libro.open = False
            # Limpiar campos
            isbn_input.value = ""
            titulo_input.value = ""
            autor_input.value = ""
            anio_input.value = ""
            cantidad_input.value = ""
            categoria_input.value = ""
            
            cargar_datos()
            navegar_a("libros")
        except BibliotecaError as ex:
            show_toast(str(ex), is_error=True)
        except Exception as ex:
            show_toast(f"Error inesperado: {str(ex)}", is_error=True)
        finally:
            set_loading(False)

    isbn_input = ft.TextField(label="ISBN (ej: 978-3-16-148410-0)", border_color="#3b82f6")
    titulo_input = ft.TextField(label="Título del Libro", border_color="#3b82f6")
    autor_input = ft.TextField(label="Autor", border_color="#3b82f6")
    anio_input = ft.TextField(label="Año de Publicación", value=str(datetime.datetime.now().year), border_color="#3b82f6")
    cantidad_input = ft.TextField(label="Cantidad Disponible", value="1", border_color="#3b82f6")
    categoria_input = ft.TextField(label="Categoría (Opcional)", border_color="#3b82f6")

    modal_libro = ft.AlertDialog(
        title=ft.Text("Registrar Nuevo Libro", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    isbn_input,
                    titulo_input,
                    autor_input,
                    ft.Row([anio_input, cantidad_input], spacing=10),
                    categoria_input
                ],
                tight=True,
                spacing=15
            ),
            width=450
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: setattr(modal_libro, "open", False) or page.update()),
            ft.ElevatedButton("Guardar", on_click=guardar_libro, bgcolor="#3b82f6", color="#ffffff")
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.overlay.append(modal_libro)


    # --- MODAL: REGISTRAR USUARIO ---
    def validar_formato_correo(correo: str) -> bool:
        return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", correo))

    def on_correo_change(e):
        correo = correo_input.value.strip()
        if not correo:
            correo_indicator.value = "Pendiente de ingreso"
            correo_indicator.color = get_color("text_muted")
        elif validar_formato_correo(correo):
            correo_indicator.value = "✓ Formato de correo válido"
            correo_indicator.color = get_color("success")
        else:
            correo_indicator.value = "✗ Formato inválido (debe contener @ y .)"
            correo_indicator.color = get_color("danger")
        page.update()

    def guardar_usuario(e):
        nombre = nombre_input.value.strip()
        correo = correo_input.value.strip()
        
        nombre_input.error_text = None
        correo_input.error_text = None
        
        valido = True
        if not nombre:
            nombre_input.error_text = "El nombre es requerido"
            valido = False
        if not correo:
            correo_input.error_text = "El correo es requerido"
            valido = False
        elif not validar_formato_correo(correo):
            correo_input.error_text = "El formato del correo es inválido"
            valido = False
            
        if not valido:
            page.update()
            return
            
        set_loading(True)
        try:
            nuevo_u = Usuario(nombre, correo)
            nuevo_id = UsuarioService.registrar_usuario(nuevo_u)
            show_toast(f"Miembro '{nombre}' registrado con éxito. ID asignado: {nuevo_id}")
            modal_usuario.open = False
            nombre_input.value = ""
            correo_input.value = ""
            correo_indicator.value = "Pendiente de ingreso"
            correo_indicator.color = get_color("text_muted")
            
            cargar_datos()
            navegar_a("usuarios")
        except BibliotecaError as ex:
            show_toast(str(ex), is_error=True)
        except Exception as ex:
            show_toast(f"Error inesperado: {str(ex)}", is_error=True)
        finally:
            set_loading(False)

    nombre_input = ft.TextField(label="Nombre Completo", border_color="#10b981")
    correo_input = ft.TextField(label="Correo Electrónico", border_color="#10b981", on_change=on_correo_change)
    correo_indicator = ft.Text("Pendiente de ingreso", size=12, color=get_color("text_muted"), italic=True)

    modal_usuario = ft.AlertDialog(
        title=ft.Text("Registrar Nuevo Miembro", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    nombre_input,
                    correo_input,
                    correo_indicator
                ],
                tight=True,
                spacing=10
            ),
            width=400
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: setattr(modal_usuario, "open", False) or page.update()),
            ft.ElevatedButton("Registrar", on_click=guardar_usuario, bgcolor="#10b981", color="#ffffff")
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.overlay.append(modal_usuario)


    # --- MODAL: REGISTRAR PRÉSTAMO ---
    def guardar_prestamo(e):
        if not select_usuario.value:
            show_toast("Debe seleccionar un usuario.", is_warning=True)
            return
        if not select_libro.value:
            show_toast("Debe seleccionar un libro.", is_warning=True)
            return
            
        id_usuario = int(select_usuario.value)
        isbn = select_libro.value
        
        dias = 7
        try:
            if select_dias.value:
                dias = int(select_dias.value)
                if dias <= 0:
                    show_toast("La duración debe ser de al menos 1 día.", is_warning=True)
                    return
        except ValueError:
            show_toast("La duración debe ser un número entero.", is_warning=True)
            return
            
        set_loading(True)
        try:
            id_prestamo = PrestamoService.registrar_prestamo(id_usuario, isbn, dias)
            show_toast(f"Préstamo #{id_prestamo} registrado con éxito.")
            modal_prestamo.open = False
            
            cargar_datos()
            navegar_a("prestamos")
        except BibliotecaError as ex:
            # Aquí se atrapan errores de negocio como SinStockError o UsuarioNoEncontradoError
            # Se muestran directamente en un Toast/SnackBar dinámico
            show_toast(str(ex), is_error=True)
        except Exception as ex:
            show_toast(f"Error inesperado: {str(ex)}", is_error=True)
        finally:
            set_loading(False)

    select_usuario = ft.Dropdown(label="Seleccionar Miembro (ID - Nombre)", border_color="#3b82f6")
    select_libro = ft.Dropdown(label="Seleccionar Libro con Stock (ISBN - Título)", border_color="#3b82f6")
    select_dias = ft.TextField(label="Duración (Días)", value="7", width=120, border_color="#3b82f6")

    modal_prestamo = ft.AlertDialog(
        title=ft.Text("Registrar Préstamo de Libro", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    select_usuario,
                    select_libro,
                    select_dias
                ],
                tight=True,
                spacing=15
            ),
            width=450
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: setattr(modal_prestamo, "open", False) or page.update()),
            ft.ElevatedButton("Crear Préstamo", on_click=guardar_prestamo, bgcolor="#3b82f6", color="#ffffff")
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.overlay.append(modal_prestamo)

    def abrir_modal_prestamo(e):
        # Poblar Dropdowns dinámicamente con los datos de BD frescos
        cargar_datos()
        
        select_usuario.options = [
            ft.dropdown.Option(str(u.id), f"ID {u.id}: {u.nombre} ({u.correo})")
            for u in state["users_list"]
        ]
        
        select_libro.options = [
            ft.dropdown.Option(l.isbn, f"{l.titulo} (Stock: {l.cantidad_disponible})")
            for l in state["books_list"] if l.cantidad_disponible > 0
        ]
        
        if not select_usuario.options:
            show_toast("No hay usuarios registrados en el sistema.", is_warning=True)
            return
        if not select_libro.options:
            show_toast("No hay libros disponibles con stock en este momento.", is_warning=True)
            return
            
        select_usuario.value = select_usuario.options[0].key
        select_libro.value = select_libro.options[0].key
        select_dias.value = "7"
        
        modal_prestamo.open = True
        page.update()


    # -------------------------------------------------------------
    # CONSTRUCCIÓN DE VISTAS DINÁMICAS (CONTENIDOS)
    # -------------------------------------------------------------
    main_content_area = ft.Container(expand=True, padding=25)

    # --- 1. DASHBOARD VIEW ---
    def get_dashboard_view() -> ft.Control:
        tot_libros = len(state["books_list"])
        stock_total = sum(l.cantidad_disponible for l in state["books_list"])
        tot_usuarios = len(state["users_list"])
        prest_activos = len(state["active_loans"])
        
        # Tarjetas de Métricas
        def metric_card(title: str, val: str, icon: str, color: str, subtext: str):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            [
                                ft.Text(title, color=get_color("text_muted"), size=14, weight=ft.FontWeight.W_500),
                                ft.Icon(name=icon, color=color, size=24)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(val, size=32, weight=ft.FontWeight.BOLD, color=get_color("text")),
                        ft.Text(subtext, color=get_color("text_muted"), size=12)
                    ],
                    spacing=5
                ),
                bgcolor=get_color("card"),
                border=ft.border.all(1, get_color("border")),
                border_radius=12,
                padding=20,
                expand=True,
                shadow=ft.BoxShadow(blur_radius=8, color="#0000000a"),
                animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
            )

        metrics_grid = ft.ResponsiveRow(
            controls=[
                ft.Column([metric_card("Catálogo de Libros", str(tot_libros), ft.Icons.BOOKMARK_ROUNDED, get_color("accent"), "Títulos registrados")], col={"sm": 12, "md": 6, "lg": 3}),
                ft.Column([metric_card("Stock Disponible", str(stock_total), ft.Icons.INVENTORY_ROUNDED, get_color("success"), "Ejemplares físicos")], col={"sm": 12, "md": 6, "lg": 3}),
                ft.Column([metric_card("Miembros Activos", str(tot_usuarios), ft.Icons.PEOPLE_ALT_ROUNDED, get_color("warning"), "Usuarios en biblioteca")], col={"sm": 12, "md": 6, "lg": 3}),
                ft.Column([metric_card("Préstamos Pendientes", str(prest_activos), ft.Icons.AUTORENEW_ROUNDED, get_color("danger"), "Libros fuera de sala")], col={"sm": 12, "md": 6, "lg": 3})
            ],
            spacing=20
        )
        
        # Lista de actividad reciente (últimos 5 préstamos registrados)
        recent_loans = state["all_loans"][:5]
        activity_controls = []
        if not recent_loans:
            activity_controls.append(
                ft.Container(
                    content=ft.Text("No hay actividad de préstamos registrada.", color=get_color("text_muted"), italic=True),
                    padding=15
                )
            )
        else:
            for pl in recent_loans:
                status_color = get_color("danger") if pl['estado'] == 'Activo' else get_color("success")
                f_prest = pl['fecha_prestamo'].strftime('%Y-%m-%d') if pl['fecha_prestamo'] else 'N/A'
                activity_controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row([
                                    ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color=get_color("accent"), size=16),
                                    ft.Text(f"{pl['nombre_usuario']} solicitó '{pl['titulo_libro']}'", weight=ft.FontWeight.W_500, color=get_color("text")),
                                ]),
                                ft.Row([
                                    ft.Text(f"Préstamo: {f_prest}", size=12, color=get_color("text_muted")),
                                    ft.Container(
                                        content=ft.Text(pl['estado'], color="#ffffff", size=10, weight=ft.FontWeight.BOLD),
                                        bgcolor=status_color,
                                        border_radius=12,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=3)
                                    )
                                ], spacing=15)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        border=ft.border.only(bottom=ft.BorderSide(1, get_color("border"))),
                        padding=ft.padding.only(bottom=12, top=4)
                    )
                )
        
        activity_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Actividad Reciente (Últimas Transacciones)", size=18, weight=ft.FontWeight.BOLD, color=get_color("text")),
                    ft.Divider(color=get_color("border")),
                    ft.Column(activity_controls, spacing=10)
                ],
                spacing=10
            ),
            bgcolor=get_color("card"),
            border=ft.border.all(1, get_color("border")),
            border_radius=12,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=8, color="#0000000a"),
            margin=ft.margin.only(top=25)
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Dashboard de Control", size=26, weight=ft.FontWeight.BOLD, color=get_color("text")),
                            ft.Text("Resumen general del estado e inventario de la biblioteca.", color=get_color("text_muted"), size=14)
                        ]),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH_ROUNDED,
                            icon_color=get_color("accent"),
                            on_click=lambda _: [cargar_datos(), navegar_a("dashboard")],
                            tooltip="Sincronizar datos"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color="transparent", height=15),
                metrics_grid,
                activity_panel
            ],
            scroll=ft.ScrollMode.AUTO
        )


    # --- 2. LIBROS VIEW ---
    txt_buscar_libro = ft.TextField(
        hint_text="Buscar libro por título, autor o categoría...",
        expand=True,
        border_radius=8,
        border_color="#3b82f6",
        prefix_icon=ft.Icons.SEARCH,
        content_padding=12
    )

    def on_search_libro_change(e):
        query = txt_buscar_libro.value.strip().lower()
        if not query:
            # Restaurar lista completa
            cargar_datos()
            navegar_a("libros")
            return
            
        try:
            # Usar servicio de búsqueda
            coincidencias = LibroService.buscar_libros(query)
            # Re-renderizar tabla de libros filtrados
            dt_libros.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(l.isbn, weight=ft.FontWeight.W_500, color=get_color("text"))),
                        ft.DataCell(ft.Text(l.titulo, weight=ft.FontWeight.BOLD, color=get_color("text"))),
                        ft.DataCell(ft.Text(l.autor, color=get_color("text"))),
                        ft.DataCell(ft.Text(str(l.anio_publicacion), color=get_color("text"))),
                        ft.DataCell(ft.Text(str(l.cantidad_disponible), weight=ft.FontWeight.BOLD, color=get_color("success") if l.cantidad_disponible > 0 else get_color("danger"))),
                        ft.DataCell(ft.Text(l.categoria, color=get_color("text"))),
                    ]
                ) for l in coincidencias
            ]
            page.update()
        except Exception as ex:
            show_toast(f"Error en búsqueda: {str(ex)}", is_error=True)

    txt_buscar_libro.on_change = on_search_libro_change
    dt_libros = ft.DataTable(
        border_radius=10,
        heading_row_color=ft.colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ISBN", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Título", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Autor", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Año", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Stock", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Categoría", weight=ft.FontWeight.BOLD)),
        ]
    )

    def get_libros_view() -> ft.Control:
        # Poblar filas de la tabla
        dt_libros.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(l.isbn, weight=ft.FontWeight.W_500, color=get_color("text"))),
                    ft.DataCell(ft.Text(l.titulo, weight=ft.FontWeight.BOLD, color=get_color("text"))),
                    ft.DataCell(ft.Text(l.autor, color=get_color("text"))),
                    ft.DataCell(ft.Text(str(l.anio_publicacion), color=get_color("text"))),
                    ft.DataCell(ft.Text(str(l.cantidad_disponible), weight=ft.FontWeight.BOLD, color=get_color("success") if l.cantidad_disponible > 0 else get_color("danger"))),
                    ft.DataCell(ft.Text(l.categoria, color=get_color("text"))),
                ]
            ) for l in state["books_list"]
        ]
        
        # Envoltura scrollable para la tabla
        table_container = ft.Container(
            content=ft.ListView(
                [
                    ft.Row([dt_libros], scroll=ft.ScrollMode.ALWAYS)
                ],
                expand=True
            ),
            border=ft.border.all(1, get_color("border")),
            border_radius=10,
            bgcolor=get_color("card"),
            padding=15,
            expand=True
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Catálogo de Libros", size=26, weight=ft.FontWeight.BOLD, color=get_color("text")),
                            ft.Text("Gestión, filtros y carga de títulos en el sistema.", color=get_color("text_muted"), size=14)
                        ]),
                        ft.ElevatedButton(
                            "Agregar Libro",
                            icon=ft.Icons.ADD,
                            on_click=lambda _: setattr(modal_libro, "open", True) or page.update(),
                            bgcolor="#3b82f6",
                            color="#ffffff"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color="transparent", height=15),
                ft.Row([txt_buscar_libro]),
                ft.Divider(color="transparent", height=10),
                table_container
            ],
            expand=True
        )


    # --- 3. USUARIOS VIEW ---
    txt_buscar_usuario = ft.TextField(
        hint_text="Buscar usuario por nombre o correo...",
        expand=True,
        border_radius=8,
        border_color="#10b981",
        prefix_icon=ft.Icons.SEARCH,
        content_padding=12
    )

    def on_search_usuario_change(e):
        query = txt_buscar_usuario.value.strip().lower()
        if not query:
            cargar_datos()
            navegar_a("usuarios")
            return
            
        coincidencias = [
            u for u in state["users_list"]
            if query in u.nombre.lower() or query in u.correo.lower()
        ]
        
        dt_usuarios.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(u.id), weight=ft.FontWeight.W_500, color=get_color("text"))),
                    ft.DataCell(ft.Text(u.nombre, weight=ft.FontWeight.BOLD, color=get_color("text"))),
                    ft.DataCell(ft.Text(u.correo, color=get_color("text"))),
                    ft.DataCell(ft.Text(u.fecha_registro.strftime('%Y-%m-%d %H:%M') if u.fecha_registro else 'Pendiente', color=get_color("text")))
                ]
            ) for u in coincidencias
        ]
        page.update()

    txt_buscar_usuario.on_change = on_search_usuario_change
    dt_usuarios = ft.DataTable(
        border_radius=10,
        heading_row_color=ft.colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Correo Electrónico", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha de Registro", weight=ft.FontWeight.BOLD)),
        ]
    )

    def get_usuarios_view() -> ft.Control:
        dt_usuarios.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(u.id), weight=ft.FontWeight.W_500, color=get_color("text"))),
                    ft.DataCell(ft.Text(u.nombre, weight=ft.FontWeight.BOLD, color=get_color("text"))),
                    ft.DataCell(ft.Text(u.correo, color=get_color("text"))),
                    ft.DataCell(ft.Text(u.fecha_registro.strftime('%Y-%m-%d %H:%M') if u.fecha_registro else 'Pendiente', color=get_color("text")))
                ]
            ) for u in state["users_list"]
        ]
        
        table_container = ft.Container(
            content=ft.ListView(
                [
                    ft.Row([dt_usuarios], scroll=ft.ScrollMode.ALWAYS)
                ],
                expand=True
            ),
            border=ft.border.all(1, get_color("border")),
            border_radius=10,
            bgcolor=get_color("card"),
            padding=15,
            expand=True
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Miembros de la Biblioteca", size=26, weight=ft.FontWeight.BOLD, color=get_color("text")),
                            ft.Text("Gestión y alta de miembros afiliados al sistema de préstamos.", color=get_color("text_muted"), size=14)
                        ]),
                        ft.ElevatedButton(
                            "Nuevo Miembro",
                            icon=ft.Icons.PERSON_ADD_ROUNDED,
                            on_click=lambda _: setattr(modal_usuario, "open", True) or page.update(),
                            bgcolor="#10b981",
                            color="#ffffff"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color="transparent", height=15),
                ft.Row([txt_buscar_usuario]),
                ft.Divider(color="transparent", height=10),
                table_container
            ],
            expand=True
        )


    # --- 4. PRESTAMOS (TRANSACCIONES) VIEW ---
    def ejecutar_devolucion(id_prestamo: int):
        set_loading(True)
        try:
            PrestamoService.registrar_devolucion(id_prestamo)
            show_toast(f"Devolución del préstamo #{id_prestamo} registrada con éxito.")
            cargar_datos()
            navegar_a("prestamos")
        except BibliotecaError as ex:
            show_toast(str(ex), is_error=True)
        except Exception as ex:
            show_toast(f"Error inesperado: {str(ex)}", is_error=True)
        finally:
            set_loading(False)

    dt_prestamos_activos = ft.DataTable(
        border_radius=10,
        heading_row_color=ft.colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Miembro", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Libro / Título", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("ISBN", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("F. Préstamo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("F. Vencimiento", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ]
    )

    dt_prestamos_historico = ft.DataTable(
        border_radius=10,
        heading_row_color=ft.colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Miembro", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Libro / Título", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("ISBN", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("F. Préstamo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("F. Vencimiento", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
        ]
    )

    def get_prestamos_view() -> ft.Control:
        # Activos
        dt_prestamos_activos.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(p['id']), weight=ft.FontWeight.W_500, color=get_color("text"))),
                    ft.DataCell(ft.Text(p['nombre_usuario'], color=get_color("text"))),
                    ft.DataCell(ft.Text(p['titulo_libro'], weight=ft.FontWeight.BOLD, color=get_color("text"))),
                    ft.DataCell(ft.Text(p['isbn'], color=get_color("text"))),
                    ft.DataCell(ft.Text(p['fecha_prestamo'].strftime('%Y-%m-%d') if p['fecha_prestamo'] else 'N/A', color=get_color("text"))),
                    ft.DataCell(ft.Text(p['fecha_devolucion_esperada'].strftime('%Y-%m-%d') if p['fecha_devolucion_esperada'] else 'N/A', color=get_color("text"))),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Devolver",
                            icon=ft.Icons.KEYBOARD_RETURN_ROUNDED,
                            bgcolor=get_color("success"),
                            color="#ffffff",
                            small=True,
                            on_click=lambda e, pid=p['id']: ejecutar_devolucion(pid)
                        )
                    )
                ]
            ) for p in state["active_loans"]
        ]
        
        # Historial Completo
        dt_prestamos_historico.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(p['id']), weight=ft.FontWeight.W_500, color=get_color("text"))),
                    ft.DataCell(ft.Text(p['nombre_usuario'], color=get_color("text"))),
                    ft.DataCell(ft.Text(p['titulo_libro'], weight=ft.FontWeight.BOLD, color=get_color("text"))),
                    ft.DataCell(ft.Text(p['isbn'], color=get_color("text"))),
                    ft.DataCell(ft.Text(p['fecha_prestamo'].strftime('%Y-%m-%d') if p['fecha_prestamo'] else 'N/A', color=get_color("text"))),
                    ft.DataCell(ft.Text(p['fecha_devolucion_esperada'].strftime('%Y-%m-%d') if p['fecha_devolucion_esperada'] else 'N/A', color=get_color("text"))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(p['estado'], color="#ffffff", size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=get_color("success") if p['estado'] == 'Devuelto' else get_color("danger"),
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4)
                        )
                    )
                ]
            ) for p in state["all_loans"]
        ]

        tab_activos = ft.Container(
            content=ft.ListView(
                [ft.Row([dt_prestamos_activos], scroll=ft.ScrollMode.ALWAYS)],
                expand=True
            ),
            padding=15,
            expand=True
        )

        tab_historico = ft.Container(
            content=ft.ListView(
                [ft.Row([dt_prestamos_historico], scroll=ft.ScrollMode.ALWAYS)],
                expand=True
            ),
            padding=15,
            expand=True
        )

        tabs_prestamos = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Préstamos Activos", content=tab_activos),
                ft.Tab(text="Historial Completo", content=tab_historico)
            ],
            expand=True
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Registro de Préstamos y Devoluciones", size=26, weight=ft.FontWeight.BOLD, color=get_color("text")),
                            ft.Text("Visualice préstamos activos, registre devoluciones o cree nuevas transacciones.", color=get_color("text_muted"), size=14)
                        ]),
                        ft.ElevatedButton(
                            "Nuevo Préstamo",
                            icon=ft.Icons.SEND_ROUNDED,
                            on_click=abrir_modal_prestamo,
                            bgcolor="#3b82f6",
                            color="#ffffff"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color="transparent", height=15),
                tabs_prestamos
            ],
            expand=True
        )


    # -------------------------------------------------------------
    # CONTROLADOR DE RUTAS/NAVEGACIÓN INTERNA
    # -------------------------------------------------------------
    def navegar_a(vista: str):
        state["vista_actual"] = vista
        
        # Actualizar Sidebar visualmente
        btn_dash.bgcolor = "transparent"
        btn_books.bgcolor = "transparent"
        btn_users.bgcolor = "transparent"
        btn_loans.bgcolor = "transparent"
        
        # Resaltar botón activo
        active_btn = None
        if vista == "dashboard":
            active_btn = btn_dash
            main_content_area.content = get_dashboard_view()
        elif vista == "libros":
            active_btn = btn_books
            main_content_area.content = get_libros_view()
        elif vista == "usuarios":
            active_btn = btn_users
            main_content_area.content = get_usuarios_view()
        elif vista == "prestamos":
            active_btn = btn_loans
            main_content_area.content = get_prestamos_view()
            
        if active_btn:
            active_btn.bgcolor = "#ffffff1c" if page.theme_mode == ft.ThemeMode.DARK else "#00000014"
            
        page.update()

    # -------------------------------------------------------------
    # SIDEBAR DE NAVEGACIÓN
    # -------------------------------------------------------------
    def cambiar_tema(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        # Actualizar colores
        page.bgcolor = get_color("bg")
        sidebar_container.bgcolor = get_color("sidebar")
        btn_theme.icon = ft.Icons.LIGHT_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE_ROUNDED
        btn_theme.tooltip = "Cambiar a Modo Claro" if page.theme_mode == ft.ThemeMode.DARK else "Cambiar a Modo Oscuro"
        
        # Refrescar vista actual para aplicar la paleta
        navegar_a(state["vista_actual"])
        
    def crear_btn_sidebar(text: str, icon: str, action):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=get_color("accent"), size=20),
                    ft.Text(text, size=15, weight=ft.FontWeight.W_500, color=get_color("text"))
                ],
                spacing=12
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=8,
            on_click=action,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

    btn_dash = crear_btn_sidebar("Dashboard", ft.Icons.DASHBOARD_ROUNDED, lambda _: navegar_a("dashboard"))
    btn_books = crear_btn_sidebar("Libros / Catálogo", ft.Icons.BOOK_ROUNDED, lambda _: navegar_a("libros"))
    btn_users = crear_btn_sidebar("Usuarios / Miembros", ft.Icons.PEOPLE_ROUNDED, lambda _: navegar_a("usuarios"))
    btn_loans = crear_btn_sidebar("Préstamos y Devolución", ft.Icons.SWAP_HORIZ_ROUNDED, lambda _: navegar_a("prestamos"))
    
    btn_theme = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE_ROUNDED,
        icon_color=get_color("accent"),
        on_click=cambiar_tema,
        tooltip="Cambiar a Modo Claro"
    )

    db_indicator_dot = ft.Container(width=10, height=10, border_radius=5, bgcolor=get_color("danger"))
    db_indicator_text = ft.Text("Desconectado de MySQL", size=12, color=get_color("text_muted"))

    sidebar_container = ft.Container(
        content=ft.Column(
            controls=[
                # Título de Cabecera
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LIBRARY_BOOKS_ROUNDED, color="#3b82f6", size=30),
                            ft.Text("MiBiblioteca", size=22, weight=ft.FontWeight.BOLD, color=get_color("text"))
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    padding=ft.padding.symmetric(vertical=20)
                ),
                ft.Divider(color=get_color("border")),
                # Botones de Navegación
                ft.Column(
                    [btn_dash, btn_books, btn_users, btn_loans],
                    spacing=8,
                    expand=True
                ),
                ft.Divider(color=get_color("border")),
                # Indicador de base de datos
                ft.Row(
                    [
                        db_indicator_dot,
                        db_indicator_text,
                        spinner
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=8
                ),
                # Botón de Tema y Footer
                ft.Row(
                    [
                        btn_theme,
                        ft.Text("v1.0.0 Pro", size=12, color=get_color("text_muted"))
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ],
            spacing=10
        ),
        width=260,
        bgcolor=get_color("sidebar"),
        border=ft.border.only(right=ft.BorderSide(1, get_color("border"))),
        padding=15
    )

    # -------------------------------------------------------------
    # CONTROLADOR DE CONEXIÓN AL INICIAR
    # -------------------------------------------------------------
    def iniciar_conexion():
        set_loading(True)
        con_exito = verificar_conexion()
        if con_exito:
            db_indicator_dot.bgcolor = get_color("success")
            db_indicator_text.value = "Conectado a MySQL"
            cargar_datos()
            navegar_a("dashboard")
        else:
            db_indicator_dot.bgcolor = get_color("danger")
            db_indicator_text.value = "Error de Conexión"
            show_toast(
                "No se pudo establecer conexión inicial con la base de datos MySQL. Verifique config.py.",
                is_error=True
            )
            # Aún así cargamos vacíos para que no crashe
            navegar_a("dashboard")
        set_loading(False)

    # -------------------------------------------------------------
    # ENSAMBLADO GENERAL DE LA PÁGINA
    # -------------------------------------------------------------
    page.bgcolor = get_color("bg")
    page.add(
        ft.Row(
            [
                sidebar_container,
                main_content_area
            ],
            expand=True,
            spacing=0
        )
    )
    
    # Arrancar la base de datos en segundo plano
    iniciar_conexion()

# Ejecución de la aplicación
if __name__ == "__main__":
    # Inicia por defecto en modo escritorio nativo
    # Si desea levantar en navegador web local, cambie a: ft.app(target=main, view=ft.AppView.WEB_BROWSER)
    ft.app(target=main)
