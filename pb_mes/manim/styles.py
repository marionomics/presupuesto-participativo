from manim import *

PALETTE = {
    "dark":       "#1A1E1D",   # Marionomics charcoal
    "accent":     "#B4FF00",   # Marionomics neon lime
    "marginal":   "#4A7A6D",   # muted teal for Marginal district
    "infeasible": "#C0392B",   # red for errors/infeasible
    "neutral":    "#6B7280",   # mid-grey for labels
    "bg":         "#EDE9E3",   # Marionomics cream background
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
    {"id": "v1", "approves": {"p1", "p3"}, "color": PALETTE["dark"]},
    {"id": "v2", "approves": {"p1", "p3"}, "color": PALETTE["dark"]},
    {"id": "v3", "approves": {"p1", "p2"}, "color": PALETTE["dark"]},
    {"id": "v4", "approves": {"p2", "p4"}, "color": PALETTE["dark"]},
]

PROJECTS_DATA = [
    {"id": "p1", "name": "Park renovation", "cost": 40, "district": "Center",   "color": PALETTE["dark"]},
    {"id": "p2", "name": "School repair",   "cost": 30, "district": "Marginal", "color": PALETTE["marginal"]},
    {"id": "p3", "name": "Road paving",     "cost": 50, "district": "Center",   "color": PALETTE["dark"]},
    {"id": "p4", "name": "Water access",    "cost": 20, "district": "Marginal", "color": PALETTE["marginal"]},
]


def make_coin(color: str = PALETTE["accent"], radius: float = 0.09) -> Circle:
    return Circle(radius=radius, fill_color=color, fill_opacity=1.0,
                  stroke_color=PALETTE["dark"], stroke_width=0.5)


def make_voter_node(vid: str, color: str) -> tuple[VGroup, ValueTracker, Mobject]:
    """
    Returns (voter_dot, balance_tracker, coin_stack).
    voter_dot: VGroup(circle, label) — position this in the scene.
    balance_tracker: starts at 25.0; animate to shrink the coin stack.
    coin_stack: an always_redraw mobject that MUST be added to the scene separately
    (not as a child of voter_dot). It self-positions directly below voter_dot
    using voter_dot.get_center() each frame.
    Add both to the scene: self.add(voter_dot, coin_stack)
    """
    tracker = ValueTracker(25.0)

    circle = Circle(radius=0.35, fill_color=color, fill_opacity=0.9,
                    stroke_color=color, stroke_width=2)
    lbl = Text(vid, font_size=20, color=WHITE).move_to(circle)
    voter_dot = VGroup(circle, lbl)

    # Coin stack positioned relative to voter_dot using its get_center() each frame
    def build_stack():
        ratio = max(tracker.get_value() / 25.0, 0.0)
        n = max(int(round(ratio * 5)), 0)
        stack = VGroup(*[
            make_coin().shift(UP * i * 0.16)
            for i in range(n)
        ])
        base = voter_dot.get_center() + DOWN * 1.0
        stack.move_to(base + UP * (n - 1) * 0.08)  # stack grows upward from base
        bal = Text(f"{tracker.get_value():.1f}", font_size=13,
                   color=PALETTE["neutral"])
        if n > 0:
            bal.next_to(stack, DOWN, buff=0.08)
        else:
            bal.move_to(base + DOWN * 0.15)
        return VGroup(stack, bal)

    coin_stack = always_redraw(build_stack)
    return voter_dot, tracker, coin_stack


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
