"""
Escenarios para el simulador de presupuesto participativo.

Un escenario es todo lo que hace falta para correr una elección: los distritos
con su población, los proyectos con su costo y ubicación, y la bolsa a repartir.

El escenario por defecto es Circleville, la ciudad ficticia de Peters et al.
(2021), Figura 1 — la misma que aparece en la presentación.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import pandas as pd


@dataclass(frozen=True)
class Proyecto:
    """Un proyecto sometido a votación."""

    id: str
    distrito: str
    costo: float
    tema: str | None = None          # interés que cruza distritos (papás, ciclistas…)
    frontera_con: str | None = None  # distrito vecino que también lo quiere


@dataclass
class Escenario:
    """Una elección completa: distritos, proyectos y presupuesto."""

    distritos: dict[str, int]        # distrito -> población
    proyectos: list[Proyecto]
    presupuesto: float
    nombre: str = ""

    # ── consultas ─────────────────────────────────────────────────────
    @property
    def poblacion_total(self) -> int:
        return sum(self.distritos.values())

    def proporcion(self, distrito: str) -> float:
        """Participación poblacional del distrito, π_d."""
        return self.distritos[distrito] / self.poblacion_total

    def parte_proporcional(self, distrito: str) -> float:
        """La bolsa que le tocaría al distrito si se repartiera por población."""
        return self.presupuesto * self.proporcion(distrito)

    def costos(self) -> dict[str, float]:
        return {p.id: p.costo for p in self.proyectos}

    def proyectos_de(self, distrito: str) -> list[Proyecto]:
        return [p for p in self.proyectos if p.distrito == distrito]

    def por_tema(self, tema: str) -> list[Proyecto]:
        return [p for p in self.proyectos if p.tema == tema]

    @property
    def temas(self) -> list[str]:
        return sorted({p.tema for p in self.proyectos if p.tema is not None})

    def tabla(self) -> pd.DataFrame:
        """Los proyectos como DataFrame, para mostrar en el notebook."""
        return pd.DataFrame(
            [
                {
                    "proyecto": p.id,
                    "distrito": p.distrito,
                    "costo": p.costo,
                    "tema": p.tema or "—",
                    "frontera con": p.frontera_con or "",
                }
                for p in self.proyectos
            ]
        )

    def tabla_distritos(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "distrito": d,
                    "población": pob,
                    "% de la ciudad": self.proporcion(d),
                    "parte proporcional": self.parte_proporcional(d),
                    "proyectos": len(self.proyectos_de(d)),
                }
                for d, pob in self.distritos.items()
            ]
        )

    # ── modificación ──────────────────────────────────────────────────
    def con(
        self,
        *,
        distritos: dict[str, int] | None = None,
        presupuesto: float | None = None,
        factor_costos: float | None = None,
    ) -> "Escenario":
        """Copia del escenario con algunos parámetros cambiados.

        `factor_costos` multiplica el costo de todos los proyectos, para mover
        la relación entre lo que cuestan las obras y lo que hay en la bolsa.
        """
        proyectos = self.proyectos
        if factor_costos is not None:
            proyectos = [replace(p, costo=p.costo * factor_costos) for p in proyectos]
        return Escenario(
            distritos=dict(distritos or self.distritos),
            proyectos=proyectos,
            presupuesto=self.presupuesto if presupuesto is None else presupuesto,
            nombre=self.nombre,
        )


# ══════════════════════════════════════════════════════════════════════
#  Circleville — Peters et al. (2021), Figura 1
# ══════════════════════════════════════════════════════════════════════
#
#  Los distritos y las poblaciones vienen del mapa. La asignación de cada
#  proyecto a su distrito se calculó con las coordenadas reales de las
#  etiquetas en el PDF: el mapa es un círculo partido en cuatro sectores
#  desde el centro (305.13, 619.37 en puntos PostScript), así que cada
#  proyecto cae en el sector que le corresponde por su ángulo.
#
#  Temas (los menciona el propio paper, p. 2):
#    · "parques"  — los papás de toda la ciudad y el parque infantil C
#    · "ciclovia" — los ciclistas y la ciclovía del río: R, S, H, G
#
#  Proyectos de frontera (también del paper, p. 2): A está sobre el límite
#  Northside/Westside y P sobre el de Westside/Southside. Los vecinos del
#  otro lado los quieren, pero bajo elecciones separadas no pueden votarlos.

_CIRCLEVILLE_PROYECTOS = [
    # ── Northside (120k) ──
    Proyecto("A", "Northside",  50_000, frontera_con="Westside"),
    Proyecto("B", "Northside",  30_000),
    Proyecto("C", "Northside", 150_000, tema="parques"),
    Proyecto("D", "Northside", 250_000),
    # ── Eastside (110k) ──
    Proyecto("E", "Eastside",   60_000),
    Proyecto("F", "Eastside",   10_000),
    Proyecto("G", "Eastside",   90_000, tema="ciclovia"),
    Proyecto("H", "Eastside",   60_000, tema="ciclovia"),
    Proyecto("I", "Eastside",    4_000),
    # ── Southside (80k) ──
    Proyecto("J", "Southside",  70_000),
    Proyecto("K", "Southside",  20_000),
    Proyecto("L", "Southside",  30_000),
    Proyecto("M", "Southside",  20_000),
    Proyecto("N", "Southside",  40_000),
    Proyecto("O", "Southside", 100_000),
    # ── Westside (90k) ──
    Proyecto("P", "Westside",   30_000, frontera_con="Southside"),
    Proyecto("Q", "Westside",   80_000),
    Proyecto("R", "Westside",   10_000, tema="ciclovia"),
    Proyecto("S", "Westside",   40_000, tema="ciclovia"),
    Proyecto("T", "Westside",    7_000),
]

_CIRCLEVILLE_POBLACION = {
    "Northside": 120_000,
    "Eastside": 110_000,
    "Westside": 90_000,
    "Southside": 80_000,
}


def circleville() -> Escenario:
    """El escenario por defecto: la ciudad de Peters et al., Figura 1."""
    return Escenario(
        distritos=dict(_CIRCLEVILLE_POBLACION),
        proyectos=list(_CIRCLEVILLE_PROYECTOS),
        presupuesto=400_000.0,
        nombre="Circleville",
    )


def escenario_simple(
    poblacion: list[int] | dict[str, int],
    proyectos_por_distrito: int = 4,
    costo_base: float = 50_000.0,
    presupuesto: float | None = None,
    nombre: str = "Escenario propio",
) -> Escenario:
    """Arma un escenario genérico desde cero.

    Útil para probar configuraciones que no son Circleville: otro número de
    distritos, otro reparto de población. Cada distrito recibe el mismo número
    de proyectos, con costos escalonados alrededor de `costo_base`.
    """
    if isinstance(poblacion, list):
        poblacion = {f"D{i + 1}": p for i, p in enumerate(poblacion)}

    proyectos: list[Proyecto] = []
    for d in poblacion:
        for k in range(proyectos_por_distrito):
            # costos escalonados: 0.5x, 1x, 1.5x, 2x … del costo base
            factor = 0.5 * (k + 1)
            proyectos.append(
                Proyecto(f"{d}-{k + 1}", d, round(costo_base * factor, 2))
            )

    if presupuesto is None:
        # por defecto, la bolsa alcanza para ~un tercio de lo propuesto
        presupuesto = round(sum(p.costo for p in proyectos) / 3, 2)

    return Escenario(
        distritos=dict(poblacion),
        proyectos=proyectos,
        presupuesto=presupuesto,
        nombre=nombre,
    )
