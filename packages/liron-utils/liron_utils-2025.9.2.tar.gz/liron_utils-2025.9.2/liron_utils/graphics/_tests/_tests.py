# from import_tracker import track_module
# from pprint import pprint
#
# x = track_module(module_name="liron_utils.graphics", track_import_stack=True, show_optional=True)
# pprint(x)

import numpy as np
from scipy.signal import windows
from liron_utils import graphics as gr

gr.update_rcParams("liron-utils-text_color", "white")

Ax = gr.Axes(shape=(2, 1))
gr.Axes(axs=Ax.axs[0, 0]).plot_fft(windows.hamming(1000), one_sided=False, dB=True, which="power")
Ax.axs[0, 0].set_ylim([-100, 0])
gr.Axes(axs=Ax.axs[1, 0]).plot_fft(windows.hamming(1000), one_sided=False, dB=True, which="phase")
gr.set_props()

# import scipy.optimize
# import matplotlib.pyplot as plt
#
# N = 101
# x = np.linspace(0, 10, N)
# yerr = 5 * np.random.randn(N)
# y = 2 * x ** 2 + 4 * x + 5 + yerr
#
#
# def fit_fcn(x, a, b, c):
#     return a * x ** 2 + b * x + c
#
# (p_opt, p_cov) = scipy.optimize.curve_fit(fit_fcn, x, y)
#
# fig, ax = gr.new_figure()
# gr.draw_xy_lines(ax)
# ax.plot(range(5))
# # gr.plot_data_and_curve_fit(x, y, fit_fcn, yerr=yerr, p_opt=p_opt, p_cov=p_cov)
# # ax.show_fig()
# fig.show()
# pass

# Ax = gr.AxesLiron(2, 1)
# t = np.linspace(0, 10, 1001)
# gr.plot(Ax.axs[0, 0], t, np.sin(t), label="1")
# gr.plot(Ax.axs[1, 0], t, np.cos(t))
# gr.plot(Ax.axs[0, 0], t, np.log(t), label="2")
# gr.plot(Ax.axs[1, 0], t, np.exp(t))
# # gr.plot(Ax.axs[0, 2], t, np.sqrt(t))
# # gr.plot(Ax.axs[1, 2], t, np.square(t))
#
# Ax.set_props(sup_title="abc",
#              ax_title=[1, 2],
#              grid=[True, False],
#              limits=[
#                  None,
#                  [[-5, 5], [-1, 1]]
#              ],
#              show_fig=True)

# def outer(func):
#     def inner(x, y):
#         z = np.zeros(5)
#         for j in range(len(x)):
#             z[j] = func(x[j], y[j])
#         return z
#
#     return inner
#
#
# @outer
# def adder(x, y):
#     return x + y
#
# @outer
# def subtract(x, y):
#     return x - y
#
# @atexit.register
# def bye():
#     print("Bye")
#
#
# x = [0,1,2,3,4]
# y = [0,1,2,3,4]
# z = adder(x, y)


pass
