"""
EcoPunto - Plataforma web para la gestion y trazabilidad de residuos reciclables
Universidad Manuela Beltran - Facultad de Ingenieria de Software
Asignaturas: Estandares y Metricas de Software / Ingenieria Web

Arquitectura: cliente-servidor de tres capas, patron MVC.
  - Modelo      -> database.py
  - Vista       -> templates/ (Jinja2 + Bootstrap 5)
  - Controlador -> este archivo (rutas Flask)

Ejecucion:
    pip install -r requirements.txt
    python app.py
    Navegador: http://127.0.0.1:5000
"""

import math
from datetime import date, datetime
from functools import wraps

from flask import (Flask, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash

import database as bd

app = Flask(__name__)
app.config["SECRET_KEY"] = "ecopunto-umb-2026-clave-desarrollo"

LOCALIDADES = ["Usaquen", "Chapinero", "Santa Fe", "Teusaquillo", "Suba",
               "Kennedy", "Engativa", "Bosa", "Fontibon", "Puente Aranda"]
ESTADOS_PUNTO = ["activo", "inactivo", "mantenimiento"]


# ======================================================================
# Utilidades y control de acceso (RNF de seguridad)
# ======================================================================

def login_requerido(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if "id_usuario" not in session:
            flash("Debe iniciar sesion para acceder a esta seccion.", "warning")
            return redirect(url_for("login"))
        return funcion(*args, **kwargs)
    return envoltura


def admin_requerido(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if session.get("rol") != "administrador":
            flash("Esta accion requiere perfil de administrador.", "danger")
            return redirect(url_for("listar_puntos"))
        return funcion(*args, **kwargs)
    return envoltura


def validar_punto(formulario):
    """Validacion de reglas de negocio del formulario de puntos."""
    errores = []
    if len(formulario.get("nombre", "").strip()) < 5:
        errores.append("El nombre del punto debe tener al menos 5 caracteres.")
    if not formulario.get("direccion", "").strip():
        errores.append("La direccion es obligatoria.")
    if formulario.get("localidad") not in LOCALIDADES:
        errores.append("Debe seleccionar una localidad valida de Bogota.")
    if formulario.get("estado") not in ESTADOS_PUNTO:
        errores.append("El estado del punto no es valido.")
    for campo, minimo, maximo in (("latitud", -90, 90), ("longitud", -180, 180)):
        valor = formulario.get(campo, "").strip()
        if valor:
            try:
                if not minimo <= float(valor) <= maximo:
                    errores.append(f"La {campo} debe estar entre {minimo} y {maximo}.")
            except ValueError:
                errores.append(f"La {campo} debe ser un valor numerico.")
    return errores


def validar_registro(formulario):
    """Validacion de reglas de negocio del formulario de registros."""
    errores = []
    id_punto = formulario.get("id_punto", "")
    id_tipo = formulario.get("id_tipo", "")
    # DEF-002: el punto y el tipo deben existir; un id inexistente generaba error 500
    if not id_punto.isdigit() or bd.obtener_punto(int(id_punto)) is None:
        errores.append("Debe seleccionar un punto de reciclaje.")
    if not id_tipo.isdigit() or bd.obtener_tipo(int(id_tipo)) is None:
        errores.append("Debe seleccionar un tipo de residuo.")
    try:
        cantidad = float(formulario.get("cantidad", ""))
        if not math.isfinite(cantidad):
            # DEF-001: float("nan") superaba las validaciones y fallaba en la BD
            errores.append("La cantidad debe ser un valor numerico.")
        elif cantidad <= 0:
            errores.append("La cantidad debe ser mayor que cero.")
        elif cantidad > 1000:
            errores.append("La cantidad maxima por registro es de 1000 kg.")
    except ValueError:
        errores.append("La cantidad debe ser un valor numerico.")
    if len(formulario.get("observaciones", "")) > 250:
        errores.append("Las observaciones no pueden superar 250 caracteres.")
    return errores


def numero_o_none(valor):
    valor = (valor or "").strip()
    return float(valor) if valor else None


# ======================================================================
# Autenticacion  (RF1)
# ======================================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        contrasena = request.form.get("contrasena", "")
        usuario = bd.obtener_usuario_por_correo(correo)

        if usuario and check_password_hash(usuario["contrasena_hash"], contrasena):
            if not usuario["activo"]:
                flash("La cuenta se encuentra inactiva.", "danger")
                return render_template("login.html")
            session["id_usuario"] = usuario["id_usuario"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            flash(f"Bienvenido(a), {usuario['nombre']}.", "success")
            return redirect(url_for("tablero"))

        flash("Correo o contrasena incorrectos.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesion finalizada correctamente.", "info")
    return redirect(url_for("login"))


# ======================================================================
# Tablero de indicadores  (RF6)
# ======================================================================

@app.route("/")
@login_requerido
def tablero():
    return render_template(
        "tablero.html",
        indicadores=bd.indicadores_generales(),
        por_localidad=bd.estadisticas_por_localidad(),
        por_tipo=bd.estadisticas_por_tipo(),
    )


# ======================================================================
# CRUD COMPLETO: PUNTO_RECICLAJE  (RF2)
# ======================================================================

@app.route("/puntos")
@login_requerido
def listar_puntos():
    busqueda = request.args.get("q", "").strip()
    return render_template(
        "puntos_lista.html",
        puntos=bd.listar_puntos(busqueda or None),
        busqueda=busqueda,
    )


@app.route("/puntos/nuevo", methods=["GET", "POST"])
@login_requerido
@admin_requerido
def crear_punto():
    if request.method == "POST":
        errores = validar_punto(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("punto_form.html", punto=dict(request.form),
                                   localidades=LOCALIDADES, estados=ESTADOS_PUNTO,
                                   accion="Crear")
        bd.crear_punto({
            "nombre": request.form["nombre"].strip(),
            "direccion": request.form["direccion"].strip(),
            "localidad": request.form["localidad"],
            "latitud": numero_o_none(request.form.get("latitud")),
            "longitud": numero_o_none(request.form.get("longitud")),
            "horario": request.form.get("horario", "").strip(),
            "estado": request.form["estado"],
        })
        flash("Punto de reciclaje creado correctamente.", "success")
        return redirect(url_for("listar_puntos"))

    return render_template("punto_form.html", punto=None, localidades=LOCALIDADES,
                           estados=ESTADOS_PUNTO, accion="Crear")


@app.route("/puntos/<int:id_punto>/editar", methods=["GET", "POST"])
@login_requerido
@admin_requerido
def editar_punto(id_punto):
    punto = bd.obtener_punto(id_punto)
    if punto is None:
        flash("El punto solicitado no existe.", "danger")
        return redirect(url_for("listar_puntos"))

    if request.method == "POST":
        errores = validar_punto(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("punto_form.html", punto=dict(request.form),
                                   localidades=LOCALIDADES, estados=ESTADOS_PUNTO,
                                   accion="Actualizar")
        bd.actualizar_punto(id_punto, {
            "nombre": request.form["nombre"].strip(),
            "direccion": request.form["direccion"].strip(),
            "localidad": request.form["localidad"],
            "latitud": numero_o_none(request.form.get("latitud")),
            "longitud": numero_o_none(request.form.get("longitud")),
            "horario": request.form.get("horario", "").strip(),
            "estado": request.form["estado"],
        })
        flash("Punto de reciclaje actualizado correctamente.", "success")
        return redirect(url_for("listar_puntos"))

    return render_template("punto_form.html", punto=dict(punto), localidades=LOCALIDADES,
                           estados=ESTADOS_PUNTO, accion="Actualizar")


@app.route("/puntos/<int:id_punto>/eliminar", methods=["POST"])
@login_requerido
@admin_requerido
def eliminar_punto(id_punto):
    if bd.obtener_punto(id_punto) is None:
        flash("El punto solicitado no existe.", "danger")
    elif bd.punto_tiene_registros(id_punto):
        flash("No se puede eliminar: el punto tiene registros asociados "
              "(integridad referencial).", "warning")
    else:
        bd.eliminar_punto(id_punto)
        flash("Punto de reciclaje eliminado.", "success")
    return redirect(url_for("listar_puntos"))


# ======================================================================
# CRUD COMPLETO: REGISTRO_RESIDUO  (RF3)
# ======================================================================

@app.route("/registros")
@login_requerido
def listar_registros():
    solo_mios = session.get("rol") != "administrador"
    registros = bd.listar_registros(session["id_usuario"] if solo_mios else None)
    return render_template("registros_lista.html", registros=registros,
                           solo_mios=solo_mios)


@app.route("/registros/nuevo", methods=["GET", "POST"])
@login_requerido
def crear_registro():
    if request.method == "POST":
        errores = validar_registro(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
        else:
            bd.crear_registro({
                "id_usuario": session["id_usuario"],
                "id_punto": int(request.form["id_punto"]),
                "id_tipo": int(request.form["id_tipo"]),
                "cantidad": float(request.form["cantidad"]),
                "observaciones": request.form.get("observaciones", "").strip(),
            })
            flash("Registro de residuo guardado correctamente.", "success")
            return redirect(url_for("listar_registros"))

    return render_template("registro_form.html", registro=dict(request.form) or None,
                           puntos=bd.listar_puntos(), tipos=bd.listar_tipos(),
                           accion="Registrar")


@app.route("/registros/<int:id_registro>/editar", methods=["GET", "POST"])
@login_requerido
def editar_registro(id_registro):
    registro = bd.obtener_registro(id_registro)
    if registro is None:
        flash("El registro solicitado no existe.", "danger")
        return redirect(url_for("listar_registros"))
    if (registro["id_usuario"] != session["id_usuario"]
            and session.get("rol") != "administrador"):
        flash("Solo puede modificar sus propios registros.", "danger")
        return redirect(url_for("listar_registros"))

    if request.method == "POST":
        errores = validar_registro(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
        else:
            bd.actualizar_registro(id_registro, {
                "id_punto": int(request.form["id_punto"]),
                "id_tipo": int(request.form["id_tipo"]),
                "cantidad": float(request.form["cantidad"]),
                "observaciones": request.form.get("observaciones", "").strip(),
            })
            flash("Registro actualizado correctamente.", "success")
            return redirect(url_for("listar_registros"))

    return render_template("registro_form.html", registro=dict(registro),
                           puntos=bd.listar_puntos(), tipos=bd.listar_tipos(),
                           accion="Actualizar")


@app.route("/registros/<int:id_registro>/eliminar", methods=["POST"])
@login_requerido
def eliminar_registro(id_registro):
    registro = bd.obtener_registro(id_registro)
    if registro is None:
        flash("El registro solicitado no existe.", "danger")
    elif (registro["id_usuario"] != session["id_usuario"]
            and session.get("rol") != "administrador"):
        flash("Solo puede eliminar sus propios registros.", "danger")
    else:
        bd.eliminar_registro(id_registro)
        flash("Registro eliminado correctamente.", "success")
    return redirect(url_for("listar_registros"))


# ======================================================================
# Reportes ambientales  (RF5)
# ======================================================================

@app.route("/reportes", methods=["GET", "POST"])
@login_requerido
def reportes():
    resumen = None
    if request.method == "POST":
        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")
        try:
            inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            if inicio > fin:
                flash("La fecha inicial no puede ser posterior a la final.", "danger")
            else:
                _, resumen = bd.generar_reporte(session["id_usuario"],
                                                fecha_inicio, fecha_fin)
                flash("Reporte ambiental generado y almacenado.", "success")
        except (TypeError, ValueError):
            flash("Debe indicar un rango de fechas valido.", "danger")

    solo_mios = session.get("rol") != "administrador"
    return render_template(
        "reportes.html",
        reportes=bd.listar_reportes(session["id_usuario"] if solo_mios else None),
        resumen=resumen, hoy=date.today().isoformat(),
    )


# ======================================================================
# API REST  (RF7) - Ingenieria Web: servicios JSON sin estado
# ======================================================================

@app.route("/api/v1/puntos", methods=["GET"])
def api_puntos():
    localidad = request.args.get("localidad")
    puntos = [dict(fila) for fila in bd.listar_puntos(localidad)]
    return jsonify({"total": len(puntos), "datos": puntos}), 200


@app.route("/api/v1/puntos/<int:id_punto>", methods=["GET"])
def api_punto(id_punto):
    punto = bd.obtener_punto(id_punto)
    if punto is None:
        return jsonify({"error": "Punto de reciclaje no encontrado"}), 404
    return jsonify(dict(punto)), 200


@app.route("/api/v1/indicadores", methods=["GET"])
def api_indicadores():
    return jsonify({
        "generales": dict(bd.indicadores_generales()),
        "por_localidad": [dict(f) for f in bd.estadisticas_por_localidad()],
        "por_tipo": [dict(f) for f in bd.estadisticas_por_tipo()],
    }), 200


@app.errorhandler(404)
def error_404(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Recurso no encontrado"}), 404
    return render_template("error.html", codigo=404,
                           mensaje="La pagina solicitada no existe."), 404


@app.errorhandler(500)
def error_500(_):
    return render_template("error.html", codigo=500,
                           mensaje="Error interno del servidor."), 500


if __name__ == "__main__":
    if bd.inicializar_bd():
        print("Base de datos creada con datos de prueba en ecopunto.db")
    print("EcoPunto ejecutandose en http://127.0.0.1:5000")
    app.run(debug=True)
