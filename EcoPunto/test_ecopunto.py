"""
EcoPunto - Pruebas funcionales del CRUD y de la API REST.
Evidencia de verificacion segun ISO/IEC 25010 (funcionalidad y fiabilidad).

Ejecucion:  python test_ecopunto.py
"""

import database as bd
from app import app


def encabezado(texto):
    print(f"\n{'=' * 62}\n{texto}\n{'=' * 62}")


def main():
    bd.inicializar_bd(forzar=True)
    print("Base de datos reinicializada con datos de prueba.")
    app.config["TESTING"] = True
    cliente = app.test_client()
    aprobadas = fallidas = 0

    def verificar(descripcion, condicion):
        nonlocal aprobadas, fallidas
        estado = "OK  " if condicion else "FALLA"
        print(f"  [{estado}] {descripcion}")
        if condicion:
            aprobadas += 1
        else:
            fallidas += 1

    encabezado("PRUEBA 1 - Autenticacion de usuarios (RF1)")
    respuesta = cliente.post("/login", data={"correo": "admin@umb.edu.co",
                                             "contrasena": "incorrecta"})
    verificar("Rechaza credenciales invalidas", b"incorrectos" in respuesta.data)
    respuesta = cliente.post("/login", data={"correo": "admin@umb.edu.co",
                                             "contrasena": "Admin2026*"},
                             follow_redirects=True)
    verificar("Permite el ingreso del administrador", b"Bienvenido" in respuesta.data)

    encabezado("PRUEBA 2 - CRUD de PUNTO_RECICLAJE (RF2)")
    total_inicial = len(bd.listar_puntos())
    cliente.post("/puntos/nuevo", data={
        "nombre": "Punto Verde Engativa Norte", "direccion": "Calle 80 # 96-20",
        "localidad": "Engativa", "latitud": "4.712300", "longitud": "-74.115600",
        "horario": "Lunes a viernes 8:00 - 17:00", "estado": "activo"},
        follow_redirects=True)
    puntos = bd.listar_puntos()
    verificar("CREATE: inserta un nuevo punto", len(puntos) == total_inicial + 1)

    nuevo = bd.consultar("SELECT * FROM punto_reciclaje WHERE nombre = ?",
                         ("Punto Verde Engativa Norte",), uno=True)
    verificar("READ: recupera el punto creado", nuevo is not None)

    cliente.post(f"/puntos/{nuevo['id_punto']}/editar", data={
        "nombre": "Punto Verde Engativa Norte", "direccion": "Calle 80 # 96-20",
        "localidad": "Engativa", "latitud": "4.712300", "longitud": "-74.115600",
        "horario": "Lunes a sabado 7:00 - 18:00", "estado": "mantenimiento"},
        follow_redirects=True)
    editado = bd.obtener_punto(nuevo["id_punto"])
    verificar("UPDATE: modifica horario y estado",
              editado["estado"] == "mantenimiento")

    cliente.post(f"/puntos/{nuevo['id_punto']}/eliminar", follow_redirects=True)
    verificar("DELETE: elimina el punto sin registros asociados",
              bd.obtener_punto(nuevo["id_punto"]) is None)

    respuesta = cliente.post("/puntos/1/eliminar", follow_redirects=True)
    verificar("Protege la integridad referencial (punto con registros)",
              bd.obtener_punto(1) is not None)

    encabezado("PRUEBA 3 - Validacion de datos de entrada (RNF)")
    respuesta = cliente.post("/puntos/nuevo", data={
        "nombre": "ABC", "direccion": "", "localidad": "Marte",
        "latitud": "999", "longitud": "", "horario": "", "estado": "volando"})
    verificar("Rechaza nombre corto", b"al menos 5 caracteres" in respuesta.data)
    verificar("Rechaza direccion vacia", b"direccion es obligatoria" in respuesta.data)
    verificar("Rechaza localidad inexistente", b"localidad valida" in respuesta.data)

    encabezado("PRUEBA 4 - CRUD de REGISTRO_RESIDUO (RF3)")
    cliente.get("/logout")
    cliente.post("/login", data={"correo": "laura.gomez@umb.edu.co",
                                 "contrasena": "Eco2026*"})
    total_inicial = len(bd.listar_registros())
    cliente.post("/registros/nuevo", data={
        "id_punto": "2", "id_tipo": "3", "cantidad": "7.5",
        "observaciones": "Prueba automatizada"}, follow_redirects=True)
    verificar("CREATE: inserta un registro de residuo",
              len(bd.listar_registros()) == total_inicial + 1)

    ultimo = bd.consultar(
        "SELECT * FROM registro_residuo ORDER BY id_registro DESC LIMIT 1", uno=True)
    cliente.post(f"/registros/{ultimo['id_registro']}/editar", data={
        "id_punto": "2", "id_tipo": "3", "cantidad": "9.25",
        "observaciones": "Cantidad corregida"}, follow_redirects=True)
    verificar("UPDATE: modifica la cantidad registrada",
              float(bd.obtener_registro(ultimo["id_registro"])["cantidad"]) == 9.25)

    respuesta = cliente.post("/registros/nuevo", data={
        "id_punto": "2", "id_tipo": "3", "cantidad": "-5", "observaciones": ""})
    verificar("Rechaza cantidades negativas", b"mayor que cero" in respuesta.data)

    cliente.post(f"/registros/{ultimo['id_registro']}/eliminar", follow_redirects=True)
    verificar("DELETE: elimina el registro",
              bd.obtener_registro(ultimo["id_registro"]) is None)

    encabezado("PRUEBA 5 - Calculo de CO2 y reporte ambiental (RF4 y RF5)")
    _, resumen = bd.generar_reporte(2, "2026-08-01", "2026-09-30")
    verificar("Calcula el total de kilogramos del periodo", resumen["total_kg"] > 0)
    verificar("Calcula el CO2 evitado del periodo", resumen["co2_evitado"] > 0)

    encabezado("PRUEBA 6 - API REST e indicadores (RF6, RF7 y RF11)")
    respuesta = cliente.get("/api/v1/puntos")
    datos = respuesta.get_json()
    verificar("GET /api/v1/puntos responde 200", respuesta.status_code == 200)
    verificar("La respuesta contiene la coleccion de puntos", datos["total"] > 0)

    respuesta = cliente.get("/api/v1/puntos/9999")
    verificar("GET de un recurso inexistente responde 404",
              respuesta.status_code == 404)

    respuesta = cliente.get("/api/v1/indicadores")
    verificar("GET /api/v1/indicadores entrega los KPI",
              respuesta.get_json()["generales"]["total_kg"] > 0)

    encabezado("RESULTADO DE LA EJECUCION")
    total = aprobadas + fallidas
    print(f"  Pruebas ejecutadas : {total}")
    print(f"  Aprobadas          : {aprobadas}")
    print(f"  Fallidas           : {fallidas}")
    print(f"  Cobertura de exito : {aprobadas / total * 100:.1f} %\n")


if __name__ == "__main__":
    main()
