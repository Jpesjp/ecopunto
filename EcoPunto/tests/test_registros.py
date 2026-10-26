"""Pruebas de integración del CRUD de registros de residuos (RF3, RF9) - HU-04, HU-05, HU-06."""
import database as bd
from conftest import ADMIN, REGISTRO_VALIDO, iniciar_sesion


def total_registros():
    return bd.consultar("SELECT COUNT(*) AS n FROM registro_residuo", uno=True)["n"]


def test_cp_r01_ciudadano_registra_entrega_valida(laura):
    antes = total_registros()
    respuesta = laura.post("/registros/nuevo", data=REGISTRO_VALIDO, follow_redirects=True)
    ultimo = bd.consultar("SELECT * FROM registro_residuo ORDER BY id_registro DESC LIMIT 1", uno=True)
    assert total_registros() == antes + 1
    assert ultimo["id_usuario"] == 2 and ultimo["fecha_registro"] is not None
    assert b"Registro de residuo guardado correctamente" in respuesta.data


def test_cp_r02_ciudadano_solo_ve_sus_registros(laura):
    html = laura.get("/registros").data.decode()
    assert "Mis registros de reciclaje" in html
    assert "Latas de bebida" not in html and "Centro de Acopio Kennedy" not in html  # registros de Carlos


def test_cp_r03_ciudadano_corrige_su_registro(laura):
    laura.post("/registros/1/editar", data={**REGISTRO_VALIDO, "cantidad": "9.25"})
    assert float(bd.obtener_registro(1)["cantidad"]) == 9.25


def test_cp_r04_ciudadano_no_edita_registro_ajeno(laura):
    respuesta = laura.post("/registros/4/editar", data={**REGISTRO_VALIDO, "cantidad": "999"},
                           follow_redirects=True)
    assert b"Solo puede modificar sus propios registros" in respuesta.data
    assert float(bd.obtener_registro(4)["cantidad"]) == 3.8


def test_cp_r05_ciudadano_no_elimina_registro_ajeno(laura):
    laura.post("/registros/4/eliminar")
    assert bd.obtener_registro(4) is not None


def test_cp_r06_ciudadano_elimina_su_registro(laura):
    laura.post("/registros/2/eliminar")
    assert bd.obtener_registro(2) is None


def test_cp_r07_administrador_audita_y_edita_cualquier_registro(cliente):
    iniciar_sesion(cliente, ADMIN)
    assert "Laura Gomez Ramirez" in cliente.get("/registros").data.decode()
    cliente.post("/registros/4/editar", data={**REGISTRO_VALIDO, "cantidad": "4.0"})
    assert float(bd.obtener_registro(4)["cantidad"]) == 4.0


def test_cp_r08_cantidad_cero_o_negativa_no_se_persiste(laura):
    antes = total_registros()
    for cantidad in ("0", "-5"):
        respuesta = laura.post("/registros/nuevo", data={**REGISTRO_VALIDO, "cantidad": cantidad})
        assert b"mayor que cero" in respuesta.data
    assert total_registros() == antes


def test_cp_r09_cantidad_superior_a_1000_kg(laura):
    respuesta = laura.post("/registros/nuevo", data={**REGISTRO_VALIDO, "cantidad": "1500"})
    assert b"1000 kg" in respuesta.data


def test_cp_r10_cantidad_nan_se_informa_sin_error_500(laura):
    """DEF-001: con 'nan' la aplicación respondía 500 en lugar de un mensaje de validación."""
    respuesta = laura.post("/registros/nuevo", data={**REGISTRO_VALIDO, "cantidad": "nan"})
    assert respuesta.status_code == 200


def test_cp_r11_punto_inexistente_se_informa_sin_error_500(laura):
    """DEF-002: un id de punto o de tipo inexistente provocaba IntegrityError (500)."""
    for datos in ({**REGISTRO_VALIDO, "id_punto": "999"}, {**REGISTRO_VALIDO, "id_tipo": "abc"}):
        respuesta = laura.post("/registros/nuevo", data=datos)
        assert respuesta.status_code == 200
