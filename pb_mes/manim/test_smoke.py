from manim import *
from styles import PALETTE, VOTERS_DATA, PROJECTS_DATA
from styles import make_voter_node, make_project_card, make_cost_bar

class SmokeTest(Scene):
    def construct(self):
        self.camera.background_color = PALETTE["bg"]
        voter, tracker = make_voter_node("v1", PALETTE["dark"])
        voter.move_to(LEFT * 3)
        self.add(voter)

        card = make_project_card("Park", 40, "Center", PALETTE["dark"])
        card.move_to(RIGHT * 2)
        self.add(card)

        bar, bar_tracker = make_cost_bar(40, PALETTE["dark"])
        bar.next_to(card, DOWN, buff=0.15)
        self.add(bar)

        self.play(bar_tracker.animate.set_value(40), run_time=1.5)
        self.play(tracker.animate.set_value(11.67), run_time=1.0)
        self.wait(0.5)
