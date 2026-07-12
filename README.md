# Walkthrough: Sistema de Gestión de Biblioteca

Hemos implementado un sistema modular, limpio y profesional en Python 3 integrado con MySQL. A continuación se detalla el trabajo realizado.

---

## 1. Estructura de Archivos Creada
Se implementó la arquitectura POO recomendada para mantener la separación de responsabilidades:

- [config.py](file:///c:/Users/Andrews/Documents/BD4/config.py): Configuración de credenciales de acceso a MySQL mediante variables de entorno y valores predeterminados.
- [requirements.txt](file:///c:/Users/Andrews/Documents/BD4/requirements.txt): Declaración de las dependencias (`pymysql` y `cryptography`).
- **`database/`**
  - [database/schema.sql](file:///c:/Users/Andrews/Documents/BD4/database/schema.sql): Script SQL estructurado con restricciones de integridad, relaciones (FK) e índices.
  - [database/connection.py](file:///c:/Users/Andrews/Documents/BD4/database/connection.py): Administrador de contexto `DatabaseConnection` y función `inicializar_base_de_datos()` para bootstrap de tablas.
- **`models/`**
  - [models/libro.py](file:///c:/Users/Andrews/Documents/BD4/models/libro.py): Modelo y mapeador de datos de la entidad `Libro`.
  - [models/usuario.py](file:///c:/Users/Andrews/Documents/BD4/models/usuario.py): Modelo de la entidad `Usuario` (miembro).
  - [models/prestamo.py](file:///c:/Users/Andrews/Documents/BD4/models/prestamo.py): Modelo de la entidad `Prestamo`.
- **`services/`**
  - [services/exceptions.py](file:///c:/Users/Andrews/Documents/BD4/services/exceptions.py): Excepciones personalizadas para reglas de negocio (ej. `SinStockError`, `LibroDuplicadoError`).
  - [services/libro_service.py](file:///c:/Users/Andrews/Documents/BD4/services/libro_service.py): CRUD y búsqueda de libros.
  - [services/usuario_service.py](file:///c:/Users/Andrews/Documents/BD4/services/usuario_service.py): Registro y obtención de usuarios.
  - [services/prestamo_service.py](file:///c:/Users/Andrews/Documents/BD4/services/prestamo_service.py): Gestión de préstamos y devoluciones con transacciones SQL ACID.
- [main.py](file:///c:/Users/Andrews/Documents/BD4/main.py): Interfaz interactiva de consola con el menú completo y control de errores.
- **`tests/`**
  - [tests/test_library.py](file:///c:/Users/Andrews/Documents/BD4/tests/test_library.py): Pruebas unitarias que validan la lógica de negocio con mocks.

---

## 2. Aspectos Destacados de la Implementación

### A. Integridad de Base de Datos (MySQL)
- Llaves foráneas con `ON DELETE RESTRICT` para evitar huérfanos.
- Constraints a nivel de base de datos como `CHECK (cantidad_disponible >= 0)` y validación básica de formato de correo.
- Creación automática de índices (`idx_libros_titulo`, `idx_usuarios_correo`, `idx_prestamos_estado`) para mejorar el rendimiento de consultas frecuentes.

### B. Context Managers Seguros
La clase `DatabaseConnection` se encarga de:
```python
with DatabaseConnection() as (conn, cursor):
    cursor.execute(...)
    conn.commit()
```
Garantiza el cierre seguro de los cursores y conexiones incluso si ocurren fallas en medio de la consulta, y ejecuta un `rollback` en caso de excepción no controlada.

### C. Lógica Transaccional ACID (Préstamos y Devoluciones)
Para evitar condiciones de carrera (Race Conditions), las operaciones de préstamos y devoluciones usan **bloqueo pesimista** (`FOR UPDATE`) dentro de una transacción explícita:
1. Se inicia la transacción.
2. Se consulta y bloquea la fila del libro o préstamo (`SELECT ... FOR UPDATE`).
3. Se verifica la regla de negocio (¿Hay stock? ¿Existe el usuario/libro?).
4. Se ejecuta la inserción del préstamo y la actualización del stock.
5. Se realiza el `COMMIT`. Si algo falla, se ejecuta `ROLLBACK` de manera automática por el administrador de contexto.

---

## 3. Verificación y Pruebas Realizadas

Se implementaron y ejecutaron con éxito pruebas unitarias en `tests/test_library.py` simulando la base de datos con `unittest.mock`. 

### Resultados de los Tests
```bash
python -m unittest tests/test_library.py
...
----------------------------------------------------------------------
Ran 3 tests in 0.014s

OK
```
Esto confirma que la lógica de negocio (validaciones de usuario no existente, libro no existente, y falta de stock de libros) funciona perfectamente y lanza las excepciones de negocio adecuadas.

---

## 4. Instrucciones para Ejecutar el Proyecto

### 1. Configurar Base de Datos
Edite el archivo [config.py](file:///c:/Users/Andrews/Documents/BD4/config.py) para ingresar los datos correctos de su servidor MySQL (ej. host, usuario y contraseña):
```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "su_usuario"
DB_PASSWORD = "su_contraseña"
```

### 2. Instalar Dependencias
Instale los paquetes especificados ejecutando:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación
Inicie la consola interactiva:
```bash
python main.py
```
*Nota: En el primer inicio, si el sistema detecta que la base de datos no existe, le preguntará si desea inicializarla automáticamente.*
