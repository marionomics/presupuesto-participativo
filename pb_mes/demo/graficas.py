"""
Gráficas y tablas para comparar reglas de conteo.

Los colores son los mismos de la presentación, para que las figuras del
notebook y las diapositivas se lean como una sola cosa.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pb_mes.demo.escenario import Escenario
from pb_mes.demo.reglas import Resultado

# ── paleta, igual que presentation/main.tex ───────────────────────────
COLORES = {
    "Conteo simple": "#8B1A1A",
    "Elecciones por distrito": "#4A4A8A",
    "Partes Iguales": "#1A6B3A",
    "Partes Iguales (sin completar)": "#1A6B3A",
    "Partes Iguales (completado codicioso)": "#1A6B3A",
}
ACENTO = "#D4A017"
_GRIS = "#5A5A5A"


def _color(regla: str) -> str:
    return COLORES.get(regla, _GRIS)


def _paleta(resultados: list[Resultado]) -> list:
    """Un color por resultado, aclarando los que comparten color base.

    Las variantes de una misma regla —por ejemplo las tres formas de repartir
    el sobrante del Método de Partes Iguales— tienen el mismo color asignado.
    Si se grafican juntas hay que poder distinguirlas, así que se aclaran de
    forma progresiva y la última queda en el tono pleno.
    """
    from matplotlib.colors import to_rgb

    base = [_color(r.regla) for r in resultados]
    total = {c: base.count(c) for c in set(base)}
    vistos: dict[str, int] = {}
    salida = []
    for c in base:
        k = vistos.get(c, 0)
        vistos[c] = k + 1
        if total[c] == 1:
            salida.append(c)
            continue
        r, g, b = to_rgb(c)
        t = 0.55 * (total[c] - 1 - k) / (total[c] - 1)   # el último queda pleno
        salida.append((r + (1 - r) * t, g + (1 - g) * t, b + (1 - b) * t))
    return salida


def _moneda(x: float) -> str:
    return f"${x:,.0f}"


# ══════════════════════════════════════════════════════════════════════
#  Tablas
# ══════════════════════════════════════════════════════════════════════
def resumen(resultados: list[Resultado]) -> pd.DataFrame:
    """Una fila por regla, con lo que hay que mirar de cada una."""
    filas = []
    for r in resultados:
        filas.append(
            {
                "regla": r.regla,
                "obras financiadas": len(r.financiados),
                "gasto": _moneda(r.gasto),
                "remanente": _moneda(r.remanente),
                "Gini entre distritos": round(r.gini, 3),
                "satisfacción media": round(r.satisfaccion_media, 2),
                "votantes sin nada": f"{r.sin_nada:.0%}",
                "grupos sin nada": len(r.grupos_sin_nada()),
            }
        )
    return pd.DataFrame(filas).set_index("regla")


def reparto(resultados: list[Resultado], esc: Escenario) -> pd.DataFrame:
    """Cuánto recibió cada distrito bajo cada regla, contra su parte proporcional."""
    filas = []
    for d in esc.distritos:
        fila = {
            "distrito": d,
            "población": f"{esc.distritos[d]:,}",
            "le tocaría": _moneda(esc.parte_proporcional(d)),
        }
        for r in resultados:
            fila[r.regla] = _moneda(r.por_distrito[d])
        filas.append(fila)
    return pd.DataFrame(filas).set_index("distrito")


def obras(resultados: list[Resultado], esc: Escenario) -> pd.DataFrame:
    """Qué proyecto financió cada regla. Un ✓ por regla que lo financió."""
    filas = []
    for p in esc.proyectos:
        fila = {"proyecto": p.id, "distrito": p.distrito, "costo": _moneda(p.costo)}
        for r in resultados:
            fila[r.regla] = "✓" if p.id in r.financiados else ""
        filas.append(fila)
    df = pd.DataFrame(filas).set_index("proyecto")
    # sólo las obras que alguna regla financió
    marcas = df[[r.regla for r in resultados]]
    return df[(marcas == "✓").any(axis=1)]


# ══════════════════════════════════════════════════════════════════════
#  Gráfica principal
# ══════════════════════════════════════════════════════════════════════
def grafica_reparto(
    resultados: list[Resultado],
    esc: Escenario,
    titulo: str | None = None,
    figsize: tuple[float, float] = (10.0, 4.6),
):
    """Barras de gasto por distrito, una por regla, contra la parte proporcional.

    La línea punteada de cada grupo marca lo que le tocaría al distrito si el
    presupuesto se repartiera en proporción a su población. Una regla es
    equitativa en la medida en que sus barras se acercan a esas marcas.
    """
    distritos = list(esc.distritos)
    x = np.arange(len(distritos))
    ancho = 0.8 / len(resultados)

    fig, ax = plt.subplots(figsize=figsize)
    paleta = _paleta(resultados)

    for k, r in enumerate(resultados):
        pos = x - 0.4 + ancho * (k + 0.5)
        valores = [r.por_distrito[d] for d in distritos]
        ax.bar(pos, valores, ancho * 0.9, label=r.regla, color=paleta[k])

    # marca de la parte proporcional
    for i, d in enumerate(distritos):
        y = esc.parte_proporcional(d)
        ax.plot(
            [i - 0.44, i + 0.44], [y, y],
            linestyle="--", linewidth=1.6, color=ACENTO,
            zorder=5,
            label="Parte proporcional a la población" if i == 0 else None,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{d}\n{esc.distritos[d]:,} hab." for d in distritos], fontsize=9
    )
    ax.set_ylabel("Gasto asignado al distrito")
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    ax.set_title(titulo or f"Reparto del presupuesto — {esc.nombre or 'escenario'}")
    ax.legend(fontsize=8, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig, ax


def grafica_remanente(
    resultados: list[Resultado],
    figsize: tuple[float, float] = (9.0, 3.0),
):
    """Barras apiladas de gastado vs. no gastado, para ver el remanente."""
    fig, ax = plt.subplots(figsize=figsize)
    nombres = [r.regla for r in resultados]
    y = np.arange(len(nombres))

    ax.barh(y, [r.gasto for r in resultados],
            color=_paleta(resultados), label="Gastado")
    ax.barh(y, [r.remanente for r in resultados],
            left=[r.gasto for r in resultados],
            color="#D8D8D8", label="Sin gastar")

    for i, r in enumerate(resultados):
        if r.remanente > 0.005 * r.presupuesto:
            ax.text(r.presupuesto, i, f"  sobran {_moneda(r.remanente)}",
                    va="center", fontsize=8.5, color=_GRIS)

    ax.set_yticks(y)
    ax.set_yticklabels(nombres, fontsize=9)
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=5))
    ax.xaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    ax.set_xlim(0, max(r.presupuesto for r in resultados) * 1.28)
    ax.set_xlabel("Presupuesto")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=2, frameon=False)
    fig.tight_layout()
    return fig, ax


def tabla_grupos(resultados: list[Resultado]) -> pd.DataFrame:
    """Satisfacción media de cada grupo de interés, bajo cada regla.

    Un cero en esta tabla es un grupo entero al que no le financiaron nada.
    Es la lectura directa de lo que EJR promete evitar.
    """
    boletas = resultados[0].boletas
    tam = boletas.tamano_grupos()
    filas = []
    for g in boletas.grupos:
        fila = {"grupo": g, "votantes": tam[g]}
        for r in resultados:
            fila[r.regla] = round(r.satisfaccion_por_grupo()[g], 2)
        filas.append(fila)
    return pd.DataFrame(filas).set_index("grupo")


def grafica_satisfaccion(
    resultados: list[Resultado],
    figsize: tuple[float, float] = (10.0, 4.6),
):
    """Satisfacción media por grupo de interés, una barra por regla.

    Mide cuántos de los proyectos que cada quien aprobó acabaron financiados.
    A diferencia del Gini del gasto por distrito —que las elecciones separadas
    ganan por definición, porque reparten por distrito de entrada— aquí sí
    aparecen los grupos que cruzan la ciudad.
    """
    boletas = resultados[0].boletas
    grupos = boletas.grupos
    tam = boletas.tamano_grupos()
    x = np.arange(len(grupos))
    ancho = 0.8 / len(resultados)

    fig, ax = plt.subplots(figsize=figsize)
    paleta = _paleta(resultados)
    for k, r in enumerate(resultados):
        por_grupo = r.satisfaccion_por_grupo()
        pos = x - 0.4 + ancho * (k + 0.5)
        barras = ax.bar(
            pos, [por_grupo[g] for g in grupos], ancho * 0.9,
            label=r.regla, color=paleta[k],
        )
        # marcar los grupos que se quedaron en cero
        for b, g in zip(barras, grupos):
            if por_grupo[g] == 0:
                ax.text(b.get_x() + b.get_width() / 2, 0.04, "0",
                        ha="center", va="bottom", fontsize=8,
                        color=paleta[k], fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{g}\n({tam[g]} votantes)" for g in grupos], fontsize=8.5
    )
    ax.set_ylabel("Proyectos aprobados que sí se financiaron\n(promedio por votante)")
    ax.set_title("Qué tan atendido queda cada grupo de interés")
    ax.legend(fontsize=8, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig, ax
