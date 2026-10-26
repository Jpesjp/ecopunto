"""Pruebas del cálculo de CO2, tablero y reportes (RF4, RF5, RF6) - HU-07, HU-08, HU-11."""
import pytest

import database as bd
from conftest import ADMIN, iniciar_sesion

# Oráculo independiente: cantidades y factores tomados de seed.sql
FACTOR = {1: 1.32, 2: 2.15, 3: 0.58, 4: 8.9, 5: 3.4, 6: 2.7}
SEED = [  # (id_usuario, id_tipo, cantidad, fecha)
    (2, 1, 12.5, "2026-08-03"), (2, 2, 8.2, "2026-08-10"), (2, 3, 15.0, "2026-08-17"),
    (3, 4, 3.8, "2026-08-21"), (3, 1, 22.4, "2026-08-28"), (3, 5, 6.1, "2026-09-04"),
    (2, 6, 4.5, "2026-09-09"), (3, 2, 11.3, "2026-09-14"),
]


def esperado(usuario=None, desde="0000", hasta="9999"):
    filas = [s for s in SEED if (usuario is None or s[0] == usuario) and desde <= s[3] <= hasta]
    return round(sum(c for _, _, c, _ in filas), 2), round(sum(c * FACTOR[t] for _, t, c, _ in filas), 2)


def test_cp_i01_co2_por_registro_es_cantidad_por_factor():
    registros = bd.listar_registros()
    assert len(registros) == len(SEED)
    for r in registros:
        assert r["co2_evitado"] == round(r["cantidad"] * r["factor_co2"], 2)
    assert next(r for r in registros if r["id_registro"] == 1)["co2_evitado"] == 16.5


def test_cp_i02_indicadores_generales_del_tablero():
    total_kg, co2 = esperado()
    kpi = bd.indicadores_generales()
    assert kpi["total_kg"] == total_kg == 83.8
    assert kpi["co2_evitado"] == co2
    assert kpi["total_registros"] == 8 and kpi["participantes"] == 2


def test_cp_i03_consolidado_por_localidad_y_tipo():
    por_localidad = {f["localidad"]: f["total_kg"] for f in bd.estadisticas_por_localidad()}
    assert por_localidad["Kennedy"] == 26.2 and sum(por_localidad.values()) == pytest.approx(83.8)
    por_tipo = {f["tipo"]: f["total_kg"] for f in bd.estadisticas_por_tipo()}
    assert por_tipo["Papel y carton"] == 34.9


def test_cp_i04_cambio_de_factor_se_refleja_sin_tocar_codigo():
    bd.ejecutar("UPDATE tipo_residuo SET factor_co2 = 2.0 WHERE id_tipo = 1")
    registro = next(r for r in bd.listar_registros() if r["id_registro"] == 1)
    assert registro["co2_evitado"] == 25.0


def test_cp_i05_usuario_sin_registros_obtiene_cero():
    _, resumen = bd.generar_reporte(1, "2026-01-01", "2026-12-31")
    assert resumen["total_kg"] == 0 and resumen["co2_evitado"] == 0


def test_cp_i06_reporte_por_periodo_se_calcula_y_persiste():
    antes = len(bd.listar_reportes())
    id_reporte, resumen = bd.generar_reporte(2, "2026-08-01", "2026-08-31")
    assert (resumen["total_kg"], resumen["co2_evitado"]) == esperado(2, "2026-08-01", "2026-08-31")
    assert len(bd.listar_reportes()) == antes + 1 and id_reporte > 0


def test_cp_i07_reporte_rechaza_rango_invertido(cliente):
    iniciar_sesion(cliente, ADMIN)
    respuesta = cliente.post("/reportes", data={"fecha_inicio": "2026-09-30", "fecha_fin": "2026-08-01"})
    assert b"no puede ser posterior" in respuesta.data


def test_cp_i08_reporte_rechaza_fechas_invalidas(cliente):
    iniciar_sesion(cliente, ADMIN)
    respuesta = cliente.post("/reportes", data={"fecha_inicio": "ayer", "fecha_fin": ""})
    assert b"rango de fechas valido" in respuesta.data


def test_cp_i09_reportes_historicos_del_seed_son_consistentes():
    """DEF-003: los reportes precargados deben coincidir con el cálculo del sistema."""
    for rep in bd.listar_reportes():
        assert (rep["total_kg"], rep["co2_evitado"]) == esperado(
            rep["id_usuario"], rep["fecha_inicio"], rep["fecha_fin"]), f"reporte {rep['id_reporte']}"
