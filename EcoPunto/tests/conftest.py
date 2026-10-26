"""
Configuración común de la suite de pruebas de EcoPunto (pytest).

Cada prueba trabaja sobre una base de datos SQLite temporal, creada desde
schema.sql y seed.sql, de modo que:
  - nunca se modifica el archivo ecopunto.db del proyecto, y
  - todas las pruebas parten del mismo estado conocido (repetibilidad).
"""
import os
import sys

import pytest

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import database as bd  # noqa: E402
from app import app as flask_app  # noqa: E402

ADMIN = ("admin@umb.edu.co", "Admin2026*")
LAURA = ("laura.gomez@umb.edu.co", "Eco2026*")   # ciudadano, id_usuario = 2
CARLOS = ("carlos.pena@umb.edu.co", "Eco2026*")  # ciudadano, id_usuario = 3


@pytest.fixture(autouse=True)
def bd_temporal(tmp_path, monkeypatch):
    """Redirige la aplicación a una BD temporal y la inicializa con el seed."""
    monkeypatch.setattr(bd, "DB_PATH", str(tmp_path / "ecopunto_test.db"))
    bd.inicializar_bd(forzar=True)
    yield


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
    return flask_app


@pytest.fixture
def cliente(app):
    return app.test_client()


def iniciar_sesion(cliente, credenciales):
    correo, contrasena = credenciales
    return cliente.post("/login", data={"correo": correo, "contrasena": contrasena})


@pytest.fixture
def admin(cliente):
    iniciar_sesion(cliente, ADMIN)
    return cliente


@pytest.fixture
def laura(cliente):
    iniciar_sesion(cliente, LAURA)
    return cliente


PUNTO_VALIDO = {
    "nombre": "Punto Verde Engativa Norte",
    "direccion": "Calle 80 # 96-20",
    "localidad": "Engativa",
    "latitud": "4.712300",
    "longitud": "-74.115600",
    "horario": "Lunes a viernes 8:00 - 17:00",
    "estado": "activo",
}

REGISTRO_VALIDO = {"id_punto": "2", "id_tipo": "3", "cantidad": "7.5",
                   "observaciones": "Prueba automatizada"}
