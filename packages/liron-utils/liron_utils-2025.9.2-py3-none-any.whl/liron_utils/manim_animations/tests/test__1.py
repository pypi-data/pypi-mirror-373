from manim import *
import numpy as np


class BraceAnnotation(Scene):
    def construct(self):
        dot = Dot([-2, -1, 0])
        dot2 = Dot([2, 1, 0])
        line = Line(dot.get_center(), dot2.get_center()).set_color(ORANGE)
        b1 = Brace(line)
        b1text = b1.get_text("Horizontal distance")
        b2 = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
        b2text = b2.get_tex("x-x_1")
        self.add(line, dot, dot2, b1, b2, b1text, b2text)


class OpeningManim(Scene):
    def construct(self):
        title = Tex(r"This is some \LaTeX")
        basel = MathTex(r"\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}")
        VGroup(title, basel).arrange(DOWN)
        self.play(
            Write(title),
            FadeIn(basel, shift=DOWN),
        )
        self.wait()

        transform_title = Tex("That was a transform")
        transform_title.to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStart(*[FadeOut(obj, shift=DOWN) for obj in basel]),
        )
        self.wait()

        grid = NumberPlane()
        grid_title = Tex("This is a grid")
        grid_title.scale(1.5)
        grid_title.move_to(transform_title)

        self.add(grid, grid_title)  # Make sure title is on top of grid
        self.play(
            FadeOut(title),
            FadeIn(grid_title, shift=UP),
            Create(grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        grid_transform_title = Tex(
            r"That was a non-linear function \\ applied to the grid"
        )
        grid_transform_title.move_to(grid_title, UL)
        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.animate.apply_function(
                lambda p: p
                          + np.array(
                    [
                        np.sin(p[1]),
                        np.sin(p[0]),
                        0,
                    ]
                )
            ),
            run_time=3,
        )
        self.wait()
        self.play(Transform(grid_title, grid_transform_title))
        self.wait()

        self.renderer.file_writer.finish()


class MyTest(Scene):
    def construct(self):
        ax = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1],
                  axis_config={'include_ticks': True, 'numbers_to_exclude': [0]}).add_coordinates()
        ax_labels = ax.get_axis_labels("x", "y")
        graph = ax.plot(lambda x: np.sin(x), x_range=[-1, 4])
        graph_label = ax.get_graph_label(graph, x_val=4)

        ax_staff = VGroup(ax, ax_labels)
        graph_staff = VGroup(graph, graph_label)

        self.play(Create(ax_staff, run_time=3))
        self.wait(3)
        self.play(Create(graph_staff, run_time=3))
        self.wait()

        box = Rectangle(stroke_color=MAROON, fill_color=BLUE_C, fill_opacity=0.5)

        self.play(
            Create(box, run_time=3)
        )
        self.play(box.animate.shift(3 * UP))


class AddToVGroup(Scene):
    def construct(self):
        circle_red = Circle(color=RED)
        circle_green = Circle(color=GREEN)
        circle_blue = Circle(color=BLUE)
        circle_red.shift(LEFT)
        circle_blue.shift(RIGHT)
        gr = VGroup(circle_red, circle_green)
        gr2 = VGroup(circle_blue)  # Constructor uses add directly
        self.add(gr, gr2)
        self.wait()
        gr += gr2  # Add group to another
        self.play(
            gr.animate.shift(DOWN),
        )
        gr -= gr2  # Remove group
        self.play(  # Animate groups separately
            gr.animate.shift(LEFT),
            gr2.animate.shift(UP),
        )
        self.play(  # Animate groups without modification
            (gr + gr2).animate.shift(RIGHT)
        )
        self.play(  # Animate group without component
            (gr - circle_red).animate.shift(RIGHT)
        )


if __name__ == "__main__":
    h = OpeningManim()
    h.construct()
    h.renderer.file_writer.finish()
    pass
