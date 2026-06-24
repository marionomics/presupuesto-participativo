# Manim MES Animation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a ~65-second standalone MP4 that animates the MES algorithm step-by-step on the 4-voter example using coins as a budget metaphor.

**Architecture:** Two files — `styles.py` (palette, data constants, helper functions) and `scene_mes.py` (MESScene class with one method per act). Acts are called in sequence from `construct()`. Coin travel is a reusable `_send_coins()` helper. Cost bars and voter balances are driven by `ValueTracker` + `always_redraw`.

**Tech Stack:** Manim Community Edition ≥ 0.18, Python 3.10+, ffmpeg, Cairo, Pango

## Global Constraints

- Manim Community (NOT 3b1b's manimlib): `pip install manim`
- macOS system deps first: `brew install cairo pango ffmpeg`
- All source under `pb_mes/manim/` — NOT `code/manim/` (stdlib shadow)
- Within scene files import styles as `from styles import PALETTE` (Manim adds the scene file's directory to sys.path, so no package prefix needed)
- Color palette — exact hex values:
  - `ujedblue` = `#003580` (Center district, voter circles v1/v2)
  - `ujedaccent` = `#D4A017` (coins, ρ winner highlight)
  - `mesdark` = `#1A6B3A` (Marginal district, funded markers)
  - `demdark` = `#8B1A1A` (infeasible markers)
  - `neutral` = `#555555` (labels, cost bars background)
  - `bg` = `#FAFAFA` (scene background)
- Preview render command (run from project root): `manim -pql pb_mes/manim/scene_mes.py MESScene`
- Production render: `manim -pqh pb_mes/manim/scene_mes.py MESScene`
- Output directory `pb_mes/manim/media/` must be gitignored
- Algorithm data — CORRECTED (presentation slides have a bug in Round 2; use these values):
  - Round 1: p1 wins (ρ=13.33), v1/v2/v3 each pay 13.33 → balances: v1=v2=v3=11.67, v4=25.0
  - Round 2: p2 wins (ρ=18.33), v3 pays 11.67 (exhausted), v4 pays 18.33 → v1=v2=11.67, v3=0, v4=6.67
  - MES stops: p3 infeasible (v1+v2=23.3 < 50), p4 infeasible (v4=6.67 < 20)
  - Completion: p4 funded from remaining pool (cost 20 ≤ 30 remaining)
  - Final: W = {p1, p2, p4}

---

## File Map

| File | Responsibility |
|------|----------------|
| `pb_mes/manim/__init__.py` | Empty — marks directory as Python package |
| `pb_mes/manim/styles.py` | PALETTE dict, layout constants, VOTERS_DATA, PROJECTS_DATA, `make_coin()`, `make_voter_node()`, `make_project_card()`, `make_cost_bar()` |
| `pb_mes/manim/scene_mes.py` | `MESScene` class: `construct()`, `_build_objects()`, `_act1_setup()` through `_act5_completion()`, `_send_coins()` |
| `.gitignore` | Add `pb_mes/manim/media/` |

---

## Task 1: Environment + Styles Module

**Files:**
- Create: `pb_mes/manim/__init__.py`
- Create: `pb_mes/manim/styles.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces:
  - `PALETTE: dict[str, str]` — color hex strings
  - `VOTERS_DATA: list[dict]` — id, approves, color per voter
  - `PROJECTS_DATA: list[dict]` — id, name, cost, district, color per project
  - `VOTER_X: float`, `PROJECT_X: float`, `VOTER_YS: list[float]`, `PROJECT_YS: list[float]`
  - `make_coin(color, radius) -> Circle`
  - `make_voter_node(vid, color) -> tuple[VGroup, ValueTracker]` — (circle+label VGroup, balance tracker starting at 25)
  - `make_project_card(name, cost, district, color) -> VGroup`
  - `make_cost_bar(cost, color) -> tuple[VGroup, ValueTracker]` — (bg+fill VGroup, fill tracker starting at 0)

- [ ] **Step 1: Install Manim and verify environment**

```bash
brew install cairo pango ffmpeg
pip install manim
manim --version
ffmpeg -version | head -1
```

Expected output line 1: `Manim Community v0.18.x` (or newer)
Expected output line 2: `ffmpeg version ...`

If `manim --version` fails, check that `pip install manim` completed without errors and that the active Python environment's bin directory is on PATH.

- [ ] **Step 2: Create directory and empty init**

```bash
mkdir -p pb_mes/manim
touch pb_mes/manim/__init__.py
```

- [ ] **Step 3: Add media output to .gitignore**

```bash
echo "pb_mes/manim/media/" >> .gitignore
```

- [ ] **Step 4: Write styles.py**

Create `pb_mes/manim/styles.py`:

```python
from manim import *

PALETTE = {
    "ujedblue":   "#003580",
    "ujeddark":   "#001F4D",
    "ujedaccent": "#D4A017",
    "mesdark":    "#1A6B3A",
    "demdark":    "#8B1A1A",
    "uamdark":    "#4A4A8A",
    "neutral":    "#555555",
    "bg":         "#FAFAFA",
    "white":      "#FFFFFF",
}

# Layout constants (16:9 frame: x in [-7.1, 7.1], y in [-4, 4])
VOTER_X = -5.2
PROJECT_X = 2.0
VOTER_YS = [2.4, 0.8, -0.8, -2.4]
PROJECT_YS = [2.4, 0.8, -0.8, -2.4]
STACK_Y_OFFSET = -1.0   # coin stack center below voter circle center
COST_BAR_Y_OFFSET = -0.62  # cost bar center below project card center

VOTERS_DATA = [
    {"id": "v1", "approves": {"p1", "p3"}, "color": PALETTE["ujedblue"]},
    {"id": "v2", "approves": {"p1", "p3"}, "color": PALETTE["ujedblue"]},
    {"id": "v3", "approves": {"p1", "p2"}, "color": PALETTE["uamdark"]},
    {"id": "v4", "approves": {"p2", "p4"}, "color": PALETTE["demdark"]},
]

PROJECTS_DATA = [
    {"id": "p1", "name": "Park renovation", "cost": 40, "district": "Center",   "color": PALETTE["ujedblue"]},
    {"id": "p2", "name": "School repair",   "cost": 30, "district": "Marginal", "color": PALETTE["mesdark"]},
    {"id": "p3", "name": "Road paving",     "cost": 50, "district": "Center",   "color": PALETTE["ujedblue"]},
    {"id": "p4", "name": "Water access",    "cost": 20, "district": "Marginal", "color": PALETTE["mesdark"]},
]


def make_coin(color: str = PALETTE["ujedaccent"], radius: float = 0.09) -> Circle:
    return Circle(radius=radius, fill_color=color, fill_opacity=1.0,
                  stroke_color=PALETTE["ujeddark"], stroke_width=0.5)


def make_voter_node(vid: str, color: str) -> tuple[VGroup, ValueTracker]:
    """
    Returns (voter_vgroup, balance_tracker).
    voter_vgroup contains: circle, label, schematic coin stack (5 coins max),
    and a DecimalNumber label showing the current balance.
    balance_tracker starts at 25.0; animate it to update the stack and label.
    """
    tracker = ValueTracker(25.0)

    circle = Circle(radius=0.35, fill_color=color, fill_opacity=0.9,
                    stroke_color=color, stroke_width=2)
    lbl = Text(vid, font_size=20, color=WHITE).move_to(circle)
    voter_dot = VGroup(circle, lbl)

    # Schematic coin stack: 5 circles, height scales with tracker
    def build_stack():
        ratio = max(tracker.get_value() / 25.0, 0.0)
        n = max(int(round(ratio * 5)), 0)
        stack = VGroup(*[
            make_coin().shift(UP * i * 0.16)
            for i in range(n)
        ])
        # Balance label below stack
        bal = Text(f"{tracker.get_value():.1f}", font_size=13,
                   color=PALETTE["neutral"])
        if n > 0:
            bal.next_to(stack, DOWN, buff=0.08)
        else:
            bal.shift(DOWN * 0.1)
        return VGroup(stack, bal)

    coin_stack = always_redraw(build_stack)
    return VGroup(voter_dot, coin_stack), tracker


def make_project_card(name: str, cost: float, district: str,
                      color: str) -> VGroup:
    """Static project card — name, district, cost. Width=3.4, height=0.85."""
    rect = RoundedRectangle(corner_radius=0.1, width=3.4, height=0.85,
                             fill_color=color, fill_opacity=0.1,
                             stroke_color=color, stroke_width=2)
    name_lbl = Text(name, font_size=15, color=color).move_to(rect).shift(UP * 0.2)
    dist_lbl = Text(district, font_size=11, color=PALETTE["neutral"]).move_to(rect)
    cost_lbl = Text(f"cost = {cost:.0f}", font_size=12,
                    color=PALETTE["neutral"]).move_to(rect).shift(DOWN * 0.22)
    return VGroup(rect, name_lbl, dist_lbl, cost_lbl)


def make_cost_bar(cost: float, color: str,
                  bar_width: float = 3.0) -> tuple[VGroup, ValueTracker]:
    """
    Returns (bar_vgroup, fill_tracker).
    fill_tracker starts at 0; animate it toward `cost` to fill the bar.
    bar_vgroup contains a grey background rect and a colored fill rect.
    """
    tracker = ValueTracker(0.0)
    bg = Rectangle(width=bar_width, height=0.18,
                   fill_color=PALETTE["neutral"], fill_opacity=0.2,
                   stroke_color=PALETTE["neutral"], stroke_width=0.5)

    def build_fill():
        ratio = min(tracker.get_value() / cost, 1.0) if cost > 0 else 0.0
        w = max(ratio * bar_width, 0.001)
        return Rectangle(width=w, height=0.18,
                         fill_color=color, fill_opacity=0.85,
                         stroke_width=0).align_to(bg, LEFT)

    fill = always_redraw(build_fill)
    return VGroup(bg, fill), tracker
```

- [ ] **Step 5: Smoke-test the import**

Create `pb_mes/manim/test_smoke.py`:

```python
from manim import *
from styles import PALETTE, VOTERS_DATA, PROJECTS_DATA
from styles import make_voter_node, make_project_card, make_cost_bar

class SmokeTest(Scene):
    def construct(self):
        self.camera.background_color = PALETTE["bg"]
        voter, tracker = make_voter_node("v1", PALETTE["ujedblue"])
        voter.move_to(LEFT * 3)
        self.add(voter)

        card = make_project_card("Park", 40, "Center", PALETTE["ujedblue"])
        card.move_to(RIGHT * 2)
        self.add(card)

        bar, bar_tracker = make_cost_bar(40, PALETTE["ujedblue"])
        bar.next_to(card, DOWN, buff=0.15)
        self.add(bar)

        self.play(bar_tracker.animate.set_value(40), run_time=1.5)
        self.play(tracker.animate.set_value(11.67), run_time=1.0)
        self.wait(0.5)
```

```bash
cd /Users/marionomics/Documents/trabajo/Research/PAPERS/2026/presupuesto-participativo
manim -pql pb_mes/manim/test_smoke.py SmokeTest
```

Expected: preview window opens. Voter circle appears with coin stack. Project card appears. Cost bar fills from left to right. Coin stack shrinks. No Python errors.

- [ ] **Step 6: Commit**

```bash
git add pb_mes/manim/__init__.py pb_mes/manim/styles.py pb_mes/manim/test_smoke.py .gitignore
git commit -m "feat: Manim styles module, palette, and smoke test"
```

---

## Task 2: Scene Skeleton + Act 1 (Setup)

**Files:**
- Create: `pb_mes/manim/scene_mes.py`

**Interfaces:**
- Consumes: `styles.py` — all exports from Task 1
- Produces: `MESScene` class with `construct()`, `_build_objects()`, `_act1_setup()` implemented; remaining act methods are `pass` stubs.

After this task, running the preview shows: title writes in, budget equation appears, 4 voter circles materialize with coin stacks, 4 project cards slide in, dotted approval lines draw.

- [ ] **Step 1: Write scene_mes.py with skeleton and Act 1**

Create `pb_mes/manim/scene_mes.py`:

```python
from manim import *
from styles import (
    PALETTE, VOTERS_DATA, PROJECTS_DATA,
    VOTER_X, PROJECT_X, VOTER_YS, PROJECT_YS,
    STACK_Y_OFFSET, COST_BAR_Y_OFFSET,
    make_voter_node, make_project_card, make_cost_bar, make_coin,
)

class MESScene(Scene):
    def construct(self):
        self.camera.background_color = PALETTE["bg"]
        self._build_objects()
        self._act1_setup()
        self._act2_round1()
        self._act3_round2()
        self._act4_mes_stops()
        self._act5_completion()

    # ── Object construction ────────────────────────────────────────────

    def _build_objects(self):
        """Create all visual objects and store as instance variables."""

        # Voters: circle+label VGroup and balance tracker
        self.voter_nodes = []    # list of VGroup (positioned)
        self.voter_trackers = [] # list of ValueTracker

        for i, vd in enumerate(VOTERS_DATA):
            node, tracker = make_voter_node(vd["id"], vd["color"])
            # voter circle at (VOTER_X, VOTER_YS[i])
            node[0].move_to([VOTER_X, VOTER_YS[i], 0])
            # coin stack below
            node[1].move_to([VOTER_X, VOTER_YS[i] + STACK_Y_OFFSET, 0])
            self.voter_nodes.append(node)
            self.voter_trackers.append(tracker)

        # Projects: card VGroup, cost bar VGroup, cost bar tracker
        self.project_cards = []
        self.cost_bars = []
        self.cost_trackers = []

        for i, pd in enumerate(PROJECTS_DATA):
            card = make_project_card(pd["name"], pd["cost"],
                                     pd["district"], pd["color"])
            card.move_to([PROJECT_X, PROJECT_YS[i], 0])
            self.project_cards.append(card)

            bar, bar_tracker = make_cost_bar(pd["cost"], pd["color"])
            bar.move_to([PROJECT_X, PROJECT_YS[i] + COST_BAR_Y_OFFSET, 0])
            self.cost_bars.append(bar)
            self.cost_trackers.append(bar_tracker)

        # Approval lines (DashedLine from voter to project)
        # voter_idx -> list of project_idxs approved
        pid_to_idx = {pd["id"]: i for i, pd in enumerate(PROJECTS_DATA)}
        self.approval_lines = {}  # (voter_idx, project_idx) -> DashedLine

        for vi, vd in enumerate(VOTERS_DATA):
            voter_center = np.array([VOTER_X, VOTER_YS[vi], 0])
            for pid in vd["approves"]:
                pi = pid_to_idx[pid]
                proj_center = np.array([PROJECT_X, PROJECT_YS[pi], 0])
                line = DashedLine(
                    voter_center, proj_center,
                    dash_length=0.12, dashed_ratio=0.5,
                    stroke_color=PALETTE["neutral"],
                    stroke_opacity=0.5, stroke_width=1.5,
                )
                self.approval_lines[(vi, pi)] = line

        # Round label (top center, replaced each act)
        self.round_label = Text("", font_size=24, color=PALETTE["ujedblue"])
        self.round_label.to_edge(UP, buff=0.3)

    # ── Act 1: Setup ───────────────────────────────────────────────────

    def _act1_setup(self):
        # Title
        title = Text("Method of Equal Shares", font_size=34,
                     color=PALETTE["ujedblue"]).to_edge(UP, buff=0.25)
        eq = MathTex(r"B = 100,\quad n = 4,\quad b_i = 25",
                     font_size=22, color=PALETTE["neutral"])
        eq.next_to(title, DOWN, buff=0.15)

        self.play(Write(title))
        self.play(FadeIn(eq, shift=UP * 0.2))
        self.wait(1)

        # Voters materialize
        self.play(LaggedStart(
            *[FadeIn(node[0], scale=0.7) for node in self.voter_nodes],
            lag_ratio=0.2,
        ))
        # Coin stacks drop in
        self.play(LaggedStart(
            *[FadeIn(node[1], shift=UP * 0.3) for node in self.voter_nodes],
            lag_ratio=0.15,
        ))
        self.wait(0.5)

        # Project cards slide in from right
        for card in self.project_cards:
            card.shift(RIGHT * 2)
        self.play(LaggedStart(
            *[card.animate.shift(LEFT * 2) for card in self.project_cards],
            lag_ratio=0.2,
        ))

        # Cost bars appear below cards
        self.play(LaggedStart(
            *[FadeIn(bar) for bar in self.cost_bars],
            lag_ratio=0.15,
        ))
        self.wait(0.5)

        # Approval lines draw one voter at a time
        for vi in range(len(VOTERS_DATA)):
            lines = [self.approval_lines[(vi, pi)]
                     for pi in range(len(PROJECTS_DATA))
                     if (vi, pi) in self.approval_lines]
            self.play(LaggedStart(
                *[Create(line) for line in lines],
                lag_ratio=0.3, run_time=0.8,
            ))

        self.wait(1)

        # Swap title for round label area
        self.play(FadeOut(title), FadeOut(eq))
        self.wait(0.3)

    # ── Stubs for later tasks ──────────────────────────────────────────

    def _act2_round1(self):
        pass

    def _act3_round2(self):
        pass

    def _act4_mes_stops(self):
        pass

    def _act5_completion(self):
        pass

    def _send_coins(self, voter_idx: int, project_idx: int,
                    amount: float, run_time: float = 1.4):
        pass
```

- [ ] **Step 2: Render preview of Act 1**

```bash
manim -pql pb_mes/manim/scene_mes.py MESScene
```

Expected: title writes in, equation fades, voter circles appear, coin stacks drop in, project cards slide in, cost bars appear, approval lines draw. Scene ends (remaining acts are stubs). No Python errors.

If you see layout overlap, adjust `VOTER_X`, `PROJECT_X`, `VOTER_YS`, `PROJECT_YS` in `styles.py` to taste. Coins, voter circles, and project cards should have breathing room.

- [ ] **Step 3: Commit**

```bash
git add pb_mes/manim/scene_mes.py
git commit -m "feat: MES scene skeleton and Act 1 setup animation"
```

---

## Task 3: Acts 2 and 3 — Rounds 1 and 2

**Files:**
- Modify: `pb_mes/manim/scene_mes.py` — implement `_send_coins()`, `_act2_round1()`, `_act3_round2()`

**Interfaces:**
- Consumes: all instance variables set in `_build_objects()` from Task 2
- Produces: `_send_coins(voter_idx, project_idx, amount, run_time)` helper usable by any act; `_act2_round1()` and `_act3_round2()` fully animated

**Algorithm values to use (hardcoded — do not compute dynamically):**

Round 1: p1 (idx=0) wins. ρ values: p1=13.3, p2=15.0, p3=25.0, p4=20.0.
Deductions: v1→13.33, v2→13.33, v3→13.33. New balances: v1=v2=v3=11.67, v4=25.0.

Round 2: p2 (idx=1) wins. ρ values: p2=18.33, p4=20.0, p3=infeasible.
Deductions: v3→11.67 (exhausted), v4→18.33. New balances: v1=v2=11.67, v3=0, v4=6.67.

- [ ] **Step 1: Implement `_send_coins()` helper**

Replace the `_send_coins` stub in `scene_mes.py`:

```python
def _send_coins(self, voter_idx: int, project_idx: int,
                amount: float, run_time: float = 1.4):
    """
    Animate a cluster of 4 coin-circles traveling from voter to project.
    Simultaneously: fill the project's cost bar by `amount`, shrink the voter's balance.
    """
    voter_pos = np.array([VOTER_X, VOTER_YS[voter_idx], 0])
    proj_pos = np.array([PROJECT_X, PROJECT_YS[project_idx], 0])

    # 4 coins spread slightly around the voter's stack center
    coins = VGroup(*[
        make_coin().move_to(
            voter_pos + DOWN * abs(STACK_Y_OFFSET) * 0.5
            + RIGHT * (j - 1.5) * 0.08
        )
        for j in range(4)
    ])
    self.add(coins)

    # Animate: coins travel to project card, bar fills, balance shrinks
    old_tracker_val = self.voter_trackers[voter_idx].get_value()
    old_bar_val = self.cost_trackers[project_idx].get_value()

    self.play(
        coins.animate.move_to(proj_pos),
        self.voter_trackers[voter_idx].animate.set_value(
            max(old_tracker_val - amount, 0.0)
        ),
        self.cost_trackers[project_idx].animate.set_value(
            old_bar_val + amount
        ),
        run_time=run_time,
    )
    self.remove(coins)
```

- [ ] **Step 2: Implement `_act2_round1()`**

Replace the `_act2_round1` stub:

```python
def _act2_round1(self):
    # Round label
    r1_lbl = Text("Round 1", font_size=26, color=PALETTE["ujedblue"])
    r1_lbl.to_edge(UP, buff=0.25)
    self.play(Write(r1_lbl))

    # Show ρ values above each project card
    rho_data = [("13.3", True), ("15.0", False), ("25.0", False), ("20.0", False)]
    rho_labels = VGroup()
    for i, (val, is_winner) in enumerate(rho_data):
        color = PALETTE["ujedaccent"] if is_winner else PALETTE["neutral"]
        size = 18 if is_winner else 14
        lbl = Text(f"ϱ = {val}", font_size=size, color=color)
        lbl.next_to(self.project_cards[i], UP, buff=0.12)
        rho_labels.add(lbl)

    self.play(LaggedStart(*[FadeIn(r) for r in rho_labels], lag_ratio=0.15))
    self.wait(0.5)

    # Highlight p1 (winner)
    p1_box = SurroundingRectangle(self.project_cards[0],
                                   color=PALETTE["ujedaccent"], stroke_width=2.5)
    self.play(Create(p1_box))
    self.wait(0.3)

    # Three coin waves: v1→p1, v2→p1, v3→p1
    for vi in [0, 1, 2]:
        self._send_coins(vi, 0, amount=13.33, run_time=1.2)

    # Funded marker on p1
    check = Text("✓ FUNDED", font_size=14, color=PALETTE["mesdark"])
    check.next_to(self.cost_bars[0], DOWN, buff=0.1)
    self.play(FadeIn(check, scale=1.2))
    self.wait(0.5)

    self.play(FadeOut(rho_labels), FadeOut(p1_box), FadeOut(r1_lbl))
    self.wait(0.3)
```

- [ ] **Step 3: Implement `_act3_round2()`**

Replace the `_act3_round2` stub:

```python
def _act3_round2(self):
    r2_lbl = Text("Round 2", font_size=26, color=PALETTE["ujedblue"])
    r2_lbl.to_edge(UP, buff=0.25)
    self.play(Write(r2_lbl))

    # ρ labels — p1 already funded (skip), p3 infeasible, p2 wins
    rho_labels = VGroup()

    # p1 funded label (grey, small)
    lbl_p1 = Text("(funded)", font_size=12, color=PALETTE["neutral"])
    lbl_p1.next_to(self.project_cards[0], UP, buff=0.12)
    rho_labels.add(lbl_p1)

    # p2 winner
    lbl_p2 = Text("ϱ = 18.33", font_size=18, color=PALETTE["ujedaccent"])
    lbl_p2.next_to(self.project_cards[1], UP, buff=0.12)
    rho_labels.add(lbl_p2)

    # p3 infeasible
    lbl_p3 = Text("✗ infeasible", font_size=13, color=PALETTE["demdark"])
    lbl_p3.next_to(self.project_cards[2], UP, buff=0.12)
    rho_labels.add(lbl_p3)

    # p4 feasible but not winner
    lbl_p4 = Text("ϱ = 20.0", font_size=14, color=PALETTE["neutral"])
    lbl_p4.next_to(self.project_cards[3], UP, buff=0.12)
    rho_labels.add(lbl_p4)

    self.play(LaggedStart(*[FadeIn(r) for r in rho_labels], lag_ratio=0.15))
    self.wait(0.5)

    # Highlight p2
    p2_box = SurroundingRectangle(self.project_cards[1],
                                   color=PALETTE["ujedaccent"], stroke_width=2.5)
    self.play(Create(p2_box))
    self.wait(0.3)

    # v3 exhausted: sends all 11.67 coins to p2
    self._send_coins(2, 1, amount=11.67, run_time=1.3)

    # v4 sends 18.33 coins to p2
    self._send_coins(3, 1, amount=18.33, run_time=1.3)

    # Funded marker on p2
    check2 = Text("✓ FUNDED", font_size=14, color=PALETTE["mesdark"])
    check2.next_to(self.cost_bars[1], DOWN, buff=0.1)
    self.play(FadeIn(check2, scale=1.2))
    self.wait(0.5)

    self.play(FadeOut(rho_labels), FadeOut(p2_box), FadeOut(r2_lbl))
    self.wait(0.3)
```

- [ ] **Step 4: Render preview through Round 2**

```bash
manim -pql pb_mes/manim/scene_mes.py MESScene
```

Expected: after Act 1, Round 1 label appears, ρ values show above project cards, p1 glows gold, three coin clusters travel to p1 filling its bar, stacks shrink, ✓ FUNDED appears. Round 2: p2 glows, v3's stack empties completely, v4's stack shrinks to ~6.67, p2 bar fills. v3's balance label should read 0.0.

If coin clusters overlap approval lines awkwardly, adjust the scatter offset in `_send_coins` (`RIGHT * (j - 1.5) * 0.08`).

- [ ] **Step 5: Commit**

```bash
git add pb_mes/manim/scene_mes.py
git commit -m "feat: MES animation Acts 2-3, coin travel, Rounds 1 and 2"
```

---

## Task 4: Acts 4 and 5 — MES Stops, Completion, Finale

**Files:**
- Modify: `pb_mes/manim/scene_mes.py` — implement `_act4_mes_stops()` and `_act5_completion()`

**Interfaces:**
- Consumes: all instance variables from `_build_objects()`; voter balances already updated by Acts 2–3 (v1=v2=11.67, v3=0, v4=6.67)
- Produces: complete ~65s animation ending on W = {p1, p2, p4} result frame

**Values (hardcoded):**
- Remaining budget after Rounds 1+2: 100 − 40 − 30 = 30
- p3: v1+v2 = 23.3 < 50 → infeasible
- p4: v4 = 6.67 < 20 → infeasible in MES phase
- Completion: p4 cost=20 ≤ 30 remaining → funded

- [ ] **Step 1: Implement `_act4_mes_stops()`**

Replace the `_act4_mes_stops` stub:

```python
def _act4_mes_stops(self):
    r3_lbl = Text("Round 3", font_size=26, color=PALETTE["ujedblue"])
    r3_lbl.to_edge(UP, buff=0.25)
    self.play(Write(r3_lbl))

    # Infeasibility markers for p3 and p4
    p3_x = Text("✗  v1 + v2 = 23.3 < 50", font_size=13,
                 color=PALETTE["demdark"])
    p3_x.next_to(self.project_cards[2], UP, buff=0.12)

    p4_x = Text("✗  v4 = 6.67 < 20", font_size=13,
                 color=PALETTE["demdark"])
    p4_x.next_to(self.project_cards[3], UP, buff=0.12)

    self.play(FadeIn(p3_x, shift=LEFT * 0.2),
              FadeIn(p4_x, shift=LEFT * 0.2))
    self.wait(0.8)

    # Stop message
    stop_msg = Text("No affordable project — MES phase complete",
                    font_size=18, color=PALETTE["demdark"])
    stop_msg.to_edge(DOWN, buff=0.8)
    self.play(Write(stop_msg))
    self.wait(1.0)

    # Remaining budget pool (30 coins) materializes at bottom center
    pool_label = Text("Remaining budget: 30", font_size=16,
                      color=PALETTE["ujedaccent"])
    pool_label.to_edge(DOWN, buff=0.4)

    # Visual pool: small group of coin circles
    pool_coins = VGroup(*[
        make_coin().shift(RIGHT * (k - 3) * 0.22)
        for k in range(7)  # 7 schematic coins representing 30
    ]).next_to(pool_label, UP, buff=0.1)

    self.play(FadeOut(stop_msg))
    self.play(FadeIn(pool_coins, shift=UP * 0.2), FadeIn(pool_label))
    self.wait(0.8)

    # Store pool for Act 5
    self._pool_coins = pool_coins
    self._pool_label = pool_label

    self.play(FadeOut(p3_x), FadeOut(p4_x), FadeOut(r3_lbl))
    self.wait(0.3)
```

- [ ] **Step 2: Implement `_act5_completion()`**

Replace the `_act5_completion` stub:

```python
def _act5_completion(self):
    comp_lbl = Text("Completion phase", font_size=26,
                    color=PALETTE["ujedblue"])
    comp_lbl.to_edge(UP, buff=0.25)
    self.play(Write(comp_lbl))
    self.wait(0.5)

    # 20 coins travel from pool to p4 (project_idx=3)
    pool_center = self._pool_coins.get_center()
    p4_pos = np.array([PROJECT_X, PROJECT_YS[3], 0])

    travel_coins = VGroup(*[
        make_coin().move_to(pool_center + RIGHT * (j - 2) * 0.1)
        for j in range(5)  # schematic 5 coins for cost=20
    ])
    self.add(travel_coins)

    self.play(
        travel_coins.animate.move_to(p4_pos),
        self.cost_trackers[3].animate.set_value(20.0),
        run_time=1.4,
    )
    self.remove(travel_coins)

    # Funded marker on p4
    check4 = Text("✓ FUNDED", font_size=14, color=PALETTE["mesdark"])
    check4.next_to(self.cost_bars[3], DOWN, buff=0.1)
    self.play(FadeIn(check4, scale=1.2))
    self.wait(0.5)

    # Remaining 10 coins: pool shrinks, p3 fades
    leftover_label = Text("10 remaining — p3 too expensive (cost 50)",
                          font_size=13, color=PALETTE["neutral"])
    leftover_label.next_to(self._pool_label, UP, buff=0.08)
    self.play(
        FadeOut(self._pool_coins),
        self.project_cards[2].animate.set_opacity(0.25),
        self.cost_bars[2].animate.set_opacity(0.25),
        FadeIn(leftover_label),
    )
    self.wait(0.8)

    # ── Finale ────────────────────────────────────────────────────────
    self.play(
        FadeOut(comp_lbl),
        FadeOut(leftover_label),
        FadeOut(self._pool_label),
    )

    # Glow funded project cards
    for pi in [0, 1, 3]:  # p1, p2, p4
        box = SurroundingRectangle(self.project_cards[pi],
                                    color=PALETTE["mesdark"], stroke_width=2)
        self.play(Create(box), run_time=0.4)

    result = Text("W  =  { p1 (Park),  p2 (School),  p4 (Water) }",
                  font_size=20, color=PALETTE["mesdark"])
    result.to_edge(DOWN, buff=0.9)

    tagline = Text("Marginal district: 2 of 3 projects funded — no geographic constraint.",
                   font_size=15, color=PALETTE["neutral"])
    tagline.next_to(result, DOWN, buff=0.12)

    self.play(Write(result))
    self.play(FadeIn(tagline, shift=UP * 0.15))
    self.wait(3.5)

    self.play(*[FadeOut(m) for m in self.mobjects])
    self.wait(0.3)
```

- [ ] **Step 3: Render full preview**

```bash
manim -pql pb_mes/manim/scene_mes.py MESScene
```

Expected: all 5 acts play in sequence. Total duration ~60–70 seconds. Check:
- Round 3: two red ✗ infeasibility labels appear, pool of coins materializes at bottom
- Completion: coins travel from pool to p4, p4 bar fills, p3 fades to 25% opacity
- Finale: three green boxes glow around p1, p2, p4; result text and tagline appear; everything fades out

- [ ] **Step 4: Fix timing and positioning issues**

Watch the preview carefully. Common issues to fix:
- If any text overlaps another element, adjust `to_edge(DOWN, buff=X)` or `next_to(..., buff=X)` values
- If coin travel is too fast/slow, adjust `run_time` in `_send_coins` calls
- If the finale glow boxes feel rushed, increase `self.wait()` before fading out
- Re-render with `manim -pql` after each fix until the flow is clean

- [ ] **Step 5: Commit**

```bash
git add pb_mes/manim/scene_mes.py
git commit -m "feat: MES animation Acts 4-5, completion phase and finale"
```

---

## Task 5: Production Render

**Files:**
- No new source files — render only

**Interfaces:**
- Consumes: `pb_mes/manim/scene_mes.py` (complete from Task 4)
- Produces: `pb_mes/manim/media/videos/scene_mes/1080p60/MESScene.mp4`

- [ ] **Step 1: Render at production quality**

```bash
manim -pqh pb_mes/manim/scene_mes.py MESScene
```

This renders at 1080p60. Expect 5–15 minutes depending on your machine. The `-p` flag opens the video in your default player when done.

Expected: video plays cleanly at full quality, ~65 seconds total. Verify:
- All text is sharp and readable
- Coin travel is smooth (no stuttering)
- Cost bars fill smoothly
- No visual artifacts on `always_redraw` elements (coin stacks, cost bars)

- [ ] **Step 2: Commit the scene source (media is gitignored)**

```bash
git add pb_mes/manim/scene_mes.py
git commit -m "feat: MES Manim animation — production render complete"
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Covered by |
|---|---|
| Voters left, projects right, coin stacks below voters | Task 2 `_build_objects()` + `_act1_setup()` |
| Dotted approval lines, always visible | Task 2 `_build_objects()` |
| ρ values appear above each project, winner in gold | Tasks 3 (`_act2_round1`, `_act3_round2`) |
| Coins travel along approval paths | Task 3 `_send_coins()` |
| Cost bar fills incrementally | `make_cost_bar()` ValueTracker + tasks 3–4 |
| Voter balance shrinks as coins leave | `make_voter_node()` ValueTracker + `_send_coins()` |
| v3 stack empties dramatically in Round 2 | Task 3 `_act3_round2()` — sends all 11.67 |
| Round 3: both projects marked infeasible | Task 4 `_act4_mes_stops()` |
| Remaining budget pool materializes | Task 4 |
| Completion phase: p4 funded from pool | Task 5 `_act5_completion()` |
| p3 fades to indicate not funded | Task 4 |
| Finale: p1,p2,p4 glow, result text | Task 4 |
| ~65 seconds total | All acts combined |
| Color palette matches Beamer | `PALETTE` in `styles.py` |
| Corrected algorithm (Round 2 = p2, not p4) | Hardcoded in task briefings and `_act3_round2()` |
| Module path `pb_mes/manim/` | All file paths in plan |
| Gitignored media output | Task 1 Step 3 |

**No placeholders found.**

**Type consistency:** `make_voter_node` returns `tuple[VGroup, ValueTracker]`; `make_cost_bar` returns `tuple[VGroup, ValueTracker]`. Both are used consistently in `_build_objects()` and `_send_coins()`. `make_coin()` returns `Circle` — used in `_send_coins()` and `_act4_mes_stops()`.
