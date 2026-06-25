from manim import *
from styles import (
    PALETTE, VOTERS_DATA, PROJECTS_DATA,
    VOTER_X, PROJECT_X, VOTER_YS, PROJECT_YS,
    STACK_Y_OFFSET, COST_BAR_Y_OFFSET,
    make_voter_node, make_project_card, make_cost_bar,
    make_coin,  # used by _send_coins (Task 3)
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

        # Voters: circle+label VGroup, balance tracker, and coin stack
        self.voter_nodes = []     # list of VGroup (voter_dot, positioned)
        self.voter_trackers = []  # list of ValueTracker
        self.voter_stacks = []    # list of always_redraw coin stack Mobjects

        for i, vd in enumerate(VOTERS_DATA):
            voter_dot, tracker, coin_stack = make_voter_node(vd["id"], vd["color"])
            voter_dot.move_to([VOTER_X, VOTER_YS[i], 0])
            self.voter_nodes.append(voter_dot)
            self.voter_trackers.append(tracker)
            self.voter_stacks.append(coin_stack)

        # Add coin stacks to scene now so they are available in all acts.
        # They are always_redraw mobjects; they self-position using voter_dot.get_center()
        # each frame, so they don't need a separate move_to().
        for stack in self.voter_stacks:
            self.add(stack)
            stack.set_opacity(0)  # hidden until _act1_setup reveals them

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
        self.round_label = Text("", font_size=24, color=PALETTE["dark"])
        self.round_label.to_edge(UP, buff=0.3)

    # ── Act 1: Setup ───────────────────────────────────────────────────

    def _act1_setup(self):
        # Title
        title = Text("Method of Equal Shares", font_size=34,
                     color=PALETTE["dark"]).to_edge(UP, buff=0.25)
        eq = MathTex(r"B = 100,\quad n = 4,\quad b_i = 25",
                     font_size=22, color=PALETTE["neutral"])
        eq.next_to(title, DOWN, buff=0.15)

        self.play(Write(title))
        self.play(FadeIn(eq, shift=UP * 0.2))
        self.wait(1)

        # Voters materialize
        self.play(LaggedStart(
            *[FadeIn(node, scale=0.7) for node in self.voter_nodes],
            lag_ratio=0.2,
        ))
        # Coin stacks fade in (already on scene with opacity=0)
        self.play(LaggedStart(
            *[FadeIn(stack, shift=UP * 0.3) for stack in self.voter_stacks],
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
            if lines:
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
