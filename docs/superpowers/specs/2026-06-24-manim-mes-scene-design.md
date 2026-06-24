# Design Spec: Manim MES Algorithm Scene

**Date:** 2026-06-24  
**Status:** Approved  
**Output:** Standalone MP4, played mid-talk (not embedded in Beamer PDF)  
**Duration:** ~65 seconds  
**Audience:** Policy / mixed (municipal government, civil society)

---

## Goal

Animate the Method of Equal Shares (MES) algorithm step-by-step using the 4-voter worked example from the paper. The animation must make the algorithm *self-explanatory* — a non-economist watching it once should understand why coins flow where they do, why some projects win early and others go to the completion phase, and why the marginal district ends up with funded projects without any geographic constraint.

---

## Source Data (4-voter example, shadow paper §3)

```
Budget B = 100,  n = 4 voters,  b_i = B/n = 25 each

Voters:
  v1 approves {p1, p3}
  v2 approves {p1, p3}
  v3 approves {p1, p2}
  v4 approves {p2, p4}

Projects:
  p1  cost=40  district=Center   (ujedblue)
  p2  cost=30  district=Marginal (mesdark)
  p3  cost=50  district=Center   (ujedblue)
  p4  cost=20  district=Marginal (mesdark)
```

**Corrected algorithm trace** (NOTE: presentation slides have a bug in Round 2 — see memory/slide-bug-mes-round2.md):

| Round | Winner | ρ    | Coins paid by supporters | Balances after |
|-------|--------|------|--------------------------|----------------|
| 1     | p1     | 13.33 | v1: 13.33, v2: 13.33, v3: 13.33 | v1=11.67, v2=11.67, v3=11.67, v4=25 |
| 2     | p2     | 18.33 | v3: 11.67 (all), v4: 18.33 | v1=11.67, v2=11.67, v3=0, v4=6.67 |
| 3     | —      | —    | p3 infeasible (23.3<50), p4 infeasible (6.67<20) | MES phase ends |
| Completion | p4 | — | 20 coins from remaining pool (30 available) | 10 coins unused |

Final: W = {p1, p2, p4}. p3 not funded.

---

## Visual Metaphor

**Budget = coins.** Each voter holds 25 gold coins (small filled circles, `ujedaccent` color). Coins physically travel along approval lines to fund projects. When a voter's stack empties, they are exhausted and cannot contribute further.

---

## Layout

Three fixed zones — no zone moves during the animation:

```
┌─────────────────────────────────────────────────────┐
│  [title / round label]                              │
│                                                     │
│  v1 ●──────────────────── p1 [████░░░░░] cost=40   │
│  v2 ●──────────────────── p2 [░░░░░░░░░] cost=30   │
│  v3 ●─────────┬────────── p3 [░░░░░░░░░] cost=50   │
│  v4 ●─────────┘────────── p4 [░░░░░░░░░] cost=20   │
│                                                     │
│  [status / completion pool]                         │
└─────────────────────────────────────────────────────┘
```

- **Left column:** 4 voter circles with coin stacks below. Stacks are schematic — shown as 5–6 stacked coin-circles with a numeric label (e.g. "25 coins"), not 25 individual circles. The label updates live as coins leave; the stack height shrinks proportionally.
- **Center:** Dotted approval lines. Always visible. Each voter's lines are drawn at setup and remain throughout.
- **Right column:** 4 project cards. Each card: project name, district label (colored), cost, and a horizontal cost bar (empty → fills left-to-right as coins arrive).
- **Bottom center:** Remaining budget pool (appears in Act 4).
- **Top:** Title (Act 1) replaced by round label (Acts 2–5).

### Color palette (matches Beamer)

| Element | Color | Hex |
|---------|-------|-----|
| Center district projects (p1, p3) | ujedblue | #003580 |
| Marginal district projects (p2, p4) | mesdark | #1A6B3A |
| Coins | ujedaccent | #D4A017 |
| Infeasible marker | demdark | #8B1A1A |
| Funded checkmark | mesdark | #1A6B3A |
| ρ label (winner) | ujedaccent | #D4A017 |
| ρ label (others) | neutral | #555555 |

---

## Acts

### Act 1 — Setup (8s)

1. Title "Method of Equal Shares" writes in at top.
2. Equation `B = 100 · n = 4 · b_i = 25` fades in below title.
3. Voter circles materialize left-to-right with a brief scale-in. Coin stacks drop in beneath each.
4. Project cards slide in from the right, one by one.
5. Approval lines draw themselves in per voter (LaggedStart), dotted stroke. Pause so the audience reads the approval structure.

### Act 2 — Round 1 (18s)

1. Title replaced by "Round 1" label.
2. ρ values appear simultaneously above each project card:
   - ρ(p1) = 13.3 → gold (winner)
   - ρ(p2) = 15.0 → grey
   - ρ(p3) = 25.0 → grey
   - ρ(p4) = 20.0 → grey
3. p1 card pulses with a gold surrounding rectangle.
4. Coins travel in three waves: v1 → p1, then v2 → p1, then v3 → p1. Each wave is a small cluster of 3–5 coin-circles (schematic, not one per coin) moving along the approval line. The cost bar on p1 fills incrementally with each wave, driven by a ValueTracker.
5. Coin stacks on v1, v2, v3 shrink (animate from 25 to 11.67). Live labels update.
6. p1 card: green ✓ "FUNDED" appears. ρ labels fade out.

### Act 3 — Round 2 (18s)

1. "Round 2" label.
2. New ρ values appear:
   - p1: greyed out (already funded)
   - ρ(p2) = 18.33 → gold (winner)
   - p3: red ✗ "infeasible (23.3 < 50)"
   - ρ(p4) = 20.0 → grey
3. p2 card pulses gold.
4. v3's entire stack travels to p2 — the stack empties dramatically (all coins leave at once).
5. v4 sends 18.33 coins to p2. Cost bar on p2 fills to full.
6. v3 stack: gone (label shows 0). v4 stack shrinks to 6.67.
7. p2: green ✓ "FUNDED". ρ labels fade out.

### Act 4 — MES phase ends (8s)

1. "Round 3" label.
2. p3: red ✗ with annotation "v1+v2 = 23.3 < 50".
3. p4: red ✗ with annotation "v4 = 6.67 < 20".
4. Text at bottom: "No affordable project — MES phase complete."
5. A pool of 30 gold coins materializes at bottom center, labeled "remaining budget: 30."

### Act 5 — Completion + finale (13s)

1. "Completion phase" label.
2. 20 coins travel from the pool to p4. Cost bar fills. Green ✓ "FUNDED".
3. 10 coins remain in the pool. p3 card fades to 30% opacity (too expensive at cost 50).
4. Brief pause. Then:
   - p1, p2, p4 cards glow green.
   - Text fades in: "W = {p1, p2, p4}"
   - Second line: "Marginal district: 2 of 3 projects — no geographic constraint needed."

---

## File Structure

```
pb_mes/manim/
├── __init__.py
├── styles.py          # PALETTE dict, make_coin(), make_voter(), make_project_card(), make_cost_bar()
├── scene_mes.py       # MESScene — the scene described in this spec
└── media/             # gitignored — rendered output
```

**Note:** Path is `pb_mes/manim/` (not `code/manim/` as in the older draft plan) to avoid the Python stdlib `code` module shadow. Internal imports use `from pb_mes.manim.styles import ...`.

---

## Technical Constraints

- **Manim Community Edition ≥ 0.18** (`pip install manim`)
- **System deps (macOS):** `brew install cairo pango ffmpeg`
- **Preview render:** `manim -pql pb_mes/manim/scene_mes.py MESScene`
- **Production render:** `manim -pqh pb_mes/manim/scene_mes.py MESScene`
- Output goes to `pb_mes/manim/media/videos/` (gitignored)
- Math labels: `MathTex` (not `Tex`) for all equations
- No voiceover; all information on-screen
- Coin travel: use `MoveAlongPath` or `animate.move_to()` with `lag_ratio` for the cluster effect
- Cost bar fill: `ValueTracker` + `always_redraw` rectangle

---

## Out of Scope

- Embedding in Beamer PDF (separate task if desired later)
- Scene 1 (DEM distortions) and Scene 3 (comparison table) from the older draft plan — those are deferred; this scene is the priority
- Voiceover or subtitles
- The equity paradox animation (discussed but deprioritized in favor of this scene)
