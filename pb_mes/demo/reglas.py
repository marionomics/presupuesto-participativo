"""
Las tres reglas de conteo que compara la presentación.

  1. conteo_simple            — voto libre, gana el más votado hasta agotar la bolsa
  2. elecciones_por_distrito  — bolsa repartida por población, voto anclado al distrito
  3. partes_iguales           — Method of Equal Shares (Peters et al., 2021)

Las tres reciben el mismo escenario y las mismas boletas, y devuelven un
`Resultado` con la misma forma, para poder ponerlas lado a lado.
"""
from __future__ import annotations

from dataclasses import dataclass

from pb_mes.demo.boletas import Boletas
from pb_mes.demo.escenario import Escenario
from pb_mes.demo.mes_rapido import mes as _mes
from pb_mes.utils.gini import gini

# Cómo desempatar entre proyectos con el mismo número de votos.
#   "costo_desc" — primero el más caro. Es el que reproduce el resultado que
#                  Peters et al. reportan para Circleville (se financian C y D).
#   "costo_asc"  — primero el más barato, para financiar más obras.
#   "id"         — alfabético; neutral, sólo para pruebas.
DESEMPATES = ("costo_desc", "costo_asc", "id")

# Qué hacer con el dinero que el MES deja sin gastar. Peters et al. (2021) §3.4
# discuten justamente esto: el método se detiene cuando nadie puede pagar, no
# cuando se acaba la bolsa, así que hace falta decidir qué pasa con el resto.
#
#   "presupuesto" — Se le sube la dotación a *todos* por igual (cada quien
#                   recibe f·b/n en vez de b/n) hasta el máximo que siga
#                   cabiendo en el presupuesto. Como el aumento es parejo, la
#                   proporcionalidad se conserva. Es lo que se usa en las
#                   implementaciones reales del método.
#   "codicioso"   — Se agregan proyectos por número de apoyos hasta agotar el
#                   remanente. Es simple, pero le entrega el sobrante al grupo
#                   más numeroso y deshace buena parte de la proporcionalidad.
#   "no"          — No se completa. Es lo que reportan los ejemplos del paper.
COMPLETADOS = ("presupuesto", "codicioso", "no")


@dataclass
class Resultado:
    """Lo que produjo una regla, listo para graficar o tabular."""

    regla: str
    financiados: list[str]
    gasto: float
    presupuesto: float
    por_distrito: dict[str, float]
    escenario: Escenario
    boletas: Boletas

    @property
    def remanente(self) -> float:
        return self.presupuesto - self.gasto

    @property
    def gini(self) -> float:
        """Desigualdad del gasto entre distritos: 0 es parejo, 1 es todo en uno."""
        return gini(list(self.por_distrito.values()))

    @property
    def distritos_sin_nada(self) -> list[str]:
        return [d for d, v in self.por_distrito.items() if v == 0]

    def personas_sin_nada(self) -> int:
        """Cuánta gente vive en distritos que no recibieron un solo peso."""
        return sum(self.escenario.distritos[d] for d in self.distritos_sin_nada)

    # ── satisfacción de los votantes ──────────────────────────────────
    #
    # El Gini del gasto por distrito mide una sola cosa, y las elecciones
    # separadas por distrito siempre la ganan: reparten por distrito *por
    # definición*. La pregunta que de verdad importa es otra —cuánto de lo que
    # cada quien pidió acabó financiado— y ahí sí se ven las diferencias,
    # incluyendo a los grupos que no son territoriales.

    def satisfaccion(self) -> dict[str, int]:
        """Cuántos de los proyectos que aprobó cada votante quedaron financiados."""
        W = set(self.financiados)
        return {v: len(a & W) for v, a in self.boletas.aprobaciones.items()}

    @property
    def satisfaccion_media(self) -> float:
        s = self.satisfaccion()
        return sum(s.values()) / len(s) if s else 0.0

    @property
    def sin_nada(self) -> float:
        """Fracción de votantes a los que no les financiaron ni un solo proyecto."""
        s = self.satisfaccion()
        return sum(1 for v in s.values() if v == 0) / len(s) if s else 0.0

    def satisfaccion_por_grupo(self) -> dict[str, float]:
        """Satisfacción media dentro de cada grupo de interés."""
        s = self.satisfaccion()
        return {
            g: sum(s[v] for v in miembros) / len(miembros)
            for g in self.boletas.grupos
            if (miembros := self.boletas.miembros(g))
        }

    def grupos_sin_nada(self) -> list[str]:
        """Grupos en los que *nadie* obtuvo un solo proyecto financiado."""
        s = self.satisfaccion()
        return [
            g
            for g in self.boletas.grupos
            if all(s[v] == 0 for v in self.boletas.miembros(g))
        ]

    def desviacion_proporcional(self) -> dict[str, float]:
        """Gasto recibido menos la parte que le tocaría por población."""
        return {
            d: self.por_distrito[d] - self.escenario.parte_proporcional(d)
            for d in self.escenario.distritos
        }


def _resultado(
    regla: str, financiados: list[str], esc: Escenario, boletas: Boletas
) -> Resultado:
    costos = esc.costos()
    por_distrito = {d: 0.0 for d in esc.distritos}
    for p in esc.proyectos:
        if p.id in financiados:
            por_distrito[p.distrito] += p.costo
    return Resultado(
        regla=regla,
        financiados=financiados,
        gasto=sum(costos[p] for p in financiados),
        presupuesto=esc.presupuesto,
        por_distrito=por_distrito,
        escenario=esc,
        boletas=boletas,
    )


def _orden(
    ids: list[str], votos: dict[str, int], costos: dict[str, float], desempate: str
) -> list[str]:
    """Ordena proyectos por votos (de más a menos), desempatando como se pida."""
    if desempate not in DESEMPATES:
        raise ValueError(f"desempate debe ser uno de {DESEMPATES}, recibí {desempate!r}")
    if desempate == "costo_desc":
        clave = lambda p: (-votos[p], -costos[p], p)
    elif desempate == "costo_asc":
        clave = lambda p: (-votos[p], costos[p], p)
    else:
        clave = lambda p: (-votos[p], p)
    return sorted(ids, key=clave)


def _greedy(orden: list[str], costos: dict[str, float], bolsa: float) -> list[str]:
    """Recorre la lista financiando lo que quepa en lo que queda de la bolsa."""
    financiados: list[str] = []
    restante = bolsa
    for p in orden:
        if costos[p] <= restante:
            financiados.append(p)
            restante -= costos[p]
    return financiados


# ══════════════════════════════════════════════════════════════════════
#  1. Voto libre + conteo simple
# ══════════════════════════════════════════════════════════════════════
def conteo_simple(
    esc: Escenario, boletas: Boletas, desempate: str = "costo_desc"
) -> Resultado:
    """Se ordenan los proyectos por votos y se financian hasta agotar la bolsa.

    Sin restricción de distrito: cualquiera puede votar por cualquier proyecto,
    y hay una sola bolsa para toda la ciudad. Es la regla que deja al distrito
    más poblado quedarse con todo.
    """
    costos = esc.costos()
    votos = {p.id: boletas.votos(p.id) for p in esc.proyectos}
    orden = _orden(list(costos), votos, costos, desempate)
    return _resultado(
        "Conteo simple", _greedy(orden, costos, esc.presupuesto), esc, boletas
    )


# ══════════════════════════════════════════════════════════════════════
#  2. Elecciones separadas por distrito
# ══════════════════════════════════════════════════════════════════════
def elecciones_por_distrito(
    esc: Escenario, boletas: Boletas, desempate: str = "costo_desc"
) -> Resultado:
    """La bolsa se reparte por población y cada distrito vota lo suyo.

    Sólo cuentan los votos de los residentes del distrito al que el proyecto
    está asignado: el apoyo de los vecinos del otro lado de la frontera, y el
    de un grupo temático repartido por la ciudad, se descarta.
    """
    costos = esc.costos()
    financiados: list[str] = []
    for d in esc.distritos:
        ids = [p.id for p in esc.proyectos_de(d)]
        if not ids:
            continue
        votos = {p: boletas.votos_locales(p, d) for p in ids}
        orden = _orden(ids, votos, costos, desempate)
        financiados += _greedy(orden, costos, esc.parte_proporcional(d))
    return _resultado("Elecciones por distrito", financiados, esc, boletas)


# ══════════════════════════════════════════════════════════════════════
#  3. Método de Partes Iguales
# ══════════════════════════════════════════════════════════════════════
def _dotacion_maxima(
    aprobaciones: dict[str, set[str]],
    costos: dict[str, float],
    presupuesto: float,
    pasos: int = 40,
) -> tuple[list[str], float]:
    """Busca la dotación pareja más alta cuyo resultado siga cabiendo en la bolsa.

    Con dotación b/n el método casi siempre deja dinero sin gastar. Subirle la
    dotación a todos por igual hace que se financien más obras sin romper la
    proporcionalidad: nadie recibe un trato distinto, sólo se agranda la
    cuenta virtual de cada quien en la misma medida.

    Devuelve (proyectos financiados, factor usado).
    """
    def corrida(f: float) -> tuple[list[str], float]:
        fin = _mes(aprobaciones, costos, presupuesto * f)
        return fin, sum(costos[p] for p in fin)

    mejor, _ = corrida(1.0)          # f = 1 siempre cabe: el MES nunca se pasa
    lo, mejor_f = 1.0, 1.0

    # cota superior: duplicar hasta que se pase
    hi = 2.0
    while hi <= 64.0:
        fin, gasto = corrida(hi)
        if gasto > presupuesto:
            break
        mejor, lo, mejor_f = fin, hi, hi
        hi *= 2.0
    else:
        return mejor, mejor_f

    # bisección entre la última que cupo y la primera que se pasó
    for _ in range(pasos):
        mid = (lo + hi) / 2
        fin, gasto = corrida(mid)
        if gasto <= presupuesto:
            mejor, lo, mejor_f = fin, mid, mid
        else:
            hi = mid
    return mejor, mejor_f


def _completado_codicioso(
    financiados: list[str],
    aprobaciones: dict[str, set[str]],
    costos: dict[str, float],
    presupuesto: float,
) -> list[str]:
    """Agrega proyectos por número de apoyos mientras alcance el remanente."""
    restante = presupuesto - sum(costos[p] for p in financiados)
    faltantes = [p for p in costos if p not in financiados]
    apoyos = {
        p: sum(1 for a in aprobaciones.values() if p in a) for p in faltantes
    }
    salida = list(financiados)
    for p in sorted(faltantes, key=lambda p: (-apoyos[p], p)):
        if costos[p] <= restante:
            salida.append(p)
            restante -= costos[p]
    return salida


def partes_iguales(
    esc: Escenario, boletas: Boletas, completar: str | bool = "presupuesto"
) -> Resultado:
    """Method of Equal Shares (Peters et al., 2021).

    Cada votante recibe b/n en una cuenta virtual y un proyecto se financia
    cuando quienes lo apoyan pueden pagarlo entre ellos.

    `completar` decide qué hacer con lo que sobra; ver COMPLETADOS. Por defecto
    se sube la dotación pareja, que es lo que conserva la proporcionalidad.
    """
    if completar is True:
        completar = "presupuesto"
    elif completar is False:
        completar = "no"
    if completar not in COMPLETADOS:
        raise ValueError(f"completar debe ser uno de {COMPLETADOS}, recibí {completar!r}")

    apr, costos = boletas.aprobaciones, esc.costos()

    if completar == "presupuesto":
        financiados, _ = _dotacion_maxima(apr, costos, esc.presupuesto)
        nombre = "Partes Iguales"
    else:
        financiados = _mes(apr, costos, esc.presupuesto)
        if completar == "codicioso":
            financiados = _completado_codicioso(financiados, apr, costos, esc.presupuesto)
            nombre = "Partes Iguales (completado codicioso)"
        else:
            nombre = "Partes Iguales (sin completar)"

    return _resultado(nombre, financiados, esc, boletas)


# ══════════════════════════════════════════════════════════════════════
def comparar(
    esc: Escenario,
    boletas: Boletas,
    desempate: str = "costo_desc",
    completar: str | bool = "presupuesto",
) -> list[Resultado]:
    """Corre las tres reglas sobre el mismo escenario y las mismas boletas."""
    return [
        conteo_simple(esc, boletas, desempate),
        elecciones_por_distrito(esc, boletas, desempate),
        partes_iguales(esc, boletas, completar),
    ]
