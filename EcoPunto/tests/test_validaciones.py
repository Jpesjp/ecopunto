"""Pruebas unitarias de las reglas de negocio (RF9 / RNF10).
Técnicas: partición de equivalencia y análisis de valores límite."""
import pytest

from app import numero_o_none, validar_punto, validar_registro
from conftest import PUNTO_VALIDO, REGISTRO_VALIDO


def punto(**cambios):
    return {**PUNTO_VALIDO, **cambios}


def registro(**cambios):
    return {**REGISTRO_VALIDO, **cambios}


# ---------------------------------------------------------------- RF2 / RF9
def test_cp_v01_punto_valido_no_genera_errores():
    assert validar_punto(punto()) == []


@pytest.mark.parametrize("nombre, valido", [("Abcd", False), ("Abcde", True), ("   Abcd   ", False)])
def test_cp_v02_limite_longitud_nombre_punto(nombre, valido):
    errores = validar_punto(punto(nombre=nombre))
    assert (errores == []) is valido


def test_cp_v03_direccion_obligatoria():
    assert "La direccion es obligatoria." in validar_punto(punto(direccion="  "))


@pytest.mark.parametrize("localidad", ["Marte", "kennedy", ""])
def test_cp_v04_localidad_fuera_del_listado_oficial(localidad):
    assert "Debe seleccionar una localidad valida de Bogota." in validar_punto(punto(localidad=localidad))


@pytest.mark.parametrize("estado", ["volando", "ACTIVO", ""])
def test_cp_v05_estado_no_permitido(estado):
    assert "El estado del punto no es valido." in validar_punto(punto(estado=estado))


@pytest.mark.parametrize("campo, valor, valido", [
    ("latitud", "-90", True), ("latitud", "90", True),
    ("latitud", "90.000001", False), ("latitud", "-90.000001", False),
    ("longitud", "180", True), ("longitud", "-180.5", False),
    ("latitud", "cuatro", False), ("latitud", "", True),
])
def test_cp_v06_limites_de_coordenadas(campo, valor, valido):
    assert (validar_punto(punto(**{campo: valor})) == []) is valido


# ---------------------------------------------------------------- RF3 / RF9
@pytest.mark.parametrize("cantidad, valido", [
    ("0", False), ("0.01", True), ("1000", True), ("1000.01", False),
    ("-5", False), ("abc", False), ("", False),
])
def test_cp_v07_limites_de_cantidad(cantidad, valido):
    assert (validar_registro(registro(cantidad=cantidad)) == []) is valido


@pytest.mark.parametrize("cantidad", ["nan", "NaN", "inf"])
def test_cp_v08_rechaza_cantidades_no_finitas(cantidad):
    """DEF-001: 'nan' no es un número válido y debe rechazarse con un mensaje."""
    assert validar_registro(registro(cantidad=cantidad)) != []


@pytest.mark.parametrize("longitud, valido", [(250, True), (251, False)])
def test_cp_v09_limite_observaciones(longitud, valido):
    assert (validar_registro(registro(observaciones="x" * longitud)) == []) is valido


@pytest.mark.parametrize("campo", ["id_punto", "id_tipo"])
def test_cp_v10_punto_y_tipo_obligatorios(campo):
    assert validar_registro(registro(**{campo: ""})) != []


def test_cp_v11_conversion_de_coordenadas_opcionales():
    assert numero_o_none("  ") is None
    assert numero_o_none("4.5") == 4.5
