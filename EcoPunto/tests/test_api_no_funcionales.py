"""Pruebas de la API REST (RF7, RF11) y de requisitos no funcionales (RNF4, RNF6, RNF7) - HU-12."""
import random
import time

import database as bd


def test_cp_api01_lista_de_puntos(cliente):
    respuesta = cliente.get("/api/v1/puntos")
    datos = respuesta.get_json()
    assert respuesta.status_code == 200 and respuesta.is_json
    assert datos["total"] == 5 == len(datos["datos"])


def test_cp_api02_filtro_por_localidad(cliente):
    datos = cliente.get("/api/v1/puntos?localidad=Kennedy").get_json()
    assert datos["total"] == 1 and datos["datos"][0]["localidad"] == "Kennedy"


def test_cp_api03_consulta_de_un_punto(cliente):
    datos = cliente.get("/api/v1/puntos/1").get_json()
    assert datos["nombre"] == "EcoPunto UMB Sede Centro"


def test_cp_api04_punto_inexistente_responde_404_json(cliente):
    respuesta = cliente.get("/api/v1/puntos/9999")
    assert respuesta.status_code == 404 and "error" in respuesta.get_json()


def test_cp_api05_indicadores_consolidados(cliente):
    datos = cliente.get("/api/v1/indicadores").get_json()
    assert set(datos) == {"generales", "por_localidad", "por_tipo"}
    assert datos["generales"]["total_kg"] == 83.8


def test_cp_api06_api_no_requiere_sesion_y_es_solo_lectura(cliente):
    assert cliente.post("/api/v1/puntos").status_code == 405


def test_cp_nf01_rutas_inexistentes_controladas(cliente):
    """RNF4: la API responde JSON y la web una página controlada, sin trazas."""
    api = cliente.get("/api/v1/no-existe")
    assert api.status_code == 404 and api.get_json()["error"] == "Recurso no encontrado"
    web = cliente.get("/pagina-inexistente")
    assert web.status_code == 404 and b"Traceback" not in web.data


def test_cp_nf02_indices_de_consultas_frecuentes():
    """RNF7: índices sobre fecha_registro, id_usuario y localidad."""
    indices = {f["name"] for f in bd.consultar("SELECT name FROM sqlite_master WHERE type = 'index'")}
    assert {"idx_registro_fecha", "idx_registro_usuario", "idx_punto_localidad"} <= indices


def test_cp_nf03_tablero_responde_en_menos_de_2_s_con_10000_registros(cliente):
    """RNF6: comportamiento temporal con datos de carga simulados."""
    random.seed(2026)
    filas = [(random.choice((2, 3)), random.randint(1, 5), random.randint(1, 6),
              round(random.uniform(0.5, 50), 2), f"2026-{random.randint(1, 9):02d}-{random.randint(1, 28):02d} 10:00:00")
             for _ in range(10_000)]
    with bd.get_connection() as conexion:
        conexion.executemany("INSERT INTO registro_residuo (id_usuario, id_punto, id_tipo, cantidad, fecha_registro)"
                             " VALUES (?, ?, ?, ?, ?)", filas)
    cliente.post("/login", data={"correo": "admin@umb.edu.co", "contrasena": "Admin2026*"})
    for ruta in ("/", "/api/v1/indicadores"):
        inicio = time.perf_counter()
        respuesta = cliente.get(ruta)
        duracion = time.perf_counter() - inicio
        print(f"\n  RNF6 {ruta}: {duracion * 1000:.1f} ms")
        assert respuesta.status_code == 200 and duracion < 2.0
