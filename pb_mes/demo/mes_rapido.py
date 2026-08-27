"""
Method of Equal Shares agregando votantes idénticos.

Es exactamente el mismo algoritmo que `pb_mes.simulation.mes.run_mes`, pero
apoyado en una observación: dos votantes que aprobaron *el mismo conjunto* de
proyectos son indistinguibles para el método. Pagan lo mismo en cada ronda, así
que su saldo siempre coincide y se pueden tratar como un solo votante con peso.

En el simulador esto importa mucho: el modelo de boletas produce a lo más un
puñado de canastas distintas (una por distrito y una por tema), así que 800
votantes se colapsan en ~6 tipos y el método corre unas 50 veces más rápido.
Eso es lo que permite mover un slider y ver el resultado al instante.

`run_mes` sigue siendo la implementación de referencia; `tests/test_demo_reglas.py`
verifica que ambas coincidan.
"""
from __future__ import annotations

from collections import defaultdict


def agrupar(aprobaciones: dict[str, set[str]]) -> list[tuple[frozenset[str], int]]:
    """Colapsa votantes con la misma canasta en (canasta, cuántos son)."""
    cuenta: dict[frozenset[str], int] = defaultdict(int)
    for a in aprobaciones.values():
        cuenta[frozenset(a)] += 1
    return sorted(cuenta.items(), key=lambda kv: (sorted(kv[0]), kv[1]))


def _rho(saldos: list[float], pesos: list[int], idx: list[int], costo: float) -> float | None:
    """El menor ρ tal que Σ peso_t · min(saldo_t, ρ) ≥ costo, o None si no alcanza.

    Misma búsqueda binaria de 64 pasos que usa `compute_rho`, para que las dos
    implementaciones coincidan hasta el último decimal.
    """
    disponible = sum(saldos[t] * pesos[t] for t in idx)
    if disponible < costo:
        return None
    lo, hi = 0.0, max(saldos[t] for t in idx)
    for _ in range(64):
        mid = (lo + hi) / 2
        if sum(min(saldos[t], mid) * pesos[t] for t in idx) >= costo:
            hi = mid
        else:
            lo = mid
    return hi


def mes(
    aprobaciones: dict[str, set[str]],
    costos: dict[str, float],
    presupuesto: float,
) -> list[str]:
    """Fase MES (sin completar), sobre votantes agregados.

    Devuelve los proyectos financiados en el orden en que se financiaron.
    """
    if not aprobaciones or not costos:
        return []

    tipos = agrupar(aprobaciones)
    n = len(aprobaciones)
    saldos = [presupuesto / n] * len(tipos)
    pesos = [w for _, w in tipos]

    # qué tipos apoyan cada proyecto (se calcula una sola vez)
    apoyos: dict[str, list[int]] = {p: [] for p in costos}
    for t, (canasta, _) in enumerate(tipos):
        for p in canasta:
            if p in apoyos:
                apoyos[p].append(t)

    financiados: list[str] = []
    restantes = sorted(costos)

    while True:
        mejor_p: str | None = None
        mejor_rho = float("inf")

        for p in restantes:
            idx = [t for t in apoyos[p] if saldos[t] > 0]
            if not idx:
                continue
            r = _rho(saldos, pesos, idx, costos[p])
            if r is not None and r < mejor_rho:
                mejor_rho = r
                mejor_p = p

        if mejor_p is None:
            return financiados

        for t in apoyos[mejor_p]:
            if saldos[t] > 0:
                saldos[t] -= min(saldos[t], mejor_rho)

        financiados.append(mejor_p)
        restantes.remove(mejor_p)
