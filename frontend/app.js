// API Base URL (relative as we serve frontend from the same origin)
const API_URL = "";

// Global lists to store currently fetched data (for local filtering/lookup if needed)
let booksData = [];
let usersData = [];
let activeLoansData = [];
let allLoansData = [];
let activeLoansTab = 'activos'; // 'activos' or 'historico'

// Initialize app when DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Load Saved Theme
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeToggleUI(savedTheme);

    // Initial Database Connectivity Check & Data Loading
    checkConnectionAndLoad();
});

// -------------------------------------------------------------
// CONEXIÓN Y DATOS
// -------------------------------------------------------------
async function checkConnectionAndLoad() {
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/dashboard`);
        if (response.ok) {
            document.getElementById("status-dot").className = "status-dot green";
            document.getElementById("status-text").textContent = "Conectado a MySQL";
            fetchDashboardData();
        } else {
            handleConnectionError();
        }
    } catch (error) {
        console.error("API Connection Error:", error);
        handleConnectionError();
    } finally {
        setLoading(false);
    }
}

function handleConnectionError() {
    document.getElementById("status-dot").className = "status-dot red";
    document.getElementById("status-text").textContent = "Error de Conexión";
    showToast("No se pudo establecer conexión con el backend MySQL. Verifique config.py.", "error");
}

async function fetchDashboardData() {
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/dashboard`);
        if (!response.ok) throw new Error("Fallo al obtener datos del dashboard");
        
        const data = await response.json();
        
        // Actualizar métricas
        document.getElementById("metric-libros").textContent = data.total_libros;
        document.getElementById("metric-stock").textContent = data.stock_total;
        document.getElementById("metric-usuarios").textContent = data.total_usuarios;
        document.getElementById("metric-prestamos").textContent = data.prestamos_pendientes;
        
        // Actualizar lista de actividad reciente
        const activityList = document.getElementById("activity-list");
        activityList.innerHTML = "";
        
        if (data.actividad_reciente.length === 0) {
            activityList.innerHTML = `<li class="no-activity">No hay actividad de préstamos registrada.</li>`;
        } else {
            data.actividad_reciente.forEach(act => {
                const isActivo = act.estado === "Activo";
                const badgeClass = isActivo ? "badge badge-danger" : "badge badge-success";
                
                const li = document.createElement("li");
                li.className = "activity-item";
                li.innerHTML = `
                    <div class="activity-left">
                        <i data-lucide="arrow-right" class="activity-bullet"></i>
                        <span class="activity-text"><strong>${act.nombre_usuario}</strong> solicitó "${act.titulo_libro}"</span>
                    </div>
                    <div class="activity-right">
                        <span class="activity-date">Préstamo: ${act.fecha_prestamo}</span>
                        <span class="${badgeClass}">${act.estado}</span>
                    </div>
                `;
                activityList.appendChild(li);
            });
            // Re-renderizar iconos cargados dinámicamente
            lucide.createIcons();
        }
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

// -------------------------------------------------------------
// NAVEGACIÓN Y TABS
// -------------------------------------------------------------
function switchTab(tabName) {
    // Desactivar todos los botones de la barra lateral y secciones de contenido
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".content-section").forEach(sec => sec.classList.remove("active"));
    
    // Activar seleccionado
    document.getElementById(`btn-${tabName}`).classList.add("active");
    document.getElementById(`view-${tabName}`).classList.add("active");
    
    // Cargar datos según corresponda
    if (tabName === 'dashboard') {
        fetchDashboardData();
    } else if (tabName === 'libros') {
        fetchLibros();
    } else if (tabName === 'usuarios') {
        fetchUsuarios();
    } else if (tabName === 'prestamos') {
        fetchPrestamos();
    }
}

// -------------------------------------------------------------
// GESTIÓN DE LIBROS
// -------------------------------------------------------------
async function fetchLibros(query = "") {
    setLoading(true);
    try {
        const url = query ? `${API_URL}/api/libros?q=${encodeURIComponent(query)}` : `${API_URL}/api/libros`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("Fallo al obtener libros");
        
        booksData = await response.json();
        renderLibrosTable(booksData);
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

function renderLibrosTable(books) {
    const tbody = document.getElementById("table-libros-body");
    tbody.innerHTML = "";
    
    if (books.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center italic text-muted">No se encontraron libros.</td></tr>`;
        return;
    }
    
    books.forEach(b => {
        const tr = document.createElement("tr");
        const hasStock = b.cantidad_disponible > 0;
        const stockStyle = hasStock ? "color: var(--success); font-weight: 600;" : "color: var(--danger); font-weight: 600;";
        
        tr.innerHTML = `
            <td><code>${b.isbn}</code></td>
            <td class="font-semibold">${b.titulo}</td>
            <td>${b.autor}</td>
            <td>${b.anio_publicacion}</td>
            <td style="${stockStyle}">${b.cantidad_disponible}</td>
            <td><span class="category-badge">${b.categoria}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

// Búsqueda reactiva de libros con pequeño delay (debouncing)
let searchLibroTimeout;
function filterLibros() {
    clearTimeout(searchLibroTimeout);
    const searchVal = document.getElementById("search-libro-input").value.trim();
    searchLibroTimeout = setTimeout(() => {
        fetchLibros(searchVal);
    }, 300);
}

async function submitLibro(event) {
    event.preventDefault();
    
    // Limpiar errores visuales
    document.querySelectorAll(".error-msg").forEach(span => span.textContent = "");
    
    const isbn = document.getElementById("libro-isbn").value.trim();
    const titulo = document.getElementById("libro-titulo").value.trim();
    const autor = document.getElementById("libro-autor").value.trim();
    const anio = parseInt(document.getElementById("libro-anio").value);
    const cantidad = parseInt(document.getElementById("libro-cantidad").value);
    const categoria = document.getElementById("libro-categoria").value.trim() || "Sin Categoría";
    
    let valido = true;
    const currentYear = new Date().getFullYear();
    
    if (!isbn) {
        document.getElementById("error-libro-isbn").textContent = "El ISBN es requerido.";
        valido = false;
    }
    if (!titulo) {
        document.getElementById("error-libro-titulo").textContent = "El título es requerido.";
        valido = false;
    }
    if (!autor) {
        document.getElementById("error-libro-autor").textContent = "El autor es requerido.";
        valido = false;
    }
    if (isNaN(anio) || anio <= 0) {
        document.getElementById("error-libro-anio").textContent = "El año debe ser un número mayor a 0.";
        valido = false;
    } else if (anio > currentYear) {
        document.getElementById("error-libro-anio").textContent = `El año no puede ser mayor al año actual (${currentYear}).`;
        valido = false;
    }
    if (isNaN(cantidad) || cantidad < 0) {
        document.getElementById("error-libro-cantidad").textContent = "La cantidad disponible no puede ser negativa.";
        valido = false;
    }
    
    if (!valido) return;
    
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/libros`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                isbn, titulo, autor, anio_publicacion: anio, cantidad_disponible: cantidad, categoria
            })
        });
        
        const resData = await response.json();
        if (!response.ok) {
            // Error capturado desde la lógica de negocio (ej. LibroDuplicadoError)
            throw new Error(resData.detail || "Error al guardar el libro");
        }
        
        showToast(`Libro "${titulo}" registrado con éxito.`, "success");
        closeModal("modal-libro");
        document.getElementById("form-libro").reset();
        
        // Refrescar catálogo
        fetchLibros();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

// -------------------------------------------------------------
// GESTIÓN DE USUARIOS
// -------------------------------------------------------------
async function fetchUsuarios() {
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/usuarios`);
        if (!response.ok) throw new Error("Fallo al obtener usuarios");
        
        usersData = await response.json();
        renderUsuariosTable(usersData);
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

function renderUsuariosTable(users) {
    const tbody = document.getElementById("table-usuarios-body");
    tbody.innerHTML = "";
    
    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center italic text-muted">No hay usuarios registrados.</td></tr>`;
        return;
    }
    
    users.forEach(u => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><code>${u.id}</code></td>
            <td class="font-semibold">${u.nombre}</td>
            <td>${u.correo}</td>
            <td>${u.fecha_registro}</td>
        `;
        tbody.appendChild(tr);
    });
}

function filterUsuarios() {
    const searchVal = document.getElementById("search-usuario-input").value.trim().toLowerCase();
    if (!searchVal) {
        renderUsuariosTable(usersData);
        return;
    }
    const filtered = usersData.filter(u => 
        u.nombre.toLowerCase().includes(searchVal) || u.correo.toLowerCase().includes(searchVal)
    );
    renderUsuariosTable(filtered);
}

// Validación de correo en tiempo real
function validateEmail(email) {
    return /^[^@]+@[^@]+\.[^@]+$/.test(email);
}

function validateEmailRealtime() {
    const emailInput = document.getElementById("usuario-correo");
    const indicator = document.getElementById("email-format-indicator");
    const val = emailInput.value.trim();
    
    if (!val) {
        indicator.textContent = "Pendiente de ingreso";
        indicator.className = "email-indicator";
    } else if (validateEmail(val)) {
        indicator.textContent = "✓ Formato de correo válido";
        indicator.className = "email-indicator valid";
    } else {
        indicator.textContent = "✗ Formato inválido (debe contener @ y .)";
        indicator.className = "email-indicator invalid";
    }
}

async function submitUsuario(event) {
    event.preventDefault();
    document.querySelectorAll(".error-msg").forEach(span => span.textContent = "");
    
    const nombre = document.getElementById("usuario-nombre").value.trim();
    const correo = document.getElementById("usuario-correo").value.trim();
    
    let valido = true;
    if (!nombre) {
        document.getElementById("error-usuario-nombre").textContent = "El nombre es requerido.";
        valido = false;
    }
    if (!correo) {
        document.getElementById("error-usuario-correo").textContent = "El correo es requerido.";
        valido = false;
    } else if (!validateEmail(correo)) {
        document.getElementById("error-usuario-correo").textContent = "Formato de correo electrónico inválido.";
        valido = false;
    }
    
    if (!valido) return;
    
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/usuarios`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, correo })
        });
        
        const resData = await response.json();
        if (!response.ok) {
            // Manejar excepciones de negocio del backend (ej. UsuarioDuplicadoError)
            throw new Error(resData.detail || "Error al registrar miembro");
        }
        
        showToast(`Miembro "${nombre}" registrado con éxito. ID Asignado: ${resData.id}`, "success");
        closeModal("modal-usuario");
        document.getElementById("form-usuario").reset();
        document.getElementById("email-format-indicator").textContent = "Pendiente de ingreso";
        document.getElementById("email-format-indicator").className = "email-indicator";
        
        fetchUsuarios();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

// -------------------------------------------------------------
// GESTIÓN DE PRÉSTAMOS
// -------------------------------------------------------------
async function fetchPrestamos() {
    setLoading(true);
    try {
        // Traer activos
        const resActivos = await fetch(`${API_URL}/api/prestamos?solo_activos=true`);
        if (!resActivos.ok) throw new Error("Fallo al cargar préstamos activos");
        activeLoansData = await resActivos.json();
        
        // Traer histórico
        const resAll = await fetch(`${API_URL}/api/prestamos?solo_activos=false`);
        if (!resAll.ok) throw new Error("Fallo al cargar historial de préstamos");
        allLoansData = await resAll.json();
        
        renderPrestamosTables();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

function renderPrestamosTables() {
    // Render Activos
    const tbodyActivos = document.getElementById("table-prestamos-activos-body");
    tbodyActivos.innerHTML = "";
    
    if (activeLoansData.length === 0) {
        tbodyActivos.innerHTML = `<tr><td colspan="7" class="text-center italic text-muted">No hay préstamos activos.</td></tr>`;
    } else {
        activeLoansData.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><code>${p.id}</code></td>
                <td>${p.nombre_usuario} <small class="text-muted">(ID: ${p.id_usuario})</small></td>
                <td class="font-semibold">${p.titulo_libro}</td>
                <td><code>${p.isbn}</code></td>
                <td>${p.fecha_prestamo}</td>
                <td><span class="text-orange font-semibold">${p.fecha_devolucion_esperada}</span></td>
                <td>
                    <button class="btn btn-success btn-small" onclick="ejecutarDevolucion(${p.id})">
                        <i data-lucide="corner-down-left" style="width: 14px; height: 14px;"></i>
                        <span>Devolver</span>
                    </button>
                </td>
            `;
            tbodyActivos.appendChild(tr);
        });
    }
    
    // Render Histórico
    const tbodyHistorico = document.getElementById("table-prestamos-historico-body");
    tbodyHistorico.innerHTML = "";
    
    if (allLoansData.length === 0) {
        tbodyHistorico.innerHTML = `<tr><td colspan="7" class="text-center italic text-muted">Historial vacío.</td></tr>`;
    } else {
        allLoansData.forEach(p => {
            const tr = document.createElement("tr");
            const isDevuelto = p.estado === 'Devuelto';
            const badgeClass = isDevuelto ? 'badge badge-success' : 'badge badge-danger';
            
            tr.innerHTML = `
                <td><code>${p.id}</code></td>
                <td>${p.nombre_usuario} <small class="text-muted">(ID: ${p.id_usuario})</small></td>
                <td class="font-semibold">${p.titulo_libro}</td>
                <td><code>${p.isbn}</code></td>
                <td>${p.fecha_prestamo}</td>
                <td>${p.fecha_devolucion_esperada}</td>
                <td><span class="${badgeClass}">${p.estado}</span></td>
            `;
            tbodyHistorico.appendChild(tr);
        });
    }
    
    lucide.createIcons();
}

function switchLoansTab(tab) {
    activeLoansTab = tab;
    document.getElementById("tab-loans-activos").classList.remove("active");
    document.getElementById("tab-loans-historico").classList.remove("active");
    
    document.getElementById("container-loans-activos").style.display = "none";
    document.getElementById("container-loans-historico").style.display = "none";
    
    if (tab === 'activos') {
        document.getElementById("tab-loans-activos").classList.add("active");
        document.getElementById("container-loans-activos").style.display = "block";
    } else {
        document.getElementById("tab-loans-historico").classList.add("active");
        document.getElementById("container-loans-historico").style.display = "block";
    }
}

async function abrir_modal_prestamo() {
    setLoading(true);
    try {
        // Cargar listas frescas de usuarios y libros
        const resUsers = await fetch(`${API_URL}/api/usuarios`);
        const resBooks = await fetch(`${API_URL}/api/libros`);
        
        if (!resUsers.ok || !resBooks.ok) throw new Error("No se pudo cargar la información para crear el préstamo");
        
        const users = await resUsers.json();
        const books = await resBooks.json();
        
        // Filtrar libros que tengan stock > 0
        const availableBooks = books.filter(b => b.cantidad_disponible > 0);
        
        const selectUser = document.getElementById("prestamo-usuario");
        const selectBook = document.getElementById("prestamo-libro");
        
        selectUser.innerHTML = "";
        selectBook.innerHTML = "";
        
        if (users.length === 0) {
            showToast("Debe registrar al menos un usuario primero.", "warning");
            return;
        }
        
        if (availableBooks.length === 0) {
            showToast("No hay libros en stock disponibles para prestar.", "warning");
            return;
        }
        
        users.forEach(u => {
            const opt = document.createElement("option");
            opt.value = u.id;
            opt.textContent = `ID ${u.id}: ${u.nombre} (${u.correo})`;
            selectUser.appendChild(opt);
        });
        
        availableBooks.forEach(b => {
            const opt = document.createElement("option");
            opt.value = b.isbn;
            opt.textContent = `[${b.isbn}] ${b.titulo} - ${b.autor} (Stock: ${b.cantidad_disponible})`;
            selectBook.appendChild(opt);
        });
        
        document.getElementById("prestamo-dias").value = 7;
        openModal("modal-prestamo");
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

async function submitPrestamo(event) {
    event.preventDefault();
    const id_usuario = parseInt(document.getElementById("prestamo-usuario").value);
    const isbn = document.getElementById("prestamo-libro").value;
    const dias = parseInt(document.getElementById("prestamo-dias").value);
    
    if (isNaN(id_usuario) || !isbn || isNaN(dias) || dias <= 0) {
        showToast("Por favor complete los campos correctamente.", "warning");
        return;
    }
    
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/prestamos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_usuario, isbn, dias_prestamo: dias })
        });
        
        const resData = await response.json();
        if (!response.ok) {
            // Manejar excepciones críticas de negocio (ej. SinStockError, UsuarioNoEncontradoError)
            throw new Error(resData.detail || "Error al procesar el préstamo");
        }
        
        showToast(`Préstamo #${resData.id} registrado con éxito.`, "success");
        closeModal("modal-prestamo");
        
        // Refrescar préstamos
        fetchPrestamos();
    } catch (err) {
        // Muestra alerta dinámica en pantalla (Toast/SnackBar) al atrapar excepciones de lógica
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

async function ejecutarDevolucion(idPrestamo) {
    if (!confirm(`¿Está seguro de registrar la devolución para el préstamo #${idPrestamo}?`)) {
        return;
    }
    
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/prestamos/devolver/${idPrestamo}`, {
            method: "POST"
        });
        
        const resData = await response.json();
        if (!response.ok) {
            throw new Error(resData.detail || "Error al registrar la devolución");
        }
        
        showToast(`Devolución del préstamo #${idPrestamo} registrada con éxito. Stock restituido.`, "success");
        fetchPrestamos();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(false);
    }
}

// -------------------------------------------------------------
// CONTROLADOR DE MODALES
// -------------------------------------------------------------
function openModal(modalId) {
    document.getElementById(modalId).classList.add("active");
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove("active");
    // Limpiar errores dentro de ese modal
    const modal = document.getElementById(modalId);
    modal.querySelectorAll(".error-msg").forEach(span => span.textContent = "");
}

// -------------------------------------------------------------
// TOASTS Y NOTIFICACIONES DINÁMICAS
// -------------------------------------------------------------
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let iconName = "check-circle";
    if (type === "error") iconName = "alert-circle";
    if (type === "warning") iconName = "alert-triangle";
    
    toast.innerHTML = `
        <i data-lucide="${iconName}"></i>
        <div class="toast-content">
            <p>${message}</p>
        </div>
        <button class="toast-close-btn">&times;</button>
    `;
    
    container.appendChild(toast);
    lucide.createIcons();
    
    // Handler para botón cerrar
    toast.querySelector(".toast-close-btn").addEventListener("click", () => {
        toast.style.animation = "toastOut 0.3s ease forwards";
        setTimeout(() => toast.remove(), 300);
    });
    
    // Auto-remove
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = "toastOut 0.3s ease forwards";
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// -------------------------------------------------------------
// CONTROLADORES DE INTERFAZ & TEMAS
// -------------------------------------------------------------
function setLoading(isLoading) {
    const spinner = document.getElementById("global-spinner");
    if (spinner) {
        spinner.style.display = isLoading ? "flex" : "none";
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    
    html.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateThemeToggleUI(newTheme);
}

function updateThemeToggleUI(theme) {
    const btn = document.getElementById("btn-theme-toggle");
    if (theme === "dark") {
        btn.setAttribute("title", "Cambiar a Modo Claro");
    } else {
        btn.setAttribute("title", "Cambiar a Modo Oscuro");
    }
}
