"""
EcoPunto - Capa de acceso a datos (Modelo en el patron MVC)
Universidad Manuela Beltran - Ingenieria de Software

Responsabilidad unica: abrir conexiones, inicializar el esquema y
exponer operaciones CRUD parametrizadas contra SQLite.

Todas las consultas usan sentencias preparadas (placeholders "?"),
lo que previene inyeccion SQL segun OWASP Top 10 (A03:2021).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "ecopunto.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "seed.sql")


def get_connection():
    """Devuelve una conexion con claves foraneas activas y filas tipo dict."""
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def consultar(sql, parametros=(), uno=False):
    """Ejecuta un SELECT y devuelve una fila o una lista de filas."""
    with get_connection() as conexion:
        cursor = conexion.execute(sql, parametros)
        return cursor.fetchone() if uno else cursor.fetchall()


def ejecutar(sql, parametros=()):
    """Ejecuta INSERT / UPDATE / DELETE y devuelve el id afectado."""
    with get_connection() as conexion:
        cursor = conexion.execute(sql, parametros)
        conexion.commit()
        return cursor.lastrowid


def inicializar_bd(forzar=False):
    """Crea el esquema y carga los datos de prueba si la BD no existe."""
    if os.path.exists(DB_PATH) and not forzar:
        return False

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with get_connection() as conexion:
        with open(SCHEMA_PATH, encoding="utf-8") as archivo:
            conexion.executescript(archivo.read())

        # Usuarios con contrasena cifrada (nunca en texto plano)
        conexion.executemany(
            "INSERT INTO usuario (nombre, correo, contrasena_hash, rol) VALUES (?, ?, ?, ?)",
            [
                ("Administrador EcoPunto", "admin@umb.edu.co",
                 generate_password_hash("Admin2026*"), "administrador"),
                ("Laura Gomez Ramirez", "laura.gomez@umb.edu.co",
                 generate_password_hash("Eco2026*"), "ciudadano"),
                ("Carlos Peña Duarte", "carlos.pena@umb.edu.co",
                 generate_password_hash("Eco2026*"), "ciudadano"),
            ],
        )

        with open(SEED_PATH, encoding="utf-8") as archivo:
            conexion.executescript(archivo.read())

        conexion.commit()
    return True


# ----------------------------------------------------------------------
# CRUD: PUNTO_RECICLAJE
# ----------------------------------------------------------------------

def listar_puntos(filtro_localidad=None):
    sql = "SELECT * FROM punto_reciclaje"
    parametros = ()
    if filtro_localidad:
        sql += " WHERE localidad LIKE ?"
        parametros = (f"%{filtro_localidad}%",)
    sql += " ORDER BY nombre"
    return consultar(sql, parametros)


def obtener_punto(id_punto):
    return consultar(
        "SELECT * FROM punto_reciclaje WHERE id_punto = ?", (id_punto,), uno=True
    )


def crear_punto(datos):
    return ejecutar(
        """INSERT INTO punto_reciclaje
           (nombre, direccion, localidad, latitud, longitud, horario, estado)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (datos["nombre"], datos["direccion"], datos["localidad"],
         datos["latitud"], datos["longitud"], datos["horario"], datos["estado"]),
    )


def actualizar_punto(id_punto, datos):
    return ejecutar(
        """UPDATE punto_reciclaje
           SET nombre = ?, direccion = ?, localidad = ?, latitud = ?,
               longitud = ?, horario = ?, estado = ?
           WHERE id_punto = ?""",
        (datos["nombre"], datos["direccion"], datos["localidad"], datos["latitud"],
         datos["longitud"], datos["horario"], datos["estado"], id_punto),
    )


def eliminar_punto(id_punto):
    return ejecutar("DELETE FROM punto_reciclaje WHERE id_punto = ?", (id_punto,))


def punto_tiene_registros(id_punto):
    fila = consultar(
        "SELECT COUNT(*) AS total FROM registro_residuo WHERE id_punto = ?",
        (id_punto,), uno=True,
    )
    return fila["total"] > 0


# ----------------------------------------------------------------------
# CRUD: REGISTRO_RESIDUO
# ----------------------------------------------------------------------

def listar_registros(id_usuario=None):
    sql = """
        SELECT r.id_registro, r.cantidad, r.fecha_registro, r.observaciones,
               u.nombre AS usuario, p.nombre AS punto, p.localidad,
               t.nombre AS tipo, t.unidad_medida, t.factor_co2,
               ROUND(r.cantidad * t.factor_co2, 2) AS co2_evitado
        FROM registro_residuo r
        INNER JOIN usuario         u ON u.id_usuario = r.id_usuario
        INNER JOIN punto_reciclaje p ON p.id_punto   = r.id_punto
        INNER JOIN tipo_residuo    t ON t.id_tipo    = r.id_tipo
    """
    parametros = ()
    if id_usuario:
        sql += " WHERE r.id_usuario = ?"
        parametros = (id_usuario,)
    sql += " ORDER BY r.fecha_registro DESC"
    return consultar(sql, parametros)


def obtener_registro(id_registro):
    return consultar(
        "SELECT * FROM registro_residuo WHERE id_registro = ?", (id_registro,), uno=True
    )


def crear_registro(datos):
    return ejecutar(
        """INSERT INTO registro_residuo
           (id_usuario, id_punto, id_tipo, cantidad, observaciones)
           VALUES (?, ?, ?, ?, ?)""",
        (datos["id_usuario"], datos["id_punto"], datos["id_tipo"],
         datos["cantidad"], datos["observaciones"]),
    )


def actualizar_registro(id_registro, datos):
    return ejecutar(
        """UPDATE registro_residuo
           SET id_punto = ?, id_tipo = ?, cantidad = ?, observaciones = ?
           WHERE id_registro = ?""",
        (datos["id_punto"], datos["id_tipo"], datos["cantidad"],
         datos["observaciones"], id_registro),
    )


def eliminar_registro(id_registro):
    return ejecutar("DELETE FROM registro_residuo WHERE id_registro = ?", (id_registro,))


# ----------------------------------------------------------------------
# Consultas de apoyo y de negocio
# ----------------------------------------------------------------------

def listar_tipos(solo_activos=True):
    sql = "SELECT * FROM tipo_residuo"
    if solo_activos:
        sql += " WHERE activo = 1"
    return consultar(sql + " ORDER BY nombre")


def obtener_tipo(id_tipo):
    return consultar(
        "SELECT * FROM tipo_residuo WHERE id_tipo = ? AND activo = 1", (id_tipo,), uno=True
    )


def obtener_usuario_por_correo(correo):
    return consultar("SELECT * FROM usuario WHERE correo = ?", (correo,), uno=True)


def indicadores_generales():
    """KPI del tablero: total reciclado, CO2 evitado y participantes."""
    return consultar(
        """SELECT COUNT(r.id_registro)                       AS total_registros,
                  IFNULL(ROUND(SUM(r.cantidad), 2), 0)       AS total_kg,
                  IFNULL(ROUND(SUM(r.cantidad * t.factor_co2), 2), 0) AS co2_evitado,
                  COUNT(DISTINCT r.id_usuario)               AS participantes
           FROM registro_residuo r
           INNER JOIN tipo_residuo t ON t.id_tipo = r.id_tipo""",
        uno=True,
    )


def estadisticas_por_localidad():
    return consultar(
        """SELECT p.localidad,
                  ROUND(SUM(r.cantidad), 2) AS total_kg,
                  ROUND(SUM(r.cantidad * t.factor_co2), 2) AS co2_evitado
           FROM registro_residuo r
           INNER JOIN punto_reciclaje p ON p.id_punto = r.id_punto
           INNER JOIN tipo_residuo    t ON t.id_tipo  = r.id_tipo
           GROUP BY p.localidad
           ORDER BY total_kg DESC"""
    )


def estadisticas_por_tipo():
    return consultar(
        """SELECT t.nombre AS tipo, t.categoria,
                  ROUND(SUM(r.cantidad), 2) AS total_kg,
                  ROUND(SUM(r.cantidad * t.factor_co2), 2) AS co2_evitado
           FROM registro_residuo r
           INNER JOIN tipo_residuo t ON t.id_tipo = r.id_tipo
           GROUP BY t.id_tipo
           ORDER BY total_kg DESC"""
    )


def generar_reporte(id_usuario, fecha_inicio, fecha_fin):
    """RF: consolida los registros de un periodo y persiste el reporte."""
    resumen = consultar(
        """SELECT IFNULL(ROUND(SUM(r.cantidad), 2), 0) AS total_kg,
                  IFNULL(ROUND(SUM(r.cantidad * t.factor_co2), 2), 0) AS co2_evitado
           FROM registro_residuo r
           INNER JOIN tipo_residuo t ON t.id_tipo = r.id_tipo
           WHERE r.id_usuario = ? AND DATE(r.fecha_registro) BETWEEN ? AND ?""",
        (id_usuario, fecha_inicio, fecha_fin), uno=True,
    )
    id_reporte = ejecutar(
        """INSERT INTO reporte_ambiental
           (id_usuario, fecha_inicio, fecha_fin, total_kg, co2_evitado)
           VALUES (?, ?, ?, ?, ?)""",
        (id_usuario, fecha_inicio, fecha_fin,
         resumen["total_kg"], resumen["co2_evitado"]),
    )
    return id_reporte, resumen


def listar_reportes(id_usuario=None):
    sql = """SELECT rep.*, u.nombre AS usuario
             FROM reporte_ambiental rep
             INNER JOIN usuario u ON u.id_usuario = rep.id_usuario"""
    parametros = ()
    if id_usuario:
        sql += " WHERE rep.id_usuario = ?"
        parametros = (id_usuario,)
    return consultar(sql + " ORDER BY rep.fecha_generacion DESC", parametros)
