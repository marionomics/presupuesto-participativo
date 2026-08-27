"""
Generación de boletas de aprobación a partir de un escenario.

El modelo tiene una sola perilla, `alpha`, que va de 0 a 1 y describe qué tan
territorial es el interés de la gente:

  alpha = 0   Todo el interés es territorial. Cada quien aprueba los proyectos
              de su propio distrito (más los de frontera que le tocan de lado).
              Es el supuesto explícito de Peters et al. (2021), p. 1: "every
              Northside resident will cast votes for projects A, B, C, and D".

  alpha = 1   Todo el interés es temático. Cada votante pertenece a un grupo
              que cruza la ciudad —los papás y el parque, los ciclistas y la
              ciclovía— y aprueba los proyectos de su tema estén donde estén.

Entre 0 y 1, `alpha` es la fracción de votantes cuyo interés es temático. Es la
perilla que hace visible el problema de la diapositiva 12: bajo elecciones
separadas por distrito, un grupo temático nunca logra formar bloque.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pb_mes.demo.escenario import Escenario


@dataclass
class Boletas:
    """Las boletas de una elección, más de dónde vive cada quien."""

    aprobaciones: dict[str, set[str]]   # votante -> proyectos que aprueba
    distrito: dict[str, str]            # votante -> distrito donde vive
    grupo: dict[str, str]               # votante -> grupo de interés al que pertenece
    alpha: float
    semilla: int

    def __len__(self) -> int:
        return len(self.aprobaciones)

    @property
    def n_votantes(self) -> int:
        return len(self.aprobaciones)

    def votos(self, proyecto: str) -> int:
        """Cuántos votantes aprobaron el proyecto, en toda la ciudad."""
        return sum(1 for a in self.aprobaciones.values() if proyecto in a)

    def votos_locales(self, proyecto: str, distrito: str) -> int:
        """Cuántos aprobaron el proyecto *entre los residentes* del distrito."""
        return sum(
            1
            for v, a in self.aprobaciones.items()
            if proyecto in a and self.distrito[v] == distrito
        )

    def votantes_de(self, distrito: str) -> list[str]:
        return [v for v, d in self.distrito.items() if d == distrito]

    @property
    def grupos(self) -> list[str]:
        return sorted(set(self.grupo.values()))

    def miembros(self, grupo: str) -> list[str]:
        return [v for v, g in self.grupo.items() if g == grupo]

    def tamano_grupos(self) -> dict[str, int]:
        return {g: len(self.miembros(g)) for g in self.grupos}


def generar_boletas(
    esc: Escenario,
    alpha: float = 0.0,
    n_votantes: int = 800,
    semilla: int = 42,
    frontera: bool = True,
) -> Boletas:
    """Genera boletas de aprobación para un escenario.

    Los votantes se reparten entre distritos en proporción a la población. Cada
    uno es territorial o temático según `alpha`:

    - **Territorial**: aprueba todos los proyectos de su distrito, más los
      proyectos de frontera del distrito vecino que dan a su lado.
    - **Temático**: se le asigna uno de los temas del escenario y aprueba los
      proyectos de ese tema en toda la ciudad.

    `frontera` controla si los vecinos del otro lado del límite aprueban los
    proyectos de frontera. Ponlo en False para reproducir el supuesto con el
    que Peters et al. abren el ejemplo —"residents only vote for projects that
    concern their own district"— y en True para el caso realista.

    Si el escenario no tiene temas, `alpha` no hace nada y todos son
    territoriales — no hay ningún interés que pueda cruzar la frontera.
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha debe estar entre 0 y 1, recibí {alpha}")
    if n_votantes < 1:
        raise ValueError(f"hacen falta votantes, recibí n_votantes={n_votantes}")

    rng = np.random.default_rng(semilla)
    temas = esc.temas
    if not temas:
        alpha = 0.0

    # ── reparto de votantes entre distritos, proporcional a la población ──
    nombres = list(esc.distritos)
    pesos = np.array([esc.distritos[d] for d in nombres], dtype=float)
    pesos /= pesos.sum()
    cuotas = _reparto_proporcional(n_votantes, pesos)

    # ── qué aprueba un territorial de cada distrito (se calcula una vez) ──
    canasta_local: dict[str, set[str]] = {
        d: {
            p.id
            for p in esc.proyectos
            if p.distrito == d or (frontera and p.frontera_con == d)
        }
        for d in nombres
    }
    canasta_tema: dict[str, set[str]] = {
        t: {p.id for p in esc.por_tema(t)} for t in temas
    }

    aprobaciones: dict[str, set[str]] = {}
    distrito: dict[str, str] = {}
    grupo: dict[str, str] = {}

    idx = 0
    for d, cuota in zip(nombres, cuotas):
        # cuántos de este distrito son temáticos
        es_tematico = rng.random(cuota) < alpha
        tema_de = rng.integers(0, len(temas), size=cuota) if temas else None

        for k in range(cuota):
            votante = f"v{idx:05d}"
            if es_tematico[k]:
                t = temas[tema_de[k]]
                aprobaciones[votante] = set(canasta_tema[t])
                grupo[votante] = f"Temático · {t}"
            else:
                aprobaciones[votante] = set(canasta_local[d])
                grupo[votante] = f"Vecinos · {d}"
            distrito[votante] = d
            idx += 1

    return Boletas(
        aprobaciones=aprobaciones,
        distrito=distrito,
        grupo=grupo,
        alpha=alpha,
        semilla=semilla,
    )


def _reparto_proporcional(total: int, pesos: np.ndarray) -> list[int]:
    """Reparte `total` enteros según `pesos`, sin perder ni inventar unidades.

    Usa el método de los restos mayores, así que la suma siempre da `total`
    exacto — importante porque el número de votantes es lo que fija b/n.
    """
    exactos = total * pesos
    base = np.floor(exactos).astype(int)
    faltan = total - int(base.sum())
    if faltan:
        orden = np.argsort(-(exactos - base))
        for i in orden[:faltan]:
            base[i] += 1
    return base.tolist()
