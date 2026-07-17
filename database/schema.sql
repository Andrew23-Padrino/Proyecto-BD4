-- Script SQL para la creación de la Base de Datos y sus Tablas
-- Sistema de Gestión de Biblioteca

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS biblioteca_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE biblioteca_db;

-- Eliminar tablas si existen para permitir la re-inicialización limpia
DROP TABLE IF EXISTS prestamos;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS libros;

-- 1. TABLA: usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_correo_valido CHECK (correo LIKE '%@%.%')
) ENGINE=InnoDB;

-- 2. TABLA: libros
CREATE TABLE IF NOT EXISTS libros (
    isbn VARCHAR(20) PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(150) NOT NULL,
    anio_publicacion INT NOT NULL,
    cantidad_disponible INT NOT NULL DEFAULT 0,
    categoria VARCHAR(100) DEFAULT 'Sin Categoría',
    CONSTRAINT chk_cantidad_no_negativa CHECK (cantidad_disponible >= 0),
    CONSTRAINT chk_anio_valido CHECK (anio_publicacion > 0)
) ENGINE=InnoDB;

-- 3. TABLA: prestamos
CREATE TABLE IF NOT EXISTS prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    isbn VARCHAR(20) NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion_esperada DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
    CONSTRAINT chk_estado_prestamo CHECK (estado IN ('Activo', 'Devuelto')),
    CONSTRAINT chk_fechas CHECK (fecha_devolucion_esperada >= fecha_prestamo),
    
    -- Llaves foráneas con políticas de integridad restrictivas
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (isbn) REFERENCES libros(isbn) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Índices adicionales para optimizar búsquedas frecuentes
CREATE INDEX idx_libros_titulo ON libros(titulo);
CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_prestamos_estado ON prestamos(estado);
