"""Pruebas de autenticación y seguridad (RF1, RNF1, RNF2, RNF3) - HU-01."""
import database as bd
from conftest import ADMIN, LAURA, iniciar_sesion


def test_cp_a01_ingreso_correcto_redirige_al_tablero(cliente):
    respuesta = iniciar_sesion(cliente, LAURA)
    assert respuesta.status_code == 302 and respuesta.headers["Location"].endswith("/")
    with cliente.session_transaction() as sesion:
        assert sesion["rol"] == "ciudadano" and sesion["nombre"] == "Laura Gomez Ramirez"


def test_cp_a02_contrasena_incorrecta_no_crea_sesion(cliente):
    respuesta = iniciar_sesion(cliente, ("laura.gomez@umb.edu.co", "Incorrecta1"))
    assert b"Correo o contrasena incorrectos" in respuesta.data
    with cliente.session_transaction() as sesion:
        assert "id_usuario" not in sesion


def test_cp_a03_correo_no_distingue_mayusculas(cliente):
    respuesta = iniciar_sesion(cliente, ("LAURA.Gomez@UMB.edu.co", "Eco2026*"))
    assert respuesta.status_code == 302


def test_cp_a04_cuenta_inactiva_no_puede_ingresar(cliente):
    bd.ejecutar("UPDATE usuario SET activo = 0 WHERE correo = ?", (LAURA[0],))
    respuesta = iniciar_sesion(cliente, LAURA)
    assert b"inactiva" in respuesta.data


def test_cp_a05_ruta_protegida_sin_sesion_redirige_al_login(cliente):
    for ruta in ("/", "/puntos", "/registros", "/reportes"):
        respuesta = cliente.get(ruta)
        assert respuesta.status_code == 302 and "/login" in respuesta.headers["Location"]


def test_cp_a06_cierre_de_sesion(cliente):
    iniciar_sesion(cliente, ADMIN)
    cliente.get("/logout")
    assert "/login" in cliente.get("/").headers["Location"]


def test_cp_a07_inyeccion_sql_en_el_login_es_rechazada(cliente):
    respuesta = iniciar_sesion(cliente, ("' OR '1'='1' --", "' OR '1'='1"))
    assert b"Correo o contrasena incorrectos" in respuesta.data


def test_cp_a08_contrasenas_cifradas_con_sal(cliente):
    """RNF1: ninguna contraseña en texto plano; hashes distintos aunque la clave sea igual."""
    filas = bd.consultar("SELECT correo, contrasena_hash FROM usuario")
    for fila in filas:
        assert fila["contrasena_hash"].startswith(("scrypt:", "pbkdf2:"))
        assert "Eco2026*" not in fila["contrasena_hash"] and "Admin2026*" not in fila["contrasena_hash"]
    hashes = {f["correo"]: f["contrasena_hash"] for f in filas}
    assert hashes["laura.gomez@umb.edu.co"] != hashes["carlos.pena@umb.edu.co"]
