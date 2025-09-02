from .base import *
from .axes import *
from .plotting import *
from .utils import *
from ..pure_python import is_notebook

__all__ = [s for s in dir() if not s.startswith('_')]

update_rcParams()  # Change default MatPlotLib parameters (e.g, figure size, label size, grid, colors, etc.)

if is_notebook():
    update_rcParams("liron-utils-notebook")

# TODO:
#   - matplotlib.animation.FuncAnimation
#   - Transfer my default kwargs to merge with mpl.rcParams
