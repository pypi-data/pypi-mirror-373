from __future__ import annotations

from manim import *
import numpy as np
import scipy.special


class PlotFunction(Scene):
    def construct(self):
        c_grid = ComplexPlane()
        moving_c_grid = ComplexPlane(
            faded_line_style={
                "stroke_color":   GREY,
                "stroke_width":   1,
                "stroke_opacity": .25,
            },
            faded_line_ratio=5
        )

        # c_grid.set_stroke(BLUE_E, 1)
        c_grid.add_coordinates()

        moving_c_grid.prepare_for_nonlinear_transform()

        self.play(
            Create(c_grid, run_time=2, lag_ratio=0.1)
        )
        self.wait(0.5)

        func_text = Tex(r"$f(z)$").to_corner(UP + LEFT)

        self.play(
            FadeIn(moving_c_grid),
            FadeIn(func_text, shift=UP),
        )
        self.wait(1.5)

        self.play(
            moving_c_grid.animate.apply_complex_function(func),
            run_time=6,
        )
        self.wait(4)


if __name__ == "__main__":
    func = lambda z: 2*z

    h = PlotFunction()
    h.construct()
    h.renderer.file_writer.finish()
    pass
