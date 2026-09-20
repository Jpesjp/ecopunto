"""Genera el diagrama de casos de uso UML del sistema EcoPunto."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyBboxPatch

VERDE = "#2E7D32"
VERDE_OSC = "#1B5E20"
VERDE_CLARO = "#E8F5E9"
GRIS = "#37474F"

fig, ax = plt.subplots(figsize=(12.5, 8.6))
ax.set_xlim(0, 12.5)
ax.set_ylim(0, 8.6)
ax.axis("off")


def actor(x, y, nombre):
    """Dibuja una figura humana de palitos con su etiqueta."""
    ax.add_patch(plt.Circle((x, y + 0.42), 0.17, fill=False, ec=GRIS, lw=1.8))
    ax.plot([x, x], [y + 0.25, y - 0.22], color=GRIS, lw=1.8)          # tronco
    ax.plot([x - 0.28, x + 0.28], [y + 0.08, y + 0.08], color=GRIS, lw=1.8)  # brazos
    ax.plot([x, x - 0.24], [y - 0.22, y - 0.62], color=GRIS, lw=1.8)   # pierna izq
    ax.plot([x, x + 0.24], [y - 0.22, y - 0.62], color=GRIS, lw=1.8)   # pierna der
    ax.text(x, y - 0.88, nombre, ha="center", va="top", fontsize=10.5,
            fontweight="bold", color=GRIS, wrap=True)


def caso(x, y, texto, ancho=2.55, alto=0.82):
    ax.add_patch(Ellipse((x, y), ancho, alto, facecolor=VERDE_CLARO,
                         edgecolor=VERDE, lw=1.6, zorder=3))
    ax.text(x, y, texto, ha="center", va="center", fontsize=8.8,
            color="#1A1A1A", zorder=4)
    return (x, y, ancho, alto)


def asociar(ax_, actor_xy, caso_xy):
    (xa, ya) = actor_xy
    (xc, yc, w, h) = caso_xy
    borde = xc - w / 2 - 0.03 if xa < xc else xc + w / 2 + 0.03
    ax_.plot([xa, borde], [ya, yc], color=GRIS, lw=1.1, zorder=1)


# ---------------- frontera del sistema ----------------
ax.add_patch(FancyBboxPatch((3.05, 0.75), 6.35, 7.25,
                            boxstyle="round,pad=0.02,rounding_size=0.08",
                            facecolor="#FAFDFA", edgecolor=VERDE_OSC,
                            lw=2.0, zorder=0))
ax.text(6.225, 7.72, "Sistema EcoPunto", ha="center", va="center",
        fontsize=13, fontweight="bold", color=VERDE_OSC, zorder=2)

# ---------------- casos de uso ----------------
cu01 = caso(6.225, 6.95, "CU-01  Iniciar sesión")

izq_x = 4.50
cu02 = caso(izq_x, 6.00, "CU-02  Consultar puntos\nde reciclaje")
cu03 = caso(izq_x, 4.95, "CU-03  Registrar entrega\nde residuo")
cu04 = caso(izq_x, 3.90, "CU-04  Editar registro\npropio")
cu05 = caso(izq_x, 2.85, "CU-05  Eliminar registro\npropio")
cu06 = caso(izq_x, 1.70, "CU-06  Generar reporte\nambiental")

der_x = 7.95
cu07 = caso(der_x, 5.50, "CU-07  Administrar puntos\nde reciclaje")
cu08 = caso(der_x, 4.10, "CU-08  Consultar tablero\nde indicadores")
cu09 = caso(der_x, 2.20, "CU-09  Consumir API de\npuntos e indicadores")

# ---------------- actores ----------------
actor(1.45, 4.30, "Ciudadano")
actor(11.10, 5.60, "Administrador\nambiental")
actor(11.10, 2.30, "Sistema externo")

ciudadano = (1.45, 4.30)
admin = (11.10, 5.60)
externo = (11.10, 2.30)

for c in (cu01, cu02, cu03, cu04, cu05, cu06):
    asociar(ax, ciudadano, c)
for c in (cu01, cu07, cu08):
    asociar(ax, admin, c)
asociar(ax, externo, cu09)

plt.tight_layout(pad=0.4)
plt.savefig("/home/claude/ecopunto/diagramas/casos_uso.png", dpi=150,
            facecolor="white", bbox_inches="tight")
print("Diagrama de casos de uso generado")
