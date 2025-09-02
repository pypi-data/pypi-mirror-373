import numpy as np
from liron_utils import uncertainties_math as un
from liron_utils import graphics


t = np.linspace(0, 10, 101)
x = np.sin(2 * np.pi * 1 * t)
xerr = 0.1 * np.random.uniform(size=t.size)

x = un.from_numpy(x, xerr)

ax = graphics._AxesLiron()
graphics.plot_errorbar(ax.axs, t, x)
ax.ax_props(ax.axs, show_fig=True)
pass
