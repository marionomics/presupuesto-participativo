"""
Pruebas del simulador interactivo (pb_mes/demo/).

La prueba que más importa es la primera: que el motor reproduzca el ejemplo
trabajado de Peters et al. (2021), pp. 7-8, que es el mismo que aparece en la
presentación. Si esa falla, las diapositivas están mal.
"""
import random

import pytest

from pb_mes.demo.boletas import generar_boletas
from pb_mes.demo.escenario import circleville, escenario_simple
from pb_mes.demo.mes_rapido import agrupar, mes
from pb_mes.demo.reglas import (
    comparar,
    conteo_simple,
    elecciones_por_distrito,
    partes_iguales,
)
from pb_mes.demo.panel import NOMBRES_CIRCLEVILLE, construir_escenario, panel, simular
from pb_mes.simulation.mes import run_mes

# ── el ejemplo del paper, pp. 7-8 ────────────────────────────────────
# 10 votantes, 5 proyectos, b = $100, así que cada quien recibe $10.
PAPER_APROBACIONES = {
    "i01": {"P1", "P2", "P3"},
    "i02": {"P1", "P2", "P3"},
    "i03": {"P1", "P2", "P3"},
    "i04": {"P1", "P2", "P3", "P4"},
    "i05": {"P1", "P2", "P3", "P4"},
    "i06": {"P2", "P4", "P5"},
    "i07": {"P4", "P5"},
    "i08": {"P5"},
    "i09": {"P5"},
    "i10": set(),
}
PAPER_COSTOS = {"P1": 36.0, "P2": 36.0, "P3": 25.0, "P4": 24.0, "P5": 24.0}


def test_ejemplo_del_paper_financia_p3_y_p5():
    """Peters et al. (2021), p. 8: W = {Proyecto 3, Proyecto 5}."""
    assert mes(PAPER_APROBACIONES, PAPER_COSTOS, 100.0) == ["P3", "P5"]


def test_ejemplo_del_paper_deja_dinero_sin_gastar():
    """El paper subraya que se gastan $49 de $100 y el método se detiene."""
    financiados = mes(PAPER_APROBACIONES, PAPER_COSTOS, 100.0)
    assert sum(PAPER_COSTOS[p] for p in financiados) == 49.0


def test_ejemplo_del_paper_rho_de_la_primera_ronda():
    """Los ρ de la ronda 1: 7.2, 6, 5, 6, 6 (figura de la p. 8)."""
    from pb_mes.simulation.mes import compute_rho

    saldos = {v: 10.0 for v in PAPER_APROBACIONES}
    esperados = {"P1": 7.2, "P2": 6.0, "P3": 5.0, "P4": 6.0, "P5": 6.0}
    for p, esperado in esperados.items():
        apoyos = [v for v, a in PAPER_APROBACIONES.items() if p in a]
        assert compute_rho(apoyos, saldos, PAPER_COSTOS[p]) == pytest.approx(esperado)


# ── la versión agregada coincide con la de referencia ────────────────
def test_agregar_colapsa_votantes_identicos():
    tipos = agrupar({"a": {"x"}, "b": {"x"}, "c": {"y"}})
    assert sorted(peso for _, peso in tipos) == [1, 2]


def test_mes_agregado_coincide_con_run_mes():
    """La agregación es exacta: mismos proyectos, mismo orden."""
    rng = random.Random(7)
    for _ in range(200):
        m, nv = rng.randint(3, 7), rng.randint(5, 40)
        costos = {f"p{j}": float(rng.randint(5, 60)) for j in range(m)}
        aprob = {f"v{i}": {p for p in costos if rng.random() < 0.45} for i in range(nv)}
        bolsa = float(rng.randint(40, 200))
        assert mes(aprob, costos, bolsa) == run_mes(
            aprob, costos, bolsa, completar=False
        )


# ── el resultado de Circleville que reporta el paper ─────────────────
def test_circleville_conteo_simple_da_C_y_D():
    """Peters et al., p. 1: se financian C y D, y 280k personas se quedan sin nada.

    Reproduce el supuesto con el que el paper abre el ejemplo: nadie vota fuera
    de su distrito (`frontera=False`). El desempate importa — ver la prueba
    siguiente.
    """
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.0, n_votantes=800, frontera=False)
    r = conteo_simple(esc, boletas, desempate="costo_desc")
    assert r.financiados == ["D", "C"]
    assert r.gasto == esc.presupuesto == 400_000
    assert r.personas_sin_nada() == 280_000


def test_circleville_el_desempate_cambia_el_resultado():
    """Con los votos empatados, el criterio de desempate decide quién gana.

    Northside tiene cuatro proyectos con exactamente los mismos votos. Si se
    financia primero lo caro sale el resultado del paper; si se financia
    primero lo barato, el presupuesto se derrama a otros distritos.
    """
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.0, n_votantes=800, frontera=False)
    caro = conteo_simple(esc, boletas, desempate="costo_desc")
    barato = conteo_simple(esc, boletas, desempate="costo_asc")
    assert caro.financiados != barato.financiados
    assert barato.personas_sin_nada() < caro.personas_sin_nada()


# ── propiedades que deben cumplirse siempre ──────────────────────────
@pytest.mark.parametrize("alpha", [0.0, 0.3, 0.6, 1.0])
def test_ninguna_regla_se_pasa_del_presupuesto(alpha):
    esc = circleville()
    boletas = generar_boletas(esc, alpha=alpha, n_votantes=400)
    for r in comparar(esc, boletas):
        assert r.gasto <= esc.presupuesto + 1e-9, r.regla


def test_elecciones_por_distrito_respetan_la_bolsa_de_cada_distrito():
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.4, n_votantes=400)
    r = elecciones_por_distrito(esc, boletas)
    for d in esc.distritos:
        assert r.por_distrito[d] <= esc.parte_proporcional(d) + 1e-9


@pytest.mark.parametrize("completar", ["presupuesto", "codicioso", "no"])
def test_partes_iguales_respeta_el_presupuesto(completar):
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.3, n_votantes=400)
    assert partes_iguales(esc, boletas, completar).gasto <= esc.presupuesto + 1e-9


def test_completado_por_presupuesto_gasta_al_menos_lo_que_la_fase_mes():
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.2, n_votantes=400)
    sin = partes_iguales(esc, boletas, "no")
    con = partes_iguales(esc, boletas, "presupuesto")
    assert con.gasto >= sin.gasto


def test_completado_codicioso_es_menos_proporcional_que_el_parejo():
    """Regresión del hallazgo: repartir el sobrante por número de apoyos se lo
    entrega al distrito más grande y deshace la proporcionalidad."""
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.0, n_votantes=800)
    assert (
        partes_iguales(esc, boletas, "codicioso").gini
        > partes_iguales(esc, boletas, "presupuesto").gini
    )


# ── el punto de la presentación, como regresión ──────────────────────
def test_partes_iguales_no_deja_grupos_vacios_donde_las_otras_si():
    """Escenario fijo (semilla 42, alpha=0.6): el conteo simple deja fuera a
    los vecinos de Southside, las elecciones por distrito a los papás, y el
    Método de Partes Iguales a nadie."""
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.6, n_votantes=800, semilla=42)
    simple, distrito, mpi = comparar(esc, boletas)
    assert simple.grupos_sin_nada() == ["Vecinos · Southside"]
    assert distrito.grupos_sin_nada() == ["Temático · parques"]
    assert mpi.grupos_sin_nada() == []
    assert mpi.sin_nada == 0.0


# ── boletas ──────────────────────────────────────────────────────────
def test_alpha_cero_todos_votan_lo_suyo():
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.0, n_votantes=200, frontera=False)
    for v, aprobados in boletas.aprobaciones.items():
        propios = {p.id for p in esc.proyectos_de(boletas.distrito[v])}
        assert aprobados == propios


def test_frontera_agrega_a_los_vecinos():
    esc = circleville()
    con = generar_boletas(esc, alpha=0.0, n_votantes=200, frontera=True)
    sin = generar_boletas(esc, alpha=0.0, n_votantes=200, frontera=False)
    # A está en Northside pero da a Westside
    assert con.votos("A") > sin.votos("A")


def test_alpha_uno_solo_quedan_los_temas():
    esc = circleville()
    boletas = generar_boletas(esc, alpha=1.0, n_votantes=200)
    sin_tema = [p.id for p in esc.proyectos if p.tema is None]
    assert all(boletas.votos(p) == 0 for p in sin_tema)


def test_los_votantes_se_reparten_en_proporcion_a_la_poblacion():
    esc = circleville()
    boletas = generar_boletas(esc, alpha=0.0, n_votantes=1000)
    assert len(boletas) == 1000
    for d in esc.distritos:
        esperado = 1000 * esc.proporcion(d)
        assert abs(len(boletas.votantes_de(d)) - esperado) <= 1


@pytest.mark.parametrize("alpha", [-0.1, 1.5])
def test_alpha_fuera_de_rango_es_error(alpha):
    with pytest.raises(ValueError, match="alpha"):
        generar_boletas(circleville(), alpha=alpha)


def test_desempate_invalido_es_error():
    esc = circleville()
    boletas = generar_boletas(esc, n_votantes=100)
    with pytest.raises(ValueError, match="desempate"):
        conteo_simple(esc, boletas, desempate="lo que sea")


# ── escenarios propios ───────────────────────────────────────────────
def test_escenario_simple_arma_lo_que_se_le_pide():
    esc = escenario_simple([100, 200, 300], proyectos_por_distrito=3)
    assert len(esc.distritos) == 3
    assert len(esc.proyectos) == 9
    assert esc.poblacion_total == 600
    assert esc.proporcion("D3") == pytest.approx(0.5)


def test_escenario_sin_temas_ignora_alpha():
    esc = escenario_simple([100, 100])
    boletas = generar_boletas(esc, alpha=1.0, n_votantes=100)
    assert boletas.alpha == 0.0
    assert all(g.startswith("Vecinos") for g in boletas.grupos)


def test_con_cambia_poblacion_y_presupuesto():
    esc = circleville().con(
        distritos={"Norte": 10, "Sur": 90}, presupuesto=1_000.0, factor_costos=0.5
    )
    assert esc.poblacion_total == 100
    assert esc.presupuesto == 1_000.0
    assert esc.proyectos[0].costo == 25_000.0


# ── el tablero y el atajo `simular` ──────────────────────────────────
def test_simular_devuelve_las_tres_reglas():
    esc, boletas, resultados = simular(mostrar=False)
    assert len(resultados) == 3
    assert esc.nombre == "Circleville"
    assert len(boletas) == 800


def test_simular_con_otro_numero_de_distritos_arma_ciudad_generica():
    esc, boletas, resultados = simular(
        poblacion=[50_000] * 6, presupuesto=600_000, alpha=0.5, mostrar=False
    )
    assert len(esc.distritos) == 6
    assert esc.temas == []          # la ciudad genérica no tiene temas…
    assert boletas.alpha == 0.0     # …así que alpha se ignora
    assert len(resultados) == 3


def test_construir_escenario_con_cuatro_distritos_usa_circleville():
    esc = construir_escenario([10, 20, 30, 40], presupuesto=1_000.0)
    assert esc.nombre == "Circleville"
    assert list(esc.distritos) == NOMBRES_CIRCLEVILLE
    assert len(esc.proyectos) == 20


def test_el_panel_se_construye_y_su_callback_corre():
    """No se puede simular un clic aquí, pero sí verificar que el tablero se
    arma y que la función que corre al mover un slider no truena."""
    tablero = panel()
    assert tablero is not None

    sliders = {}
    def recolectar(w):
        if hasattr(w, "children"):
            for h in w.children:
                recolectar(h)
        if getattr(w, "description", "").startswith(("Número", "Población", "Presupuesto")):
            sliders[w.description] = w.value
    recolectar(tablero)
    assert sliders["Número de distritos"] == 4
    assert sliders["Presupuesto"] == 400_000
    # el mismo camino que recorre el callback
    _, _, resultados = simular(
        poblacion=[sliders[f"Población {n}"] for n in NOMBRES_CIRCLEVILLE],
        presupuesto=sliders["Presupuesto"],
        mostrar=False,
    )
    assert len(resultados) == 3
