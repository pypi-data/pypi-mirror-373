import os
import functools
import warnings

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib.figure import Figure
from matplotlib.axes import Axes as Axes_plt
from matplotlib.ticker import ScalarFormatter

from .utils.default_kwargs import merge_kwargs
from ..time import TIME_STR, get_time_str
from ..files import MAIN_FILE_DIR, open_file, mkdirs
from ..pure_python.dicts import DL_to_LD


# TODO: change Ax.axs to be 1D (top->down, left->right), enable custom shapes (large, small axes)


class _Axes:
    def __init__(self,
            shape: tuple = (1, 1),
            grid_layout: list[list[tuple]] = None,
            sharex: (bool, str) = False, sharey: (bool, str) = False,
            projection: str = None,
            layout: str = None,
            fig: Figure = None, axs: (Axes_plt, list[Axes_plt]) = None,
            subplot_kw: dict = None, gridspec_kw: dict = None, **fig_kw):
        """
        Create a new figure with (possibly) subplots using the plt.subplots() function.

        Parameters
        ----------
        shape :             tuple (int, int), default: (1, 1)
                            number of rows, columns (in case of subplots).

        layout :            list[list[tuple]], optional
                            ([<row_start>, <row_end>], [<col_start>, <col_end>]),
                            e.g., [[(0, 2), (0, 2)], [(0, 1), (2, 4)]]

        sharex, sharey :    bool or {'none', 'all', 'row', 'col'}, default: False
                            Share the x or y `~matplotlib.axis` with sharex and/or sharey.
                            The axis will have the same limits, ticks, and scale as the axis
                            of the shared axes.

        projection :        {None, 'aitoff', 'hammer', 'lambert', 'mollweide', 'polar', 'rectilinear', str}, default: None
                            The projection type of the subplot (`~.axes.Axes`). *str* is the
                            name of a custom projection, see `~matplotlib.projections`. The
                            default None results in a 'rectilinear' projection.

        layout :            {'constrained', 'compressed', 'tight', 'none', `.LayoutEngine`, None}, default: None
                            The layout mechanism for positioning of plot elements to avoid
                            overlapping Axes decorations (labels, ticks, etc). Note that layout
                            managers can measurably slow down figure display.

                            - 'constrained': The constrained layout solver adjusts axes sizes
                              to avoid overlapping axes decorations.  Can handle complex plot
                              layouts and colorbars, and is thus recommended.

                              See :ref:`constrainedlayout_guide`
                              for examples.

                            - 'compressed': uses the same algorithm as 'constrained', but
                              removes extra space between fixed-aspect-ratio Axes.  Best for
                              simple grids of axes.

                            - 'tight': Use the tight layout mechanism. This is a relatively
                              simple algorithm that adjusts the subplot parameters so that
                              decorations do not overlap. See `.Figure.set_tight_layout` for
                              further details.

                            - 'none': Do not use a layout engine.

                            - A `.LayoutEngine` instance. Builtin layout classes are
                              `.ConstrainedLayoutEngine` and `.TightLayoutEngine`, more easily
                              accessible by 'constrained' and 'tight'.  Passing an instance
                              allows third parties to provide their own layout engine.

                            If not given, fall back to using the parameters *tight_layout* and
                            *constrained_layout*, including their config defaults
                            :rc:`figure.autolayout` and :rc:`figure.constrained_layout.use`.

        fig :               Figure, optional
                            Usually None, or send an existing figure

        axs :               Axes, optional
                            Usually None, or send own axis/axes

        Other Parameters
        ----------------
        subplot_kw :        dict, optional
                            Not interesting

        gridspec_kw :       dict, optional
                            left, right, top, bottom : float, optional
                                Extent of the subplots as a fraction of figure width or height.
                                Left cannot be larger than right, and bottom cannot be larger than
                                top. If not given, the values will be inferred from a figure or
                                rcParams at draw time. See also `GridSpec.get_subplot_params`.

                            wspace : float, optional
                                The amount of width reserved for space between subplots,
                                expressed as a fraction of the average axis width.
                                If not given, the values will be inferred from a figure or
                                rcParams when necessary. See also `GridSpec.get_subplot_params`.

                            hspace : float, optional
                                The amount of height reserved for space between subplots,
                                expressed as a fraction of the average axis height.
                                If not given, the values will be inferred from a figure or
                                rcParams when necessary. See also `GridSpec.get_subplot_params`.

                            width_ratios : array-like of length *ncols*, optional
                                Defines the relative widths of the columns. Each column gets a
                                relative width of ``width_ratios[i] / sum(width_ratios)``.
                                If not given, all columns will have the same width.

                            height_ratios : array-like of length *nrows*, optional
                                Defines the relative heights of the rows. Each row gets a
                                relative height of ``height_ratios[i] / sum(height_ratios)``.
                                If not given, all rows will have the same height.

        fig_kw :            dict, optional
                            num : int or str or `.Figure` or `.SubFigure`, optional
                                A unique identifier for the figure.

                                If a figure with that identifier already exists, this figure is made
                                active and returned. An integer refers to the ``Figure.number``
                                attribute, a string refers to the figure label.

                                If there is no figure with the identifier or *num* is not given, a new
                                figure is created, made active and returned.  If *num* is an int, it
                                will be used for the ``Figure.number`` attribute, otherwise, an
                                auto-generated integer value is used (starting at 1 and incremented
                                for each new figure). If *num* is a string, the figure label and the
                                window title is set to this value.  If num is a ``SubFigure``, its
                                parent ``Figure`` is activated.

                            figsize : (float, float), default: :rc:`figure.figsize`
                                Width, height in inches.

                            dpi : float, default: :rc:`figure.dpi`
                                The resolution of the figure in dots-per-inch.

                            facecolor : color, default: :rc:`figure.facecolor`
                                The background color.

                            edgecolor : color, default: :rc:`figure.edgecolor`
                                The border color.

                            frameon : bool, default: True
                                If False, suppress drawing the figure frame.

                            FigureClass : subclass of `~matplotlib.figure.Figure`
                                If set, an instance of this subclass will be created, rather than a
                                plain `.Figure`.

                            clear : bool, default: False
                                If True and the figure already exists, then it is cleared.

                            **kwargs
                                Additional keyword arguments are passed to the `.Figure` constructor.


        Examples
        --------
            >> from plotting import plot
            >> Ax = AxesLiron([2, 3])
            >> t = np.linspace(0, 10, 1001)
            >> plot(Ax.axs[0,0], t, np.sin(t))
            >> plot(Ax.axs[1,0], t, np.cos(t))
            >> plot(Ax.axs[0,1], t, np.log(t))
            >> plot(Ax.axs[1,1], t, np.exp(t))
            >> plot(Ax.axs[0,2], t, np.sqrt(t))
            >> plot(Ax.axs[1,2], t, np.square(t))

            >> Ax.set_props(sup_title="abc", ax_title=[1, 2, 3, 4, 5, 6], grid=[True, True, False, True, False, True], show_fig=True)

        """

        self.fig = fig
        self.axs = np.atleast_2d(axs)

        if fig is None and axs is None:
            if subplot_kw is None:
                subplot_kw = dict()
            subplot_kw = {"projection": projection} | subplot_kw
            fig_kw = {"layout": layout} | fig_kw
            fig_kw = merge_kwargs(fig_kw=fig_kw)["fig_kw"]
            padding = [None] * 4
            for i, key in enumerate(["w_pad", "h_pad", "wspace", "hspace"]):
                if key in fig_kw:
                    padding[i] = fig_kw.pop(key)

            nrows, ncols = shape

            if grid_layout is None:
                self.fig, self.axs = plt.subplots(nrows=nrows, ncols=ncols,
                        sharex=sharex, sharey=sharey,
                        squeeze=False,
                        subplot_kw=subplot_kw, gridspec_kw=gridspec_kw, **fig_kw)
            else:
                if gridspec_kw is None:
                    gridspec_kw = dict()
                if sharex == "all":
                    sharex = True
                elif sharex == "none":
                    sharex = False
                if sharey == "all":
                    sharey = True
                elif sharey == "none":
                    sharey = False
                assert type(sharex) is bool and type(sharey) is bool, "'sharex' and 'sharey' must be bool."

                self.fig = plt.figure(**fig_kw)
                gs = self.fig.add_gridspec(nrows=nrows, ncols=ncols, **gridspec_kw)

                ax_share = None
                axs = np.ones(shape=shape, dtype=Axes_plt)
                for i, (row_range, col_range) in enumerate(grid_layout):
                    if isinstance(row_range, int):
                        row_range = (row_range, row_range + 1)
                    if isinstance(col_range, int):
                        col_range = (col_range, col_range + 1)
                    r0, r1 = row_range
                    c0, c1 = col_range

                    axs[r0:r1, c0:c1] = 0
                    axs[r0, c0] = self.fig.add_subplot(gs[r0:r1, c0:c1],
                            sharex=ax_share if sharex else None,
                            sharey=ax_share if sharey else None,
                            **subplot_kw
                    )

                    if ax_share is None:
                        ax_share = axs[r0, c0]

                for (r, c) in np.argwhere(axs == 1):
                    axs[r, c] = self.fig.add_subplot(gs[r, c],
                            sharex=ax_share if sharex else None,
                            sharey=ax_share if sharey else None,
                            **subplot_kw
                    )

                self.axs = axs

            from matplotlib.layout_engine import ConstrainedLayoutEngine
            if type(self.fig.get_layout_engine()) is ConstrainedLayoutEngine:
                self.fig.get_layout_engine().set(w_pad=padding[0], h_pad=padding[1], hspace=padding[2],
                        wspace=padding[3])

        elif fig is not None:
            self.axs = np.atleast_2d(self.fig.axes)

        elif axs is not None:
            self.fig = self.axs[0, 0].figure

        self.func_animation = None

    @staticmethod
    def _vectorize(cls, ax: Axes_plt = None, **vec_params):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if ax is not None:
                    return func(ax, *args, **vec_params, **kwargs)

                # Vectorize the function
                m, n = cls.axs.shape

                params_list = DL_to_LD(vec_params)
                if params_list is None or len(params_list) != m * n:
                    params_list = np.repeat(vec_params, m * n)

                out = np.empty((m, n), dtype=object)

                for i in range(m):
                    for j in range(n):
                        out[i, j] = func(cls.axs[i, j], *args, **params_list[j * m + i], **kwargs)

                return out

            return wrapper

        return decorator

    @staticmethod
    def _merge_kwargs(key, **kwargs):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args):
                kwargs_merged = merge_kwargs(**{key: kwargs})[key]

                return func(*args, **kwargs_merged)

            return wrapper

        return decorator

    def draw_xy_lines(self, **xy_lines_kw):
        @self._merge_kwargs("xy_lines_kw", **xy_lines_kw)
        @self._vectorize(cls=self)
        def _draw_xy_lines(ax: Axes_plt, **xy_lines_kw):
            """
            Draw x-y axes lines to look bolder than the rest of the grid lines

            Args:
                ax:
                **axis_lines_kw:

            Returns:

            """

            if hasattr(ax, "axis_lines_drawn") or hasattr(ax, 'zaxis') or len(
                    ax.images) > 0:  # Don't draw axis lines for 3D plots and images
                return

            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            ax.axhline(**xy_lines_kw)
            ax.axvline(**xy_lines_kw)

            ax.set_xlim(*xlim, auto=True)
            ax.set_ylim(*ylim, auto=True)

            ax.axis_lines_drawn = True

        _draw_xy_lines()

    def sup_title(self, title: str):
        self.fig.suptitle(title, color=plt.rcParams[
            "axes.titlecolor"])  # for unknown reason, color is not automatically inherited from axes.titlecolor

    def ax_axis(self, axis: (bool, str)):
        """

            Parameters
            ----------
            ax :
            axis :  ================ ===========================================================
                    Value            Description
                    ================ ===========================================================
                    'off' or `False` Hide all axis decorations, i.e. axis labels, spines,
                                     tick marks, tick labels, and grid lines.
                                     This is the same as `~.Axes.set_axis_off()`.
                    'on' or `True`   Do not hide all axis decorations, i.e. axis labels, spines,
                                     tick marks, tick labels, and grid lines.
                                     This is the same as `~.Axes.set_axis_on()`.
                    'equal'          Set equal scaling (i.e., make circles circular) by
                                     changing the axis limits. This is the same as
                                     ``ax.set_aspect('equal', adjustable='datalim')``.
                                     Explicit data limits may not be respected in this case.
                    'scaled'         Set equal scaling (i.e., make circles circular) by
                                     changing dimensions of the plot box. This is the same as
                                     ``ax.set_aspect('equal', adjustable='box', anchor='C')``.
                                     Additionally, further autoscaling will be disabled.
                    'tight'          Set limits just large enough to show all data, then
                                     disable further autoscaling.
                    'auto'           Automatic scaling (fill plot box with data).
                    'image'          'scaled' with axis limits equal to data limits.
                    'square'         Square plot; similar to 'scaled', but initially forcing
                                     ``xmax-xmin == ymax-ymin``.
                    ================ ===========================================================

            Returns
            -------

            """

        @self._vectorize(cls=self, axis=axis)
        def _ax_axis(ax: Axes_plt, axis: (bool, str)):
            ax.axis(axis)

        _ax_axis()

    def ax_spines(self, spines: bool):
        """
        Show axis spines (boundaries)

        Parameters
        ----------
        spines :        bool

        """

        @self._vectorize(cls=self, spines=spines)
        def _ax_spines(ax: Axes_plt, spines: (str, list, bool)):
            locs = np.array(["left", "bottom", "top", "right"])

            if type(spines) is str:
                spines = [spines]

            if type(spines) is list:
                locs = np.array(spines)
                idx = [True] * locs.size
            elif type(spines) is bool:
                idx = [False] * locs.size
                if spines:
                    idx = [True] * locs.size
            else:
                raise ValueError("'spines' must be one of (str, list, bool).")

            if locs[idx].size > 0:
                ax.spines[locs[idx].tolist()].set_visible(True)
            if locs[np.logical_not(idx)].size > 0:
                ax.spines[locs[np.logical_not(idx)].tolist()].set_visible(False)

        _ax_spines()

    def ax_ticks(self, ticks: (bool, list[list], dict, list[dict]), labels: (bool, list[list])):
        @self._vectorize(cls=self, ticks=ticks, labels=labels)
        def _ax_ticks(ax: Axes_plt, ticks: (bool, list[list], dict, list[dict]), labels: (bool, list[list])):
            # todo: if labels is False
            if len(ax.get_shared_x_axes().get_siblings(ax)) > 1 or len(ax.get_shared_y_axes().get_siblings(ax)) > 1:
                warnings.warn(
                        f"Axis shares x or y axis with siblings. Changing ticks would affect all siblings.")  # todo: fix in future

            ndim = 3 if hasattr(ax, "get_zticks") else 2

            if ticks is None or ticks is True:  # show ticks for all axes
                ticks = [True] * ndim
                if labels is None:  # show labels for all axes
                    labels = [True] * ndim
            elif ticks is False:  # hide ticks for all axes
                ticks = [False] * ndim
                if labels is None:  # hide labels for all axes
                    labels = [False] * ndim
            elif type(ticks) is dict:  # only x-axis
                ticks = [ticks] + [True] * (ndim - 1)
            # labels check is done later

            if labels is True:  # show labels for all axes
                labels = [True] * ndim
            elif labels is False:  # hide labels for all axes
                labels = [False] * ndim
            elif labels is None:
                labels = [None] * ndim

            # ticks = np.atleast_1d(ticks)
            # labels = np.atleast_1d(labels)
            assert len(ticks) <= ndim, "len(ticks) must be <= graph dimensionality."
            assert len(labels) <= ndim, "len(labels) must be <= graph dimensionality."

            d = {
                "ticks":  {
                    0: ax.get_xticks(),
                    1: ax.get_yticks(),
                    2: ax.get_zticks() if ndim == 3 else [],
                },

                "labels": {
                    0: ax.get_xticklabels(),
                    1: ax.get_yticklabels(),
                    2: ax.get_zticklabels() if ndim == 3 else [],
                },
                # "offset": {
                # 	0: ax.xaxis.get_offset_text(),
                # 	1: ax.yaxis.get_offset_text(),
                # 	2: ax.zaxis.get_offset_text() if ndim == 3 else [],
                # },
            }

            funcs = [ax.get_xlim, ax.get_ylim]
            if ndim == 3:
                funcs += [ax.get_zlim]

            for i, func in enumerate(funcs):
                lim = func()
                idx = np.logical_and(min(lim) <= d["ticks"][i], d["ticks"][i] <= max(lim))
                if len(d["ticks"][i]) > 0:
                    d["ticks"][i] = d["ticks"][i][idx]
                if len(d["labels"][i]) > 0:
                    d["labels"][i] = np.array(d["labels"][i])[idx]

            for i in range(len(ticks)):  # x,y,z axes
                if ticks[i] is None or ticks[i] is True or ticks[i] is np.True_:  # show ticks
                    pass

                elif ticks[i] is False or ticks[i] is np.False_:  # hide ticks
                    d["ticks"][i] = []
                    if labels[i] is None:  # hide labels
                        d["labels"][i] = []
                # d["offset"][i] = None

                elif type(ticks[i]) is dict:  # custom ticks
                    assert labels[i] is None or labels[
                        i] is np.True_, "When 'ticks' is a dict, 'labels' must not be given."
                    d["ticks"][i] = ticks[i].keys()
                    d["labels"][i] = ticks[i].values()

                elif type(ticks[i]) is list or type(ticks[i]) is np.ndarray:  # custom ticks
                    d["ticks"][i] = ticks[i]
                    d["labels"][i] = ticks[i]
                # d["offset"][i] = None  # todo: check

                else:
                    raise ValueError("'ticks' must be given either as a boolean, list[list] or list[dict].")

                if labels[i] is None or labels[i] is True or labels[i] is np.True_:  # show labels
                    pass

                elif labels[i] is False or labels[i] is np.False_:  # hide labels
                    d["labels"][i] = []
                # d["offset"][i] = None

                elif type(labels[i]) is list or type(labels[i]) is np.ndarray:  # custom labels
                    assert len(labels[i]) == len(ticks[i]), "len(labels[i]) must be equal to len(ticks[i])."
                    d["labels"][i] = labels[i]
                # d["offset"][i] = None  # todo: check

                else:
                    raise ValueError("'labels' must be given either as a boolean or list[list].")

            # Set ticks and labels
            ax.set_xticks(d["ticks"][0], d["labels"][0])
            ax.xaxis.set_major_formatter(
                    ScalarFormatter(useOffset=True))  # todo: returns the tick labels for unknown reason

            ax.set_yticks(d["ticks"][1], d["labels"][1])
            ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=True))

            if ndim == 3:
                ax.set_zticks(d["ticks"][2], d["labels"][2])
                ax.zaxis.set_major_formatter(ScalarFormatter(useOffset=True))

        _ax_ticks()

    def ax_title(self, title: str):
        @self._vectorize(cls=self, title=title)
        def _ax_title(ax: Axes_plt, title: str):
            ax.set_title(title)

        _ax_title()

    def ax_labels(self, labels: list[str]):
        @self._vectorize(cls=self, labels=labels)
        def _ax_labels(ax: Axes_plt, labels: list[str]):
            labels = np.atleast_1d(labels)  # In case labels=None or labels is just 1 list (only xlabel)
            ax.set_xlabel(labels[0])
            if np.size(labels) >= 2:
                ax.set_ylabel(labels[1])
            if np.size(labels) >= 3:
                ax.set_zlabel(labels[2])

        _ax_labels()

    def ax_limits(self, limits: list[float]):
        @self._vectorize(cls=self, limits=limits)
        def _ax_limits(ax: Axes_plt, limits: list[float]):
            limits = np.array(limits, dtype=object)
            limits = np.atleast_2d(limits)  # In case limits=None or limits is just 1 list (only xlim)

            ax.set_xlim(limits[0])
            if len(limits) >= 2:
                ax.set_ylim(limits[1])
            if len(limits) >= 3:
                ax.set_zlim(limits[2])

        _ax_limits()

    def ax_view(self, view: list):
        @self._vectorize(cls=self, view=view)
        def _ax_view(ax: Axes_plt, view: list):
            ax.view_init(view[0], view[1])

        _ax_view()

    def ax_grid(self, grid: bool):
        @self._vectorize(cls=self, grid=grid)
        def _ax_grid(ax: Axes_plt, grid: bool):
            ax.grid(grid)

        _ax_grid()

    def ax_legend(self, legend: (bool, list), legend_loc: str):
        @self._vectorize(cls=self, legend=legend, legend_loc=legend_loc)
        def _ax_legend(ax: Axes_plt, legend: (bool, list), legend_loc: str):
            if legend is False:
                legend = ax.get_legend()
                if legend is not None:
                    legend.remove()

            elif legend is True:
                handles, labels = ax.get_legend_handles_labels()
                if len(handles) > 0:
                    ax.legend(handles, labels, loc=legend_loc)  # todo [::-1] ?

            else:
                ax.legend(legend, loc=legend_loc)

        _ax_legend()

    def ax_colorbar(self, axs: (bool, list[list[Axes_plt], Axes_plt]), **colorbar_kw):
        if axs is False:
            return
        elif axs is True:
            axs = [[ax] for ax in self.fig.axes if len(ax.images) > 0]
        elif type(axs) is Axes_plt:
            axs = [axs]
        elif type(axs) is np.ndarray:
            axs = axs.tolist()

        # convert to a list of lists
        for i in range(len(axs)):  # run through common axes
            if type(axs[i]) is Axes_plt:  # if not a list, convert to a list
                axs[i] = [axs[i]]

            assert type(axs[i]) is list, "'axs' must be a list of lists."
            for j in range(len(axs[i])):
                assert len(axs[i][j].images) > 0, "At least one of the axes provided doesn't have an image plotted."

        # draw colorbar
        for ax_common in axs:
            mappable = ax_common[0].images[0]
            self.fig.colorbar(mappable=mappable, ax=ax_common, **colorbar_kw)

    def ax_face_color(self, face_color):
        @self._vectorize(cls=self, face_color=face_color)
        def _ax_face_color(ax, face_color):
            ax.set_facecolor(face_color)

        _ax_face_color()

    def save_fig(self, file_name: str = None, **savefig_kw):
        """
        Save figure as file

        Args:
            file_name:              File name
            **savefig_kw:           kwargs for function fig.savefig

        Returns:

        """

        file_name = get_savefig_file_name(file_name, mkdir=True)

        format = os.path.splitext(file_name)[-1]

        if format == ".gif":
            assert self.func_animation is not None, "Call plot_animation() before saving gif."
            self.func_animation.save(file_name, **savefig_kw)
        else:
            self.fig.savefig(file_name, **savefig_kw)

        return file_name

    def show_fig(self):
        self.fig.show()

    def show(self):
        self.show_fig()

    def set_props(self,
            save_file_name: (str, bool) = False,
            colorbar_kw: dict = None,
            xy_lines_kw: dict = None,
            save_fig_kw: dict = None,
            **set_props_kw):
        """
        Set figure properties after plotting.

        Parameters
        ----------
        save_file_name :    str/bool
                            The file name to be saved.
                            False - don't save, True - save to MAIN_FILE_DIR, str - specify location

        save_fig_kw :       dict, optional
                            Sent to fig.savefig()

        colorbar_kw :       dict, optional
                            Sent to fig.colorbar()

        xy_lines_kw :       dict, optional
                            Sent to ax.axhline()


        Other Parameters
        ----------------
        For the following parameters, a '*' symbol means that it can be vectorized
        to all axes by being sent as a list.

        sup_title :         str, default: None
                            supreme figure title

        *ax_title :         str, default: None
                            axis title

        *axis :             str/bool, default: None

        *spines :           bool/list/str, default: None
                            show axis boundaries.
                            'True' will plot all boundaries.
                            Can be specified as one (or a list) of the strings ["left", "bottom", "top", "right"]

        *ticks :            bool/list, default: None
                            axis ticks
                            'False' will remove all ticks and tick labels.
                            A list will set the ticks for the x,y,z axes

        *tick_labels :     bool/list, default: None
                            axis tick labels
                            'False' will remove all tick labels.
                            A list will set the tick labels for the x,y,z axes

        *labels :           list[str], default: None
                            axis labels for the x,y,z axes

        *limits :           list[float], default: None
                            axis limits for the x,y,z axes, given as a 2-tuple,
                            e.g., limits=[[0,2], [-1,1]] will set xlim=[0,2],ylim=[-1,1]

        *view :             list[float], default: None
                            axis view in case of a 3D plot, given as a 2-tuple.

        *grid :             bool, default: None
                            Show grid.
                            'None' will toggle the grid on and off

        *legend :           bool/list[str], default: True
                            Show legend.
                            A list of strings would set the legend labels

        *legend_loc :       str, default: None
                            The location of the legend:
                            - 'upper left', 'upper right', 'lower left', 'lower right' place the legend at the
                              corresponding corner of the axes.
                            - 'upper center', 'lower center', 'center left', 'center right' place the legend
                              at the center of the corresponding edge of the axes.
                            - 'center' places the legend at the center of the axes.
                            - 'best' places the legend at the location, among the nine locations defined so far, with
                              the minimum overlap with other drawn artists.
                              This option can be quite slow for plots with
                              large amounts of data; your plotting speed may benefit from providing a specific location.
                            The location can also be a 2-tuple giving the coordinates of the lower-left corner of the
                            legend in axes coordinates (in which case bbox_to_anchor will be ignored).

        colorbar :          bool/list[list[Axes], Axes], default: False
                            A boolean decides whether to add a colorbar to each axis containing an image.
                            Otherwise, provide a list of the desired axes.
                            A list inside the list would create a common colorbar.

        *xy_lines :         bool, default: True
                            Draw x-y axis lines (the lines x=0 and y=0).

        *face_color :       color, default: None
                            axes face color

        show_fig :          bool, default: True
                            Show figure at the end of the function run

        open_dir :          bool, default: False
                            If file saved, open directory afterward.

        Returns
        -------

        """

        if colorbar_kw is None:
            colorbar_kw = dict()
        if xy_lines_kw is None:
            xy_lines_kw = dict()
        if save_fig_kw is None:
            save_fig_kw = dict()

        set_props_kw = merge_kwargs(set_props_kw=set_props_kw)["set_props_kw"]

        def caller(func, *args, **kwargs):
            if args[0] is None:
                return None
            return func(*args, **kwargs)

        # Supreme Title
        caller(self.sup_title, set_props_kw["sup_title"])

        # Axes Title
        caller(self.ax_title, set_props_kw["ax_title"])

        # Axis
        caller(self.ax_axis, set_props_kw["axis"])

        # Axis Spines
        caller(self.ax_spines, set_props_kw["spines"])

        # Axis Labels
        caller(self.ax_labels, set_props_kw["labels"])

        # View (in case of 3D)
        caller(self.ax_view, set_props_kw["view"])

        # Grid
        caller(self.ax_grid, set_props_kw["grid"])

        # Legend
        self.ax_legend(set_props_kw["legend"], set_props_kw["legend_loc"])

        # Colorbar
        self.ax_colorbar(set_props_kw["colorbar"], **colorbar_kw)

        # Axis Limits
        caller(self.ax_limits, set_props_kw["limits"])

        # Axis Ticks
        caller(self.ax_ticks, set_props_kw["ticks"], set_props_kw["tick_labels"])

        # x-y Lines (through the origin)
        if set_props_kw["xy_lines"]:
            self.draw_xy_lines(**xy_lines_kw)

        # Face Color
        caller(self.ax_face_color, set_props_kw["face_color"])

        # -------------------------------------------------------

        # Save Figure
        file_name = None
        if save_file_name is not False:  # if user wants to save figure
            if save_file_name is True:  # default file name, otherwise provide a string
                save_file_name = None

            file_name = self.save_fig(file_name=save_file_name, **save_fig_kw)

        # Show Figure
        if set_props_kw["show_fig"]:
            self.show_fig()
            if set_props_kw["open_dir"]:
                open_file(os.path.split(file_name)[0])

        # Close Figure
        if set_props_kw["close_fig"]:
            plt.close(self.fig)

        return file_name


def new_figure(nrows=1, ncols=1,
        sharex=False, sharey=False,
        projection=None,
        squeeze=True,
        subplot_kw=None, gridspec_kw=None, **figure_kw) -> (Figure, Axes_plt):
    """
    Create new figure with (possibly) subplots

    Args:
        nrows:              number of rows (in case of subplots)
        ncols:              number of columns (in case of subplots)
        sharex:             Link x-axis (zoom together)
        sharey:             Link y-axis (zoom together)
        squeeze:            Extra dimensions are squeezed out
        projection:         ['3d', 'aitoff', 'hammer', 'lambert', 'mollweide', 'polar', 'rectilinear']
        subplot_kw:
        gridspec_kw:
        **figure_kw

    Returns:

    """

    if subplot_kw is None:
        subplot_kw = dict()
    subplot_kw = {'projection': projection} | subplot_kw

    fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
            sharex=sharex, sharey=sharey,
            squeeze=squeeze,
            subplot_kw=subplot_kw, gridspec_kw=gridspec_kw, **figure_kw)

    return fig, axs


# @copy_docstring_and_deprecators(_AxesLiron.draw_xy_lines)
def draw_xy_lines(ax: Axes_plt, **axis_lines_kw):
    _Axes(axs=ax).draw_xy_lines(**axis_lines_kw)


# @copy_docstring_and_deprecators(_AxesLiron.save_fig)
def save_fig(fig: Figure = None, file_name: str = None, **savefig_kw):
    """
    Save figure as file

    Args:
        fig:                    Figure to be saved
        file_name:              File name
        **savefig_kw:           kwargs for function fig.savefig

    Returns:

    """

    if fig is None:
        fig = plt.gcf()

    _Axes(fig=fig).save_fig(file_name, **savefig_kw)


# @copy_docstring_and_deprecators(_AxesLiron.set_props)
def set_props(ax: Axes_plt = None,
        save_file_name: (str, bool) = False, save_fig_kw: dict = None,
        **set_props_kw):
    if ax is None:
        ax = plt.gca()

    _Axes(axs=ax).set_props(save_file_name=save_file_name,
            save_fig_kw=save_fig_kw,
            **set_props_kw)


def get_savefig_file_name(file_name: str = None, time_dir: bool = False, mkdir: bool = False):
    """

    Parameters
    ----------
    file_name :     str, optional
                    If <file_name> doesn't contain a directory name, the default saving directory
                    will be "<CUR_DIR>/figs", where <CUR_DIR> is the current directory of the directory
                    of the Python file being called.
    time_dir :      bool, optional
                    If True, a time directory will be created in the default saving directory.

    Returns
    -------
    Full path of file to be saved.
    """

    if file_name is None or os.path.dirname(file_name) == "":
        dir_name = os.path.join(MAIN_FILE_DIR, "figs")
    else:
        dir_name = os.path.dirname(file_name)

    if time_dir:
        dir_name = os.path.join(dir_name, TIME_STR)

    if mkdir and not os.path.exists(dir_name):
        mkdirs(dir_name)

    if file_name is None:
        file_name = os.path.join(dir_name, f"fig {get_time_str()}")
    elif os.path.dirname(file_name) == "":
        file_name = os.path.join(dir_name, file_name)

    return file_name
