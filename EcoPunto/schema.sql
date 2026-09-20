-- ============================================================
-- EcoPunto - Esquema de base de datos relacional
-- Universidad Manuela Beltran - Ingenieria de Software
-- SGBD: SQLite 3 (compatible con MySQL 8 con ajustes minimos)
-- ============================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS reporte_ambiental;
DROP TABLE IF EXISTS campania;
DROP TABLE IF EXISTS registro_residuo;
DROP TABLE IF EXISTS tipo_residuo;
DROP TABLE IF EXISTS punto_reciclaje;
DROP TABLE IF EXISTS usuario;

-- ------------------------------------------------------------
-- Tabla: usuario
-- ------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario       INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           VARCHAR(100) NOT NULL,
    correo           VARCHAR(120) NOT NULL UNIQUE,
    contrasena_hash  VARCHAR(200) NOT NULL,
    rol              VARCHAR(20)  NOT NULL DEFAULT 'ciudadano'
                     CHECK (rol IN ('ciudadano', 'administrador')),
    fecha_registro   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activo           INTEGER      NOT NULL DEFAULT 1
);

-- ------------------------------------------------------------
-- Tabla: punto_reciclaje
-- ------------------------------------------------------------
CREATE TABLE punto_reciclaje (
    id_punto     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       VARCHAR(100)  NOT NULL,
    direccion    VARCHAR(150)  NOT NULL,
    localidad    VARCHAR(60)   NOT NULL,
    latitud      DECIMAL(9,6),
    longitud     DECIMAL(9,6),
    horario      VARCHAR(80),
    estado       VARCHAR(20)   NOT NULL DEFAULT 'activo'
                 CHECK (estado IN ('activo', 'inactivo', 'mantenimiento'))
);

-- ------------------------------------------------------------
-- Tabla: tipo_residuo
-- factor_co2 = kg de CO2 equivalente evitado por cada kg reciclado
-- ------------------------------------------------------------
CREATE TABLE tipo_residuo (
    id_tipo        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         VARCHAR(60)  NOT NULL UNIQUE,
    categoria      VARCHAR(40)  NOT NULL,
    unidad_medida  VARCHAR(10)  NOT NULL DEFAULT 'kg',
    factor_co2     DECIMAL(6,3) NOT NULL DEFAULT 0,
    activo         INTEGER      NOT NULL DEFAULT 1
);

-- ------------------------------------------------------------
-- Tabla: registro_residuo  (entidad transaccional principal)
-- ------------------------------------------------------------
CREATE TABLE registro_residuo (
    id_registro     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario      INTEGER      NOT NULL,
    id_punto        INTEGER      NOT NULL,
    id_tipo         INTEGER      NOT NULL,
    cantidad        DECIMAL(8,2) NOT NULL CHECK (cantidad > 0),
    fecha_registro  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observaciones   VARCHAR(250),
    CONSTRAINT fk_registro_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_registro_punto   FOREIGN KEY (id_punto)
        REFERENCES punto_reciclaje (id_punto) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_registro_tipo    FOREIGN KEY (id_tipo)
        REFERENCES tipo_residuo (id_tipo) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ------------------------------------------------------------
-- Tabla: reporte_ambiental
-- ------------------------------------------------------------
CREATE TABLE reporte_ambiental (
    id_reporte        INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario        INTEGER       NOT NULL,
    fecha_generacion  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_inicio      DATE          NOT NULL,
    fecha_fin         DATE          NOT NULL,
    total_kg          DECIMAL(10,2) NOT NULL DEFAULT 0,
    co2_evitado       DECIMAL(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_reporte_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ------------------------------------------------------------
-- Tabla: campania
-- ------------------------------------------------------------
CREATE TABLE campania (
    id_campania   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_punto      INTEGER      NOT NULL,
    nombre        VARCHAR(100) NOT NULL,
    descripcion   VARCHAR(250),
    fecha_inicio  DATE         NOT NULL,
    fecha_fin     DATE         NOT NULL,
    CONSTRAINT fk_campania_punto FOREIGN KEY (id_punto)
        REFERENCES punto_reciclaje (id_punto) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ------------------------------------------------------------
-- Indices para optimizar consultas frecuentes (RNF de rendimiento)
-- ------------------------------------------------------------
CREATE INDEX idx_registro_fecha   ON registro_residuo (fecha_registro);
CREATE INDEX idx_registro_usuario ON registro_residuo (id_usuario);
CREATE INDEX idx_punto_localidad  ON punto_reciclaje (localidad);
