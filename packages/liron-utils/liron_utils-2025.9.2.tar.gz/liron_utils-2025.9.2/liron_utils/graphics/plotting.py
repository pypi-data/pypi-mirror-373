import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
import matplotlib.collections
import matplotlib.colors
import matplotlib.animation
from matplotlib.figure import Figure
from matplotlib.axes import Axes as Axes_plt

from .axes import _Axes
from ..uncertainties_math import to_numpy
from ..signal_processing.base import interp1


# TODO:
#   - add option to call gr.Axes.plot(ax, x, y) with ax=plt.Axes (add decorator to outer plotting functions),
#     and change class name to be Plot
#   - add standalone functions out of class gr.plot
#   - PyWavelet.dwt (wavelet transform) and plot_wavelet


class Axes(_Axes):
    def __init__(self,
            shape: tuple = (1, 1),
            grid_layout: list[list[tuple]] = None,
            sharex: (bool, str) = False, sharey: (bool, str) = False,
            projection: str = None,
            layout: str = None,
            fig: Figure = None, axs: (Axes_plt, list[Axes_plt]) = None,
            subplot_kw: dict = None, gridspec_kw: dict = None, **fig_kw):
        super().__init__(shape=shape, grid_layout=grid_layout, sharex=sharex, sharey=sharey, projection=projection,
                layout=layout, fig=fig, axs=axs, subplot_kw=subplot_kw, gridspec_kw=gridspec_kw, **fig_kw)

    def plot(self,
            x, y=None, z=None,
            **plot_kw):

        @self._merge_kwargs("plot_kw", **plot_kw)
        @self._vectorize(cls=self, x=x, y=y, z=z)
        def _plot(ax: Axes_plt,
                x, y=None, z=None,
                **plot_kw):
            """
            2D plot of y=f(x)

            Args:
                ax:
                x:
                y:
                z:
                **plot_kw:

            Returns:

            """

            args = [x]
            if y is not None:
                args += [y]
            if z is not None:
                args += [z]

            ax.plot(*args, **plot_kw)

        return _plot()

    def plot_vlines(self,
            x=0, ymin=0, ymax=1,
            **plot_kw):

        @self._merge_kwargs("plot_kw", **plot_kw)
        @self._vectorize(cls=self, x=x, ymin=ymin, ymax=ymax)
        def _plot_vlines(ax: Axes_plt,
                x=0, ymin=0, ymax=1,
                **plot_kw):
            x = np.atleast_1d(x)

            label = None
            if "label" in plot_kw:
                label = plot_kw.pop("label")

            for i, xx in enumerate(x):
                ax.axvline(x=xx, ymin=ymin, ymax=ymax,
                        label=label if i == x.shape[0] - 1 else "_nolabel_",
                        **plot_kw)

        return _plot_vlines()

    def plot_hlines(self,
            y=0, xmin=0, xmax=1,
            **plot_kw):

        @self._merge_kwargs("plot_kw", **plot_kw)
        @self._vectorize(cls=self, y=y, xmin=xmin, xmax=xmax)
        def _plot_hlines(ax: Axes_plt,
                y=0, xmin=0, xmax=1,
                **plot_kw):
            y = np.atleast_1d(y)

            label = None
            if "label" in plot_kw:
                label = plot_kw.pop("label")

            for i, yy in enumerate(y):
                ax.axhline(y=yy, xmin=xmin, xmax=xmax,
                        label=label if i == y.shape[0] - 1 else "_nolabel_",
                        **plot_kw)

        return _plot_hlines()

    def plot_errorbar(self,
            x, y=None, xerr=None, yerr=None,
            **errorbar_kw):

        @self._merge_kwargs("errorbar_kw", **errorbar_kw)
        @self._vectorize(cls=self, x=x, y=y, xerr=xerr, yerr=yerr)
        def _plot_errorbar(ax: Axes_plt,
                x, y=None, xerr=None, yerr=None,
                **errorbar_kw):
            """
            2D plot of y=f(x) with errorbars

            Parameters
            ----------
            ax :
            x :
            y :
            xerr, yerr :        array_like, optional
                Deviations in 'x','y'. 'x','y' may also be sent as 'uncertainties' arrays, then 'xerr','yerr' are disregarded
            errorbar_kw :

            Returns
            -------

            """

            if y is None:
                assert xerr is None and yerr is None, "If y is not given, xerr and yerr should not be given."
                y = x
                x = np.arange(len(y))

            x, xerr = to_numpy(x, xerr)
            y, yerr = to_numpy(y, yerr)

            ax.errorbar(x, y, xerr=xerr, yerr=yerr, **errorbar_kw)

        return _plot_errorbar()

    def plot_filled_error(self, ax: Axes_plt,
            x,
            y=None, yerr=None, n_std=2,
            y_low=None, y_high=None,
            **fill_between_kw):

        @self._merge_kwargs("fill_between_kw", **fill_between_kw)
        @self._vectorize(cls=self, ax=ax,
                x=x,
                y=y, yerr=yerr, n_std=n_std,
                y_low=y_low, y_high=y_high)
        def _plot_filled_error(ax: Axes_plt,
                x,
                y=None, yerr=None, n_std=2,
                y_low=None, y_high=None,
                **fill_between_kw):
            """
            Plot error using filled area

            Parameters
            ----------
            ax :   		        Axes
            x :  		        array_like
            y, yerr :  		    array_like, optional
            n_std :  		    int, optional
                                Number of standard deviations to fill.
            y_low, y_high :     array_like, optional
                                Lower and upper bounds of the filled area.
                                If not given, will be calculated as y-n_std*yerr, y+n_std*yerr
            fill_between_kw :

            Returns
            -------

            """

            # Data
            x, _ = to_numpy(x)
            if y is None:
                assert y_low is not None and y_high is not None, "(y, yerr) or (y_low, y_high) should be given."
            else:
                assert y_low is None and y_high is None, "(y, yerr) or (y_low, y_high) should be given."
                y, yerr = to_numpy(y, yerr)
                assert yerr is not None, "yerr should be given."

                y_low = y - n_std * yerr
                y_high = y + n_std * yerr

            ax.fill_between(x, y_low, y_high,
                    **fill_between_kw)

        return _plot_filled_error()

    def plot_data_and_curve_fit(self,
            x, y, fit_fcn, xerr=None, yerr=None,
            p_opt=None, p_cov=None, n_std=2, interp_factor=20,
            curve_fit_plot_kw=None, **errorbar_kw):

        @self._merge_kwargs("errorbar_kw", **errorbar_kw)
        @self._vectorize(cls=self,
                x=x, y=y, fit_fcn=fit_fcn, xerr=xerr, yerr=yerr,
                p_opt=p_opt, p_cov=p_cov, n_std=n_std, interp_factor=interp_factor,
                curve_fit_plot_kw=curve_fit_plot_kw)
        def _plot_data_and_curve_fit(ax: Axes_plt,
                x, y, fit_fcn, xerr=None, yerr=None,
                p_opt=None, p_cov=None, n_std=2, interp_factor=20,
                curve_fit_plot_kw=None, **errorbar_kw):
            """
            2D scatter plot y=f(x) + curve fit

            Parameters
            ----------
            ax :
            x, y :
            fit_fcn :
            xerr, yerr :        array_like, optional
                Deviations in 'x','y'. 'x','y' may also be sent as 'uncertainties' arrays, then 'xerr','yerr' are disregarded
            p_opt : Output parameter of scipy.optimize.curve_fit
            p_cov : Output parameter of scipy.optimize.curve_fit
            n_std : Number of standard deviations of confidence to be plotted with the fitted curve
            interp_factor :
            curve_fit_plot_kw :
            errorbar_kw :

            Returns
            -------

            Examples
            --------
                >>> import numpy as np
                >>> from liron_utils import graphics as gr
                >>> import scipy.optimize

                >>> N = 101
                >>> x = np.linspace(0, 10, N)
                >>> yerr = 5 * np.random.randn(N)
                >>> y = 2 * x ** 2 + 4 * x + 5 + yerr

                >>> def fit_fcn(x, a, b, c):
                >>>     return a * x ** 2 + b * x + c

                >>> (p_opt, p_cov) = scipy.optimize.curve_fit(fit_fcn, x, y)

                >>> Ax = gr.Axes()
                >>> Ax.plot_data_and_curve_fit(x, y, fit_fcn, yerr=yerr, p_opt=p_opt, p_cov=p_cov)
                >>> Ax.show_fig()
            """

            errorbar_kw = {
                              "label":  'Data',
                              "zorder": -1
                          } | errorbar_kw

            if curve_fit_plot_kw is None:
                curve_fit_plot_kw = dict()
            curve_fit_plot_kw = {
                                    "label": 'Curve fit'
                                } | curve_fit_plot_kw

            # Data
            x, xerr = to_numpy(x, xerr)
            y, yerr = to_numpy(y, yerr)
            p_opt, _ = to_numpy(p_opt)
            idx = np.argsort(x)
            x, y, xerr, yerr = x[idx], y[idx], xerr[idx], yerr[idx]

            self.plot_errorbar(x, y, xerr=xerr, yerr=yerr, **errorbar_kw)

            # Curve fit
            x_interp = interp1(x, interp_factor * len(x))
            fit_mid = fit_fcn(x_interp, *p_opt)

            ax.plot(x_interp, fit_mid, **curve_fit_plot_kw)

            # Confidence fill
            if p_opt is not None and p_cov is not None:
                p_err = np.sqrt(np.diag(p_cov))
                fit_low = np.ones(interp_factor * len(x)) * np.inf
                fit_high = np.ones(interp_factor * len(x)) * (-np.inf)

                for i in range(len(p_opt)):
                    p_opt_i = p_opt.copy()
                    p_opt_i[i] = p_opt[i] - n_std * p_err[i]
                    low = fit_fcn(x_interp, *p_opt_i)
                    p_opt_i[i] = p_opt[i] + n_std * p_err[i]
                    high = fit_fcn(x_interp, *p_opt_i)

                    fit_low = np.minimum(fit_low, np.minimum(low, high))
                    fit_high = np.maximum(fit_high, np.maximum(low, high))

                self.plot_filled_error(ax=ax, x=x_interp, y_low=fit_low, y_high=fit_high)

        return _plot_data_and_curve_fit()

    def plot_data_and_lin_reg(self,
            x, y, reg=None, xerr=None, yerr=None,
            reg_plot_kw=None, **errorbar_kw):

        @self._merge_kwargs("errorbar_kw", **errorbar_kw)
        @self._vectorize(cls=self,
                x=x, y=y, reg=reg, xerr=xerr, yerr=yerr,
                reg_plot_kw=reg_plot_kw)
        def _plot_data_and_lin_reg(ax: Axes_plt,
                x, y, reg=None, xerr=None, yerr=None,
                reg_plot_kw=None, **errorbar_kw):
            """
            2D scatter plot y=f(x) + linear regression.

            Examples:
                >>> import numpy as np
                >>> from scipy.stats import linregress
                >>> from liron_utils import graphics as gr

                >>> N = 100
                >>> x = np.arange(N)
                >>> y = 2*x + np.random.randn(N)
                >>> reg = linregress(x, y)

                >>> ax = gr.Axes()
                >>> ax.plot_data_and_lin_reg(x, y, reg)
                >>> ax.show_fig()

            Args:
                ax:
                x:
                y:                      f(x)
                reg:                    Output of scipy.stats.linregress
                xerr:                   Error in x
                yerr:                   Error in y
                reg_plot_kw:
                **errorbar_kw:

            Returns:

            """

            errorbar_kw = {
                              "label": "Data"
                          } | errorbar_kw

            if reg_plot_kw is None:
                reg_plot_kw = dict()
            reg_plot_kw = {
                              "label": fr"{errorbar_kw['label']} linreg: slope={reg.slope:.3f}$\pm${reg.stderr:.3f}, $R^2$={reg.rvalue ** 2:.3f}"
                          } | reg_plot_kw

            x, xerr = to_numpy(x, xerr)
            y, yerr = to_numpy(y, yerr)

            self.plot_errorbar(x, y, xerr=xerr, yerr=yerr,
                    **errorbar_kw)  # TODO: need to change to _plot_errorbar

            if reg is not None:
                tmp = [reg.slope * i + reg.intercept for i in x]
                self.plot(x, tmp, **reg_plot_kw)

        return _plot_data_and_lin_reg()

    def plot_line_collection(self,
            x: np.ndarray, y: np.ndarray, arr: np.ndarray,
            colorbar_kw=None, **LineCollection_kw):

        @self._vectorize(cls=self, x=x, y=y, arr=arr)
        def _plot_line_collection(ax: Axes_plt,
                x: np.ndarray, y: np.ndarray, arr: np.ndarray,
                colorbar_kw=None, **LineCollection_kw):
            """

            Args:
                ax:
                x:
                y:
                arr:
                colorbar_kw:
                **LineCollection_kw:

            Returns:

            """
            if colorbar_kw is None:
                colorbar_kw = dict()

            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            norm = plt.Normalize(vmin=np.min(arr), vmax=np.max(arr))

            # cmap = matplotlib.colors.ListedColormap(['r', 'g', 'b'])
            lc = matplotlib.collections.LineCollection(segments, norm=norm, **LineCollection_kw)
            lc.set_array(arr)

            line = ax.add_collection(lc)

            cbar = ax.figure.colorbar(line, ax=ax, **colorbar_kw)

            return line, cbar

        return _plot_line_collection(colorbar_kw=colorbar_kw, **LineCollection_kw)

    def plot_fft(self,
            x, fs=1.0, n=None,
            one_sided=True,
            dB=False,
            eps=1e-20,
            which="power",
            normalize=False,
            **plot_kw):

        @self._merge_kwargs("plot_kw", **plot_kw)
        @self._vectorize(cls=self, x=x, fs=fs, n=n, one_sided=one_sided, dB=dB, eps=eps, which=which,
                normalize=normalize)
        def _plot_fft(ax: Axes_plt,
                x, fs=1.0, n=None,
                one_sided=True,
                dB=False,
                eps=1e-20,
                which="power",
                normalize=False,
                **plot_kw):
            """
            Plot the magnitude spectrum of the FFT of a signal.

            Parameters
            ----------
            x : np.ndarray
                Input signal (1D array).
            fs : float, optional
                Sampling frequency (Hz). Default is 1.0.
            n : int, optional
                Number of points for FFT. If None, uses len(y).
            one_sided : bool, optional
                If True, plots only the positive frequencies. Default is True.
            dB : bool, optional
                If True, plot in decibels. Default is False.
            eps : float, optional
                Renormalization constant added to logarithmic plot
            which : str, optional
                Choose what to plot: "amp", "power", or "phase". Default is "power".
            normalize : bool, optional
                If True, normalize the transformed signal to have a maximal value of 1. Default is False.
            plot_kw : dict
                Additional keyword arguments for the plot.

            Returns
            -------
            Line2D
                The line object for the FFT plot.
            """

            x = np.asarray(x)
            if n is None:
                n = x.shape[0]

            X = np.fft.fft(x, n=n)
            if normalize:
                X /= X.max(axis=0)

            freqs = np.fft.fftfreq(n=n, d=1 / fs)

            if one_sided:
                X = X[:n // 2]
                freqs = freqs[:n // 2]
            else:
                X = np.fft.fftshift(X, axes=0)
                freqs = np.fft.fftshift(freqs)

            which = which.lower()
            if which == "amp":
                ydata = np.abs(X)
                ylabel = "Amplitude"
            elif which == "power":
                ydata = np.abs(X) ** 2
                ylabel = "Power"
            elif which == "phase":
                ydata = np.degrees(np.unwrap(np.angle(X)))
                ylabel = "Phase [deg]"
            # ticks = np.arange(-180, 181, 45)
            # ax.set_yticks(ticks)
            # tick_labels = [f"${t}^\circ$" for t in ticks]
            # ax.set_yticklabels(tick_labels)

            else:
                raise ValueError(f"which must be one of 'amp', 'power', or 'phase'. Got: {which}")

            if dB and which in ("amp", "power"):
                ydata = 10 * np.log10(ydata + eps)
                ylabel += " [dB]"

            line = ax.plot(freqs, ydata, **plot_kw)

            if ax.get_title() == "":
                ax.set_title(f"FFT ({which})")
            if ax.get_xlabel() == "":
                ax.set_xlabel("Frequency [Hz]")
                if fs == 1.0:
                    ax.set_xlabel("Frequency [normalized]")
            if ax.get_ylabel() == "":
                ax.set_ylabel(ylabel)

            return (X, freqs), line

        return _plot_fft()

    def plot_specgram(self,
            y: np.ndarray, fs: int,
            **specgram_kw):

        @self._merge_kwargs("specgram_kw", **specgram_kw)
        @self._vectorize(cls=self, y=y, fs=fs)
        def _plot_specgram(ax: Axes_plt,
                y: np.ndarray, fs: int,
                **specgram_kw):
            """
            Plot spectrogram

            Args:
                ax:
                y:                      Data, given as 1D array with respect to time
                fs:                     Sample rate
                **specgram_kw:

            Returns:

            """

            specgram_out = ax.specgram(y, Fs=fs,
                    **specgram_kw)  # todo: add option for log frequency mapping using librosa.feature.melspectrogram()
            spectrum, freqs, t, im = specgram_out

            scaling = {0: "", 3: "K", 6: "M", 9: "G", 12: "T"}  # todo: use siprefix.si_format
            scale = 0
            if fs != 1:
                scale = 3 * (int(np.log10(freqs[-1])) // 3)

                extent = im.get_extent()
                extent = (extent[0], extent[1], extent[2] / 10 ** scale, extent[3] / 10 ** scale)
                im.set_extent(extent=extent)

            if ax.get_title() == "":
                ax.set_title("Spectrogram")
            if ax.get_xlabel() == "":
                ax.set_xlabel("Time [sec]")
            if ax.get_ylabel() == "":
                ax.set_ylabel(f"Frequency [{scaling[scale]}Hz]")

            ax.figure.colorbar(im, ax=ax)

            return specgram_out

        return _plot_specgram()

    def plot_surf(self,
            x, y, z,
            **plot_surface_kw):

        @self._merge_kwargs("plot_surface_kw", **plot_surface_kw)
        @self._vectorize(cls=self, x=x, y=y, z=z)
        def _plot_surf(ax: Axes_plt,
                x, y, z,
                **plot_surface_kw):
            """
            3D surf plot of z=f(x,y)

            Args:
                ax:
                x:          1D or 2D. If given as 1D, will automatically apply meshgrid and treat z as a lambda function
                y:          1D or 2D. If given as 1D, will automatically apply meshgrid and treat z as a lambda function
                z:          2D or lambda function

            Returns:

            """

            assert hasattr(ax, "plot_surface"), "Axes does not have a plot_surface attribute. " \
                                                "make sure that you created an axes with projection='3d'"

            X, Y, Z = x, y, z
            if x.ndim == 1:
                X, Y = np.meshgrid(x, y)
            if callable(z):
                Z = z(X, Y)
            if np.all(Z.shape == np.flip(X.shape)):
                Z = Z.T

            ax.plot_surface(X, Y, Z, **plot_surface_kw)

        # ax.figure.colorbar(matplotlib.cm.ScalarMappable(), ax=ax)

        return _plot_surf()

    def plot_contour(self,
            x, y, z, contours,
            *args, **kwargs):

        @self._vectorize(cls=self, x=x, y=y, z=z, contours=contours)
        def _plot_contour(ax: Axes_plt,
                x, y, z, contours,
                *args, **kwargs):
            """
            Contour plot of scalar field z=f(x,y)

            Parameters
            ----------
            ax :
            x :
            y :
            z :
            contours :
            args, kwargs :
             :

            Returns
            -------

            """

            cs = ax.contour(x, y, z, contours, *args, **kwargs)
            ax.clabel(cs, inline=True, fontsize=10)
            return cs

        return _plot_contour(*args, **kwargs)

    def plot_animation(self, axs: (Axes_plt, np.ndarray[Axes_plt]),
            func: callable = None,
            n_frames: int = None,
            data: list[np.ndarray] = None,
            data_instance: list = None,
            titles: list = None,
            *args, **kwargs):
        """
        Plot animation

        Examples
        --------
            >>> import numpy as np
            >>> from liron_utils import graphics as gr

            >>> nimages = 10
            >>> images = np.random.random((nimages))
            >>> Ax = gr.Axes()
            >>> Ax.plot_animation(images)
            >>> Ax.save_fig("test.gif")

        Parameters
        ----------
        axs :               Axes or list[Axes]
                            All axes should be of the same figure
        func :              callable, optional
                            Function to be called for each frame. If not given, will use update_data
        n_frames :		    int, optional
                            Number of frames to be plotted. If not given, will use len(data[0])
        data :              array_like, optional
                            The data to be plotted, given as list of size len(axs) of:
                                - (image) a 4D array of size [#n_frames, x, y]
                                - (plot)  a 4D array of size [#n_frames, 2, xy]
        data_instance   :   array_like of matplotlib objects, optional
                            Image/line/etc. handle to use in case user wants some pre-defined properties.
                            First axis should be of size 'len(axs)'
        titles :            list or function handle, optional
                            Axis titles. Can be given as:
                                - List of changing titles
                                - function handle whose input argument is iterable and outputs the title
        args, kwargs :      sent to matplotlib.animation.FuncAnimation

        Returns
        -------

        """
        assert (func is not None and n_frames is not None) or \
               (data is not None and data_instance is not None), \
            "Either (func, n_frames) or (data, data_instance) should be given."

        if type(axs) is Axes_plt:  # convert to array
            axs = [axs]
            data = [data]
            data_instance = [data_instance]

        assert (axs[i].figure == axs[i + 1].figure
            for i in range(len(axs) - 1)), "All axes should be of the same figure."

        if func is None:
            assert len(axs) == len(data) == len(data_instance), "Number of axes should be equal to number of data sets."
            n_frames = len(data[0])

        if titles is not None:
            kwargs = {"blit": False} | kwargs

        # if callable(titles):
        # 	titles = [titles(i) for i in range(n_frames)]  # convert to list

        def update_data(i):
            """
            Update data for animation

            Parameters
            ----------
            i : Frame index
            """
            for idx_ax, ax in enumerate(axs):
                h = data_instance[idx_ax]
                if type(h) is list:  # multiple objects
                    for j, hh in enumerate(h):
                        hh.set_data(data[idx_ax][i][j])  # update images
                else:
                    h.set_data(data[idx_ax][i])  # update image

                if titles is not None:
                    ax.set_title(titles[i])  # update title

            return data_instance

        if func is None:
            func = update_data

        self.func_animation = matplotlib.animation.FuncAnimation(fig=axs[0].figure,
                func=func, frames=n_frames,
                *args, **kwargs)
