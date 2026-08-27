"""
Las dos formas de usar el simulador desde el notebook.

  `simular(...)`  — se le pasan números y muestra el resultado. Sirve si los
                    widgets no cargan, o para dejar un escenario fijo escrito
                    en la celda.
  `panel()`       — el tablero de sliders para mover cosas en vivo.
"""
from __future__ import annotations

import matplotlib.pyplot as plt

from pb_mes.demo import graficas
from pb_mes.demo.boletas import generar_boletas
from pb_mes.demo.escenario import Escenario, circleville, escenario_simple
from pb_mes.demo.reglas import comparar

NOMBRES_CIRCLEVILLE = ["Northside", "Eastside", "Westside", "Southside"]
MAX_DISTRITOS = 8


def construir_escenario(
    poblacion: list[int],
    presupuesto: float,
    factor_costos: float = 1.0,
    usar_circleville: bool = True,
) -> Escenario:
    """Arma el escenario a partir de los controles del panel.

    Con cuatro distritos se usa Circleville, que trae los proyectos reales del
    paper —con sus temas y sus proyectos de frontera—. Con cualquier otro
    número se arma una ciudad genérica, sin temas.
    """
    if usar_circleville and len(poblacion) == 4:
        base = circleville()
        distritos = dict(zip(NOMBRES_CIRCLEVILLE, poblacion))
        return base.con(
            distritos=distritos,
            presupuesto=presupuesto,
            factor_costos=factor_costos,
        )
    return escenario_simple(
        poblacion,
        costo_base=50_000.0 * factor_costos,
        presupuesto=presupuesto,
        nombre=f"Ciudad de {len(poblacion)} distritos",
    )


def simular(
    poblacion: list[int] | None = None,
    presupuesto: float = 400_000.0,
    alpha: float = 0.0,
    completar: str = "presupuesto",
    desempate: str = "costo_desc",
    factor_costos: float = 1.0,
    n_votantes: int = 800,
    semilla: int = 42,
    frontera: bool = True,
    mostrar: bool = True,
):
    """Corre las tres reglas y muestra el resultado.

    Parameters
    ----------
    poblacion
        Habitantes por distrito. Con cuatro valores se usa Circleville; con
        cualquier otro número, una ciudad genérica. Por defecto, Circleville.
    presupuesto
        La bolsa a repartir.
    alpha
        Qué fracción de la gente tiene un interés temático en vez de
        territorial (0 = todo el interés es de su propia colonia).
    completar
        Qué hacer con lo que el Método de Partes Iguales deja sin gastar:
        "presupuesto", "codicioso" o "no".
    desempate
        Cómo romper empates de votos: "costo_desc", "costo_asc" o "id".
    factor_costos
        Multiplica el costo de todas las obras.
    n_votantes
        Cuántos votantes simular. Más votantes no cambian el resultado de
        forma apreciable, sólo lo hacen más lento.

    Returns
    -------
    (escenario, boletas, resultados)
    """
    if poblacion is None:
        poblacion = [120_000, 110_000, 90_000, 80_000]

    esc = construir_escenario(poblacion, presupuesto, factor_costos)
    boletas = generar_boletas(
        esc, alpha=alpha, n_votantes=n_votantes, semilla=semilla, frontera=frontera
    )
    resultados = comparar(esc, boletas, desempate=desempate, completar=completar)

    if mostrar:
        _mostrar(esc, boletas, resultados)
    return esc, boletas, resultados


def _mostrar(esc, boletas, resultados) -> None:
    from IPython.display import display

    display(graficas.resumen(resultados))
    graficas.grafica_reparto(resultados, esc)
    plt.show()
    graficas.grafica_satisfaccion(resultados)
    plt.show()


# ══════════════════════════════════════════════════════════════════════
#  Tablero de sliders
# ══════════════════════════════════════════════════════════════════════
def panel():
    """Devuelve el tablero interactivo. Úsalo como última línea de una celda."""
    import ipywidgets as W
    from IPython.display import display

    estilo = {"description_width": "170px"}
    ancho = W.Layout(width="460px")

    n_distritos = W.IntSlider(
        value=4, min=2, max=MAX_DISTRITOS, step=1,
        description="Número de distritos", style=estilo, layout=ancho,
        continuous_update=False,
    )

    poblaciones = [
        W.IntSlider(
            value=v, min=5_000, max=300_000, step=5_000,
            description=f"Población {n}", style=estilo, layout=ancho,
            continuous_update=False, readout_format=",d",
        )
        for n, v in zip(
            NOMBRES_CIRCLEVILLE + [f"D{i}" for i in range(5, MAX_DISTRITOS + 1)],
            [120_000, 110_000, 90_000, 80_000] + [80_000] * (MAX_DISTRITOS - 4),
        )
    ]

    presupuesto = W.IntSlider(
        value=400_000, min=50_000, max=1_200_000, step=50_000,
        description="Presupuesto", style=estilo, layout=ancho,
        continuous_update=False, readout_format=",d",
    )
    factor_costos = W.FloatSlider(
        value=1.0, min=0.25, max=3.0, step=0.25,
        description="Costo de las obras (×)", style=estilo, layout=ancho,
        continuous_update=False,
    )
    alpha = W.FloatSlider(
        value=0.0, min=0.0, max=1.0, step=0.05,
        description="Interés temático (α)", style=estilo, layout=ancho,
        continuous_update=False,
    )
    completar = W.Dropdown(
        options=[
            ("Subir la dotación pareja", "presupuesto"),
            ("Repartir por número de apoyos", "codicioso"),
            ("No completar", "no"),
        ],
        value="presupuesto",
        description="Sobrante del MES", style=estilo, layout=ancho,
    )
    desempate = W.Dropdown(
        options=[
            ("Primero lo caro", "costo_desc"),
            ("Primero lo barato", "costo_asc"),
            ("Alfabético", "id"),
        ],
        value="costo_desc",
        description="Empates de votos", style=estilo, layout=ancho,
    )
    n_votantes = W.Dropdown(
        options=[("Rápido (400)", 400), ("Normal (800)", 800), ("Fino (2000)", 2000)],
        value=800, description="Votantes simulados", style=estilo, layout=ancho,
    )

    aviso = W.HTML()

    def _visibilidad(*_):
        for i, s in enumerate(poblaciones):
            s.layout.display = "" if i < n_distritos.value else "none"
        es_circleville = n_distritos.value == 4
        alpha.disabled = not es_circleville
        aviso.value = (
            "<i>Circleville: los 20 proyectos del paper, con temas "
            "(parque, ciclovía) y proyectos de frontera.</i>"
            if es_circleville
            else "<i>Ciudad genérica: cuatro obras por distrito y sin temas, "
            "así que α no hace nada. Vuelve a 4 distritos para Circleville.</i>"
        )

    n_distritos.observe(_visibilidad, names="value")
    _visibilidad()

    def _correr(**kw):
        n = kw["n_distritos"]
        poblacion = [kw[f"p{i}"] for i in range(n)]
        simular(
            poblacion=poblacion,
            presupuesto=kw["presupuesto"],
            alpha=kw["alpha"],
            completar=kw["completar"],
            desempate=kw["desempate"],
            factor_costos=kw["factor_costos"],
            n_votantes=kw["n_votantes"],
        )

    controles = {
        "n_distritos": n_distritos,
        "presupuesto": presupuesto,
        "factor_costos": factor_costos,
        "alpha": alpha,
        "completar": completar,
        "desempate": desempate,
        "n_votantes": n_votantes,
        **{f"p{i}": s for i, s in enumerate(poblaciones)},
    }
    salida = W.interactive_output(_correr, controles)

    izquierda = W.VBox([n_distritos, *poblaciones, aviso])
    derecha = W.VBox([presupuesto, factor_costos, alpha, completar, desempate, n_votantes])
    return W.VBox([W.HBox([izquierda, derecha]), salida])
