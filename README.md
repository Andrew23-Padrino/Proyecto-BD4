# 📚 Sistema de Gestión de Biblioteca

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Flet UI](https://img.shields.io/badge/Flet-UI-blueviolet.svg)](https://flet.dev)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un sistema modular, seguro y profesional para la administración de bibliotecas integrado con **MySQL**. Este proyecto destaca por implementar **tres interfaces de usuario distintas** en la misma lógica de negocio, además de emplear **control de concurrencia avanzado** para garantizar la integridad ACID en las transacciones de préstamos y devoluciones.

---

## 🚀 Características Clave

*   **Arquitectura Modular Multiusuario**: Separación rigurosa de responsabilidades (Presentación, Servicios, Modelos y Persistencia).
*   **Múltiples Interfaces**:
    *   💻 **Web SPA**: Panel moderno y reactivo (FastAPI + HTML5/CSS3/JS Vanilla) con soporte de modo oscuro, alertas dinámicas (Toasts) y transiciones fluidas.
    *   🖥️ **Desktop GUI**: Interfaz de escritorio nativa basada en **Flet** (Flutter para Python) con modo claro/oscuro.
    *   📟 **CLI Console**: Interfaz de terminal interactiva con menús y control de excepciones.
*   **Transaccionalidad Segura (ACID)**: Lógica de préstamos y devoluciones blindada contra condiciones de carrera mediante **bloqueos pesimistas (`SELECT ... FOR UPDATE`)** a nivel de base de datos MySQL (InnoDB).
*   **Integridad Referencial Estricta**:
    *   Llaves foráneas con políticas restrictivas (`ON DELETE RESTRICT`) para prevenir registros huérfanos.
    *   Restricciones `CHECK` para control de stock no negativo y validación sintáctica de formato de correo.
    *   Índices óptimos creados de forma automática para agilizar búsquedas.
*   **Autobootstrap**: El sistema inicializa la base de datos y recrea el esquema SQL de forma automática en el primer inicio.

---

## 🛠️ Pila Tecnológica (Tech Stack)

*   **Lenguaje**: Python 3.8+
*   **Base de Datos**: MySQL (motor InnoDB)
*   **Frameworks Web / API**: FastAPI, Uvicorn, Pydantic
*   **Desktop UI**: Flet (Flutter engine)
*   **Acceso a Base de Datos**: PyMySQL
*   **Estilos y Maquetación**: HTML5, Vanilla CSS3 (con variables de tema CSS), Lucide Icons
*   **Pruebas (Testing)**: Unittest & Unittest.mock

---

## 📁 Estructura del Proyecto

```bash
├── database/            # Capa de persistencia (Esquema SQL y conexión)
│   ├── connection.py    # Administrador de contextos de conexión y bootstrapping
│   └── schema.sql       # Script de creación de tablas, restricciones e índices
├── models/              # Clases de dominio del sistema
│   ├── libro.py         # Entidad Libro
│   ├── usuario.py       # Entidad Usuario
│   └── prestamo.py      # Entidad Préstamo
├── services/            # Capa lógica de negocio (Excepciones y Servicios)
│   ├── exceptions.py    # Excepciones de negocio personalizadas
│   ├── libro_service.py # Lógica CRUD y búsquedas de catálogo
│   ├── usuario_service.py # Gestión y altas de miembros
│   └── prestamo_service.py # Control transaccional ACID de préstamos y devoluciones
├── frontend/            # Código fuente de la Single Page Application (Web UI)
│   ├── index.html       # Estructura HTML de la app
│   ├── style.css        # Hoja de estilos con variables de tema (Oscuro/Claro)
│   └── app.js           # Lógica y llamadas AJAX (fetch) a FastAPI
├── tests/               # Pruebas unitarias
│   └── test_library.py  # Tests lógicos simulados con MagicMock
├── app.py               # Servidor FastAPI (Servicios REST y Static Files)
├── gui.py               # Aplicación de Escritorio (Flet)
├── main.py              # Interfaz de Consola interactiva (CLI)
├── config.py            # Carga de credenciales y dotenv
└── requirements.txt     # Dependencias del sistema
```

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/proyecto-bd4.git
cd proyecto-bd4
```

### 2. Configurar Variables de Entorno
Cree un archivo `.env` en la raíz del proyecto basándose en el archivo `.env.example`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=biblioteca_db
```
*(Nota: Si no se configuran estas variables, el sistema usará credenciales por defecto: `localhost`, `3306`, `root`, sin contraseña, base de datos `biblioteca_db`)*.

### 3. Instalar Dependencias
Se recomienda utilizar un entorno virtual (venv):
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

---

## 🖥️ Ejecución de la Aplicación

El proyecto proporciona **tres formas independientes** de interactuar con el sistema de biblioteca:

### Opción A: Aplicación Web (FastAPI)
Ejecute el servidor web para acceder desde cualquier navegador:
```bash
python app.py
```
El servidor se iniciará en **http://127.0.0.1:8000** sirviendo la API REST (`/api/...`) y el frontend estático interactivo en la raíz (`/`).

### Opción B: Aplicación de Escritorio (Flet)
Corra la aplicación gráfica multiplataforma:
```bash
python gui.py
```
Se abrirá una ventana de escritorio con el panel de administración, soporte de temas claro/oscuro y validación de formularios.

### Opción C: Interfaz por Consola (CLI)
Corra la consola interactiva clásica en terminal:
```bash
python main.py
```
*(Nota: En cualquiera de los tres casos, si la base de datos `biblioteca_db` o sus tablas no existen en el servidor MySQL, la aplicación solicitará autorización o las creará automáticamente)*.

---

## 🧪 Pruebas Unitarias

El proyecto cuenta con una batería de pruebas unitarias para validar las reglas de negocio críticas de forma aislada sin requerir de un servidor MySQL activo (usando `unittest.mock`):

```bash
python -m unittest tests/test_library.py
```

Las pruebas cubren escenarios críticos como:
*   Intento de préstamos a usuarios no registrados.
*   Intento de préstamos de libros no registrados.
*   Intento de préstamos de libros que se encuentran sin stock físico.
*   Validaciones de límites y restricciones de años de publicación.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulte el archivo `LICENSE` para más detalles.
