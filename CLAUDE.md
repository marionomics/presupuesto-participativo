# Participatory Budgeting Mechanism Design — Research Paper

## About This Project

Economics research paper analyzing the district-exclusivity voting constraint in Durango, Mexico's participatory budgeting (*presupuesto participativo*) system. The paper combines **mechanism design theory** with **simulation** to (1) characterize distortions in the current system, (2) propose the Method of Equal Shares as an alternative, and (3) evaluate the proposed reform via counterfactual simulation. Analysis of real municipal voting data and household survey data is planned as follow-up work.

The author is a PhD economist and professor at FECA-UJED with SNII status, working in the intersection of microeconomics, operations research, and public policy. The paper targets an economics journal audience.

## Current State of the Project

The theory is fully developed and has been reviewed for internal consistency. The authoritative study document is **`notebooks/notebook_v2.tex`** — a single, self-contained, corrected *Working Notebook (v2)* that supersedes the three original notebooks (`notebook1/2/3.tex`, kept for reference). It covers everything from mechanism-design foundations to the Method of Equal Shares with full proofs, motivations, and worked examples, folding in every correction from the mathematical review. A Python simulation pipeline (`pb_mes/`) compares the DEM and MES. **The paper itself (`paper/main.tex`) still needs to be written by distilling `notebook_v2.tex` into formal paper sections.** Read `notebook_v2.tex` first.

> **Scope note (current paper):** this paper is **theory + simulation**. CONAPO-marginalization weighting of budget shares and the ENIGH welfare extension are **out of scope for this paper** and reserved for follow-up work; the equity guarantee rests on population-proportional EJR, not on need-weighting. (Sections below that mention CONAPO/ENIGH describe that potential future extension, not the current paper.)

### What the Notebooks Contain

**Notebook 1** (Foundations + Proposition 1):
- Mechanism design basics: environments, types, social choice functions, mechanisms, implementation
- The Revelation Principle with full proof
- Incentive compatibility (DSIC and BIC)
- Gibbard-Satterthwaite impossibility theorem with key lemma proved
- The formal PB model: Definition of the environment ⟨N, D, P, B, v, u, σ⟩ including the information function σᵢ
- Formal definitions of the DEM (District-Exclusivity Mechanism) and UAM (Unrestricted Allocation Mechanism)
- **Proposition 1**: Preference truncation causes strict welfare loss under DEM vs UAM

**Notebook 2** (Propositions 2–5):
- **Proposition 2** (Noise Injection): Uninformed votes degrade outcome quality. Signal-noise decomposition of vote totals. Numerical example showing noise exceeds signal for small projects
- **Proposition 3** (Coordination Game): District selection creates a game with multiple Nash equilibria producing different funded sets. Focal points and attention aggregation drive outcomes
- **Proposition 4** (Mobilization Advantage): Institutions like universities act as equilibrium selectors, causing vote displacement of c·v votes from members' preferred districts
- **Proposition 5** (Equity Tradeoff): The UAM destroys geographic equity — low-salience districts get zero funding. The DEM's constraint, despite all its flaws, provides accidental partial protection

**Notebook 3** (The Solution + Comparison):
- Full formal definition of the Method of Equal Shares (MES) with the ρ(p) algorithm
- EJR (Extended Justified Representation) — proof sketch that MES satisfies it
- **Proposition 6.2**: MES implies geographic equity — district with population share βd gets ≥ βd of budget
- **Propositions 6–9**: MES resolves each DEM distortion (no truncation, no forced noise, reduced coordination, bounded mobilization)
- **Proposition 10** (Honest limitation): MES is not strategy-proof (concrete counterexample)
- **Comparison Theorem**: Full property table comparing DEM, UAM, MES
- Complete 300-voter worked example comparing all three mechanisms
- Practical implementation design for Durango, including CONAPO marginalization weighting
- Paper architecture table mapping notebooks → paper sections

## Two Critical Nuances (Must Be Central to the Paper)

These are NOT secondary observations. They shape the entire mechanism design problem.

### 1. Information Asymmetry and Rational Ignorance

Voters typically know only projects in their immediate circle. Under the DEM, a voter who selects a district must allocate all votes (e.g., 6) within it, even if they only care about one project. Remaining votes go to unknown projects — essentially random noise. The mechanism does not incentivize information acquisition. This connects to rational ignorance (Downs, 1957) and costly information acquisition in voting (Martinelli, 2006).

This must appear in: the model (σᵢ information function), distortions (Prop. 2 noise injection), and alternatives (MES allows voters to approve only known projects).

### 2. Centralization Risk and Protection of Marginalized Districts

Removing district exclusivity entirely would let high-visibility city-center projects absorb all votes, disadvantaging marginalized districts. The paper must NOT simply argue "remove the constraint" — it must grapple with why the constraint exists.

This connects to: proportional representation in PB (Peters et al., 2021), CONAPO marginalization indices, and the political economy of decentralization.

This must appear in: introduction (DEM as blunt equity instrument), model (district salience parameter αd), distortions (Prop. 5 equity tradeoff), and alternatives (MES provides equity by construction via EJR).

## Research Questions

1. What strategic and welfare distortions does the district-exclusivity constraint introduce?
2. What alternative mechanisms mitigate these distortions while preserving geographic equity for marginalized districts?
3. **[NEW — Empirical]** How do these theoretical predictions manifest in Durango's actual voting data?
4. **[NEW — Simulation]** What would the outcomes have been under MES? How much welfare improvement and geographic equity improvement would result?
5. **[NEW — Extension]** Can we link PB allocation outcomes to household welfare data (ENIGH) to measure poverty reduction potential?

## Project Structure

```
pb-mechanism-design/
├── CLAUDE.md                    # This file
├── paper/
│   ├── main.tex                 # Master document
│   ├── preamble.tex             # Packages, macros, theorem environments
│   ├── references.bib           # BibTeX bibliography
│   ├── sections/
│   │   ├── 01-introduction.tex  # Motivation, PB worldwide, Mexican legal framework
│   │   ├── 02-literature.tex    # PB mechanisms, social choice, equal shares
│   │   ├── 03-model.tex         # Formal model and definitions
│   │   ├── 04-distortions.tex   # Propositions 1–5 on DEM failures
│   │   ├── 05-alternatives.tex  # MES definition, Propositions 6–9
│   │   ├── 06-comparison.tex    # Comparison Theorem, property table
│   │   ├── 07-empirical.tex     # Descriptive analysis of Durango voting data
│   │   ├── 08-simulation.tex    # Counterfactual simulations under MES
│   │   ├── 09-enigh.tex         # [Optional] Welfare analysis with ENIGH data
│   │   └── 10-conclusion.tex    # Summary, policy recommendations, limitations
│   ├── figures/                 # TikZ diagrams and generated plots
│   ├── tables/                  # Generated tables
│   └── appendix/
│       └── proofs.tex           # Extended proofs
├── notebooks/
│   ├── notebook1.tex            # Foundations + Proposition 1
│   ├── notebook2.tex            # Propositions 2–5
│   └── notebook3.tex            # MES analysis + Comparison Theorem
├── data/
│   ├── raw/                     # Raw data from transparency requests
│   ├── processed/               # Cleaned datasets
│   └── enigh/                   # ENIGH microdata (if obtained)
├── code/
│   ├── analysis/                # Descriptive statistics and empirical analysis
│   ├── simulation/              # MES simulation engine
│   └── utils/                   # Helper functions, data cleaning
└── transparencia/               # Transparency request templates and correspondence
```

## Tech Stack

- **Paper**: LaTeX, compiled with `latexmk -pdf paper/main.tex`
- **Empirical analysis**: Python (pandas, numpy, matplotlib, seaborn)
- **Simulations**: Python (custom MES implementation)
- **Data**: CSV/Excel from transparency requests; ENIGH microdata from INEGI
- **Bibliography**: BibTeX (natbib with `\citet{}` and `\citep{}`)
- **Clean command**: `latexmk -C` in `paper/`

## LaTeX Conventions

- Use `\input{}` to include sections from `sections/` directory
- Mathematical notation follows economics conventions (see macros in `preamble.tex`)
- Theorem environments: `theorem`, `proposition`, `lemma`, `definition`, `example`, `remark`
- Figures use TikZ for diagrams, matplotlib for data plots (exported to PDF)
- Write in formal academic English; Spanish terms like "presupuesto participativo" in italics
- Tables go in `tables/` as standalone .tex files, included with `\input{}`

## Key Macros (defined in preamble.tex)

- `\voters` → N (set of voters)
- `\districts` → D (set of districts)
- `\projects` → P (set of projects)
- `\votes` → v (vote budget)
- `\util` → u (utility function)
- `\DEM` → District-Exclusivity Mechanism
- `\UAM` → Unrestricted Allocation Mechanism
- `\MES` → Method of Equal Shares
- `\ES` → Equal Shares (short form)

## Writing Style

- Formal academic economics prose
- Propositions state results precisely; proofs follow immediately or go in appendix
- Use concrete examples from Durango to motivate abstract results
- Keep notation consistent — always reference preamble.tex macros
- The paper targets an economics journal (e.g., Journal of Public Economics, Social Choice and Welfare)

## Section-Specific Guidance

### Section 1 (Introduction)
Needs research on:
- History and spread of participatory budgeting worldwide (Porto Alegre 1989, Europe, Asia)
- PB adoption in Mexican municipalities — which cities use it, legal basis (Ley de Participación Ciudadana at state level), how common it is
- Durango's specific PB rules, legal framework, budget amounts, participation rates
- Voting systems used in PB internationally — what rules other cities use, how they compare to Durango's

This section requires web research and possibly consultation of Mexican legislative databases (leyes de participación ciudadana by state).

### Sections 3–6 (Theory)
Content is fully developed in the three notebooks. Distill, don't copy verbatim — the paper should be tighter and more formal than the notebooks, with extended proofs in the appendix.

### Section 7 (Empirical — Voting Data)
Data needed (request via Plataforma Nacional de Transparencia or direct from Municipio de Durango):
- Project list by district: name, description, cost, district
- Vote totals by project
- Number of registered voters by district
- Number of participating voters by district
- Ideally: individual ballot data (which district each voter selected, vote allocation)
- Historical data if PB has been conducted multiple years

Analysis to perform:
- Descriptive statistics: participation rates by district, vote concentration, project costs
- Test for mobilization effects: do districts with universities/large employers get disproportionate votes?
- Test for noise: is vote distribution within districts consistent with informed voting or random allocation?
- Measure geographic equity: how does funding correlate with district marginalization (CONAPO)?

### Section 8 (Simulation)
Using the real voting data:
- Implement the MES algorithm in Python
- Run counterfactual: given the same ballots, what would MES have funded?
- Compare: funded project set, total welfare (using vote totals as proxy for preferences), geographic distribution
- Sensitivity analysis: vary the completion method, try weighted shares (CONAPO), vary ballot format assumptions
- If individual ballot data unavailable, generate synthetic ballots consistent with the aggregate data

### Section 9 (ENIGH Extension — Optional)
If data allows:
- Link districts to ENIGH's geographic identifiers (municipality, locality)
- Characterize household income/poverty at the district level
- Measure: does the DEM's funded project set target high-need areas? Would MES do better?
- This requires ENIGH 2022 microdata from INEGI (publicly available) and a mapping between PB districts and ENIGH geographic units

## Data Acquisition Plan

### Transparency Request (Solicitud de Acceso a la Información)
- Platform: Plataforma Nacional de Transparencia (https://www.plataformadetransparencia.org.mx/)
- Directed to: Municipio de Durango, specifically the Dirección de Participación Ciudadana or equivalent
- Request the following:
  1. Resultados del presupuesto participativo [year(s)]: lista de proyectos registrados por distrito, costo estimado, votos recibidos, y estatus de financiamiento
  2. Datos de participación: número de votantes registrados y participantes por distrito
  3. Reglas de votación: reglamento o lineamientos del presupuesto participativo vigente
  4. Si está disponible: datos desagregados de boletas individuales (distrito seleccionado y distribución de votos por proyecto)

### ENIGH Data
- Source: INEGI (https://www.inegi.org.mx/programas/enigh/)
- Download: ENIGH 2022 nueva serie, microdatos
- Key tables: concentradohogar (household income), viviendas (housing), población (demographics)
- Geographic matching: use entidad + municipio codes to link to Durango's PB districts

### CONAPO Marginalization Index
- Source: CONAPO (https://www.gob.mx/conapo)
- Index available at municipio and AGEB (census tract) level
- Use AGEB-level data to compute marginalization by PB district

## Don'ts

- Don't change notation without updating preamble.tex macros
- Don't add packages to individual section files — all packages go in preamble.tex
- Don't hardcode numbers that should be variables (use macros)
- Don't remove or reorganize sections without explicit instruction
- Don't write simulation code without first reading the notebooks to understand the mechanisms
- Don't assume the data structure — the transparency request may return data in unexpected formats
- Don't merge empirical and theoretical sections — keep them cleanly separated