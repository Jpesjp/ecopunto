"""Pruebas de integración del CRUD de puntos (RF2, RF8, RF9, RF10, RF11) - HU-02, HU-03, HU-09, HU-10."""
import database as bd
from conftest import PUNTO_VALIDO


def test_cp_p01_admin_crea_punto_valido(admin):
    total = len(bd.listar_puntos())
    respuesta = admin.post("/puntos/nuevo", data=PUNTO_VALIDO, follow_redirects=True)
    assert len(bd.listar_puntos()) == total + 1
    assert b"Punto de reciclaje creado correctamente" in respuesta.data


def test_cp_p02_listado_muestra_datos_y_estado_diferenciado(admin):
    html = admin.get("/puntos").data.decode()
    assert "Centro de Acopio Kennedy" in html and "Carrera 78K # 38-50 Sur" in html
    assert 'badge bg-warning text-dark">Mantenimiento' in html   # HU-02: etiqueta diferenciada


def test_cp_p03_admin_actualiza_punto(admin):
    admin.post("/puntos/3/editar", data={**PUNTO_VALIDO, "nombre": "Centro de Acopio Kennedy",
                                         "localidad": "Kennedy", "estado": "mantenimiento"})
    assert bd.obtener_punto(3)["estado"] == "mantenimiento"


def test_cp_p04_admin_elimina_punto_sin_registros(admin):
    id_nuevo = bd.crear_punto({**PUNTO_VALIDO, "latitud": None, "longitud": None})
    admin.post(f"/puntos/{id_nuevo}/eliminar")
    assert bd.obtener_punto(id_nuevo) is None


def test_cp_p05_integridad_referencial_punto_con_registros(admin):
    respuesta = admin.post("/puntos/1/eliminar", follow_redirects=True)
    assert bd.obtener_punto(1) is not None
    assert b"integridad referencial" in respuesta.data


def test_cp_p06_ciudadano_no_puede_administrar_puntos(laura):
    total = len(bd.listar_puntos())
    respuesta = laura.post("/puntos/nuevo", data=PUNTO_VALIDO, follow_redirects=True)
    assert b"requiere perfil de administrador" in respuesta.data
    assert len(bd.listar_puntos()) == total
    laura.post("/puntos/5/eliminar")
    assert bd.obtener_punto(5) is not None
    laura.post("/puntos/2/editar", data={**PUNTO_VALIDO, "estado": "inactivo"})
    assert bd.obtener_punto(2)["estado"] == "activo"


def test_cp_p07_errores_de_validacion_conservan_lo_diligenciado(admin):
    datos = {**PUNTO_VALIDO, "nombre": "ABC", "direccion": "Calle Prueba 123", "localidad": "Marte"}
    html = admin.post("/puntos/nuevo", data=datos).data.decode()
    assert "al menos 5 caracteres" in html and "localidad valida" in html
    assert 'value="Calle Prueba 123"' in html            # RF9: no se pierde la información


def test_cp_p08_filtro_por_localidad(admin):
    html = admin.get("/puntos?q=Kennedy").data.decode()
    assert "Centro de Acopio Kennedy" in html and "Punto Limpio Suba Rincon" not in html


def test_cp_p09_editar_punto_inexistente(admin):
    respuesta = admin.get("/puntos/999/editar", follow_redirects=True)
    assert b"El punto solicitado no existe" in respuesta.data
