# Design — Peters-Founded Notebook (canonical foundation + paper skeleton)

**Date:** 2026-06-26
**Author:** Mario Alberto García Meza (design captured by Claude)
**Status:** Approved (brainstorming), tight-first-cut build authorized

## Purpose

Peters, Pierczyński & Skowron (2021/2022), *Proportional Participatory Budgeting
with Additive Utilities* (arXiv:2008.13276v2), is the foundational paper for this
project — "the rock upon which we build." Its motivating *Circleville* example is
almost exactly our Durango district-exclusivity critique.

Produce a **new canonical study notebook**, `notebooks/notebook_peters.tex`, that:

1. Adopts Peters' notation and definitions project-wide.
2. Re-derives the whole theory (model → MES → EJR/FJR → distortions → equity →
   comparison → simulation design) on that foundation, applied to Durango.
3. Becomes the authoritative base whose structure mirrors Peters' and thereby
   defines the paper's section order. `notebook_v2.tex` is demoted to reference.

This is a **study notebook** (an artifact Claude may author), not paper section
content (which Mario writes by hand).

## Decisions (locked)

- **Notation:** Peters-canonical. Election tuple `(N, C, b, cost, {u_i})`; MES uses
  plain `ρ`; axiom lattice `JR ⊂ PJR ⊂ EJR ⊂ FJR ⊂ core`.
- **Scope:** Full re-derivation, but delivered as a **tight first cut** —
  Sections 1–7 complete; Section 8 (simulation) a deliberate stub to expand later.
- **Role:** Canonical foundation + paper skeleton.

### Symbol crosswalk (notebook_v2 → new)

| Object | notebook_v2 | new (Peters-compatible) |
|---|---|---|
| Voters | `N` | `N` |
| Projects | `𝒫` | `C` (individual project `c`) |
| Budget | `B` | `b` |
| Cost | `c` macro | `cost(·)` |
| MES threshold | `ϱ` (`\mesrho`) | `ρ` (`\rho`, used directly) |
| EJR cohesion threshold | — | `α(c)` |
| FJR weak-cohesion threshold | — | `β` |
| District **salience** | `α_d` | `s_d` |
| Voter **information** function | `σ_i` | `κ_i` |
| District **population share** | `β_d` | `π_d` |
| Signal / noise | `S(p), η(p)` | unchanged |

DEM, UAM, MES names unchanged. Coined terms still flagged in violet `naming`
boxes per project convention; established terms (MES, EJR, FJR, GCR, PAV, PSC,
core, priceability) cited, not coined.

## Structure (mirrors Peters)

1. **Introduction** — Circleville → Durango; DEM = the "separate district
   elections" fix Peters critiques. Plant the two nuances: rational ignorance
   (`κ_i`) and marginalized-district protection (`s_d`).
2. **Preliminaries / PB model** — Peters' tuple, plus our additions: districts
   `D`, project→district assignment, salience `s_d`, info `κ_i`, vote budget `v`.
   DEM and UAM defined as rules `R`.
3. **Method of Equal Shares** — Def. 1, ρ-affordability, Algorithm 1, worked
   example (Durango-flavored, modeled on Peters' 10-voter example).
4. **Proportionality axioms** — EJR (approval→general, Defs 2–5), Thm 2 (EJR up to
   one project) with proof, core / priceability / exhaustiveness, FJR + GCR,
   the axiom lattice, completion methods.
5. **Distortions of the DEM** — Props 1–5 recast against the EJR baseline
   (truncation/welfare loss, noise injection, coordination, mobilization,
   equity tradeoff).
6. **MES resolves the distortions** — Props 6–10; geographic equity as a
   corollary of EJR (the `π_d` guarantee); non-strategyproofness via Peters'
   machinery (Peters & Skowron / EJR⇒not SP), **not** Gibbard–Satterthwaite.
7. **Comparison** — DEM vs UAM vs MES property table over the JR–core lattice.
8. **Toward the paper / simulation** *(stub in first cut)* — cost vs approval
   utilities, ordinal→PSC, completions, Durango counterfactual design (mirrors
   Peters §6 experiments).
- **Appendix** — notation crosswalk table + ~20 keystone BibTeX entries to add
  to `references.bib`.

## Deliverables

- `notebooks/notebook_peters.tex` — new preamble with Peters-canonical macros,
  reusing notebook_v2's tcolorbox pedagogy boxes (keyidea / intuition /
  connection / watchout / naming) and theorem environments. Compiles standalone.
- BibTeX block (keystone references from Peters) for `references.bib`.
- This design doc, committed.

## Out of scope (this notebook)

- CONAPO marginalization weighting and ENIGH welfare extension (follow-up work).
- Real Durango voting-data analysis (Section 8 stays design-only for now).
- Rewriting `paper/` section files (Mario writes those by hand).
