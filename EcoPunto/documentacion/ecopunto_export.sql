-- ============================================================
-- EcoPunto - Export completo de la base de datos
-- Universidad Manuela Beltran - Ingenieria de Software
-- Evento PLANETA VERDE 2026
-- SGBD origen: SQLite 3.45
-- Restauracion:  sqlite3 ecopunto.db < ecopunto_export.sql
-- Contenido: 6 tablas, 3 indices, datos de prueba incluidos
-- ============================================================

BEGIN TRANSACTION;
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
INSERT INTO "campania" VALUES(1,1,'Semana Ambiental UMB','Jornada de recoleccion de papel y RAEE en la sede Centro','2026-09-21','2026-09-26');
INSERT INTO "campania" VALUES(2,2,'Reciclaton Simon Bolivar','Recoleccion masiva de plastico PET y vidrio','2026-10-05','2026-10-06');
INSERT INTO "campania" VALUES(3,3,'Kennedy Recicla','Campana de sensibilizacion y acopio de metales','2026-10-12','2026-10-20');
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
INSERT INTO "punto_reciclaje" VALUES(1,'EcoPunto UMB Sede Centro','Av. Circunvalar 60-00','Chapinero',4.64123,-74.06145,'Lunes a viernes 7:00 - 19:00','activo');
INSERT INTO "punto_reciclaje" VALUES(2,'Punto Verde Parque Simon Bolivar','Calle 63 # 59-30','Teusaquillo',4.6589,-74.0934,'Todos los dias 6:00 - 18:00','activo');
INSERT INTO "punto_reciclaje" VALUES(3,'Centro de Acopio Kennedy','Carrera 78K # 38-50 Sur','Kennedy',4.6287,-74.1553,'Lunes a sabado 8:00 - 17:00','activo');
INSERT INTO "punto_reciclaje" VALUES(4,'EcoPunto Plaza Usaquen','Carrera 6 # 119-20','Usaquen',4.6945,-74.0302,'Martes a domingo 9:00 - 16:00','mantenimiento');
INSERT INTO "punto_reciclaje" VALUES(5,'Punto Limpio Suba Rincon','Calle 131A # 91-40','Suba',4.7448,-74.0976,'Lunes a viernes 8:00 - 18:00','activo');
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
INSERT INTO "registro_residuo" VALUES(1,2,1,1,12.5,'2026-08-03 09:15:00','Material de oficina del semestre anterior');
INSERT INTO "registro_residuo" VALUES(2,2,1,2,8.2,'2026-08-10 10:40:00','Botellas separadas y limpias');
INSERT INTO "registro_residuo" VALUES(3,2,2,3,15,'2026-08-17 11:05:00','Frascos de vidrio de conjunto residencial');
INSERT INTO "registro_residuo" VALUES(4,3,3,4,3.8,'2026-08-21 14:30:00','Latas de bebida compactadas');
INSERT INTO "registro_residuo" VALUES(5,3,3,1,22.4,'2026-08-28 08:50:00','Campana escolar de recoleccion');
INSERT INTO "registro_residuo" VALUES(6,3,5,5,6.1,'2026-09-04 16:20:00','Dos teclados y un monitor');
INSERT INTO "registro_residuo" VALUES(7,2,5,6,4.5,'2026-09-09 17:00:00','Aceite de cocina en envase sellado');
INSERT INTO "registro_residuo" VALUES(8,3,2,2,11.3,'2026-09-14 09:35:00','Jornada ambiental del barrio');
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
INSERT INTO "reporte_ambiental" VALUES(1,2,'2026-09-01 08:00:00','2026-08-01','2026-08-31',35.7,51.51);
INSERT INTO "reporte_ambiental" VALUES(2,3,'2026-09-01 08:05:00','2026-08-01','2026-08-31',26.2,63.42);
CREATE TABLE tipo_residuo (
    id_tipo        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         VARCHAR(60)  NOT NULL UNIQUE,
    categoria      VARCHAR(40)  NOT NULL,
    unidad_medida  VARCHAR(10)  NOT NULL DEFAULT 'kg',
    factor_co2     DECIMAL(6,3) NOT NULL DEFAULT 0,
    activo         INTEGER      NOT NULL DEFAULT 1
);
INSERT INTO "tipo_residuo" VALUES(1,'Papel y carton','Aprovechable','kg',1.32,1);
INSERT INTO "tipo_residuo" VALUES(2,'Plastico PET','Aprovechable','kg',2.15,1);
INSERT INTO "tipo_residuo" VALUES(3,'Vidrio','Aprovechable','kg',0.58,1);
INSERT INTO "tipo_residuo" VALUES(4,'Aluminio y metales','Aprovechable','kg',8.9,1);
INSERT INTO "tipo_residuo" VALUES(5,'Residuos electronicos (RAEE)','Especial','kg',3.4,1);
INSERT INTO "tipo_residuo" VALUES(6,'Aceite vegetal usado','Especial','kg',2.7,1);
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
INSERT INTO "usuario" VALUES(1,'Administrador EcoPunto','admin@umb.edu.co','scrypt:32768:8:1$ai5hPjt2Jb3j1jl0$b9bc4e652005a7a0f111f84c6d3e2761251e81707cd0d41e1253e7ec56661509c37de1bfb897594d8cbd4b24df4fdb0434433c60fef4d5a46b310d733fa7550a','administrador','2026-09-19 02:06:20',1);
INSERT INTO "usuario" VALUES(2,'Laura Gomez Ramirez','laura.gomez@umb.edu.co','scrypt:32768:8:1$OIwuwEG6OBsmGRKG$dc9124178b1815098bb54f2f5b02b5abf5bfe62bdc8790090780c7fab8cf27b77737c18c264bd01a0ff98ae0c806856c036b3c8114ad424569da044e930d30ed','ciudadano','2026-09-19 02:06:20',1);
INSERT INTO "usuario" VALUES(3,'Carlos Peña Duarte','carlos.pena@umb.edu.co','scrypt:32768:8:1$jHSLGTK9v0WqMQS1$24f98e4b2a5bf4ebb2f2d4f52cf2ca56cd262cc98950563221413bae3eb07b8a74c53ee7a1fa5be987f970beb82a3820cb48f93204ee6d4916c0fd3dfce1931c','ciudadano','2026-09-19 02:06:20',1);
CREATE INDEX idx_registro_fecha   ON registro_residuo (fecha_registro);
CREATE INDEX idx_registro_usuario ON registro_residuo (id_usuario);
CREATE INDEX idx_punto_localidad  ON punto_reciclaje (localidad);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('usuario',3);
INSERT INTO "sqlite_sequence" VALUES('punto_reciclaje',5);
INSERT INTO "sqlite_sequence" VALUES('tipo_residuo',6);
INSERT INTO "sqlite_sequence" VALUES('registro_residuo',8);
INSERT INTO "sqlite_sequence" VALUES('campania',3);
INSERT INTO "sqlite_sequence" VALUES('reporte_ambiental',2);
COMMIT;
