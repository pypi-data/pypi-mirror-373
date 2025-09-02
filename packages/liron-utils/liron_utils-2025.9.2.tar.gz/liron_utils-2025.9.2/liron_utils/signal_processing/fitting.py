import numpy as np
import scipy.stats
import scipy.optimize
import scipy.odr as odr
import scipy.signal
from collections import namedtuple

from .stats import chi_squared_test
from ..uncertainties_math import val, to_numpy, from_numpy
from .. import graphics as gr

linear_regression = scipy.stats.linregress


def linear_fit(x, y, xerr=None, yerr=None, beta0=None, **kwargs):
	"""
	Linear regression

	Parameters
	----------
	x, y :              array_like
		Data
	xerr, yerr :        array_like, optional
		Deviations in 'x','y'. 'x','y' may also be sent as 'uncertainties' arrays, then 'xerr','yerr' are disregarded
	beta0 :             array_like, optional
		Initial parameter values, sent as a 2-tuple '(a, b)', where 'a' is the slope and 'b' is the intercept
	kwargs :            sent to odr.ODR

	Returns
	-------

	"""
	x, xerr = to_numpy(x, xerr)
	y, yerr = to_numpy(y, yerr)

	if xerr is not None:
		xerr[xerr == 0] = np.nan
	if yerr is not None:
		yerr[yerr == 0] = np.nan

	if beta0 is None:
		beta0 = [0, 0]  # [slope, intercept]

	def f(B, x):
		return B[0] * x + B[1]

	linear_model = odr.Model(f)
	data = odr.RealData(x, y, xerr, yerr)

	out = odr.ODR(data, linear_model, beta0, **kwargs).run()

	# Calculate params
	from uncertainties import ufloat
	slope = ufloat(out.beta[0], out.sd_beta[0])
	intercept = ufloat(out.beta[1], out.sd_beta[1])

	pred = lambda x: f([slope, intercept], x)

	y_pred = pred(x)

	from sklearn.metrics import r2_score

	r2 = r2_score(y, val(y_pred))

	Linear_regression = namedtuple("Linear_regression",
			["h", "eval", "slope", "intercept", "r2"])
	return Linear_regression(h=out, eval=pred, slope=slope, intercept=intercept, r2=r2)


def curve_fit(fit_fcn,
		x, y, p0=None,
		xerr=None, yerr=None,
		plot=False, plot_data_and_curve_fit_kw=None,
		**kwargs):
	"""
	Use non-linear least squares to fit a function, f, to data.
	Assumes ``y = f(x, *params) + eps``.

	Parameters
	----------
	fit_fcn :   callable
				The model function, f(x, ...). It must take the independent
				variable as the first argument and the parameters to fit as
				separate remaining arguments
	x :         array_like
				The independent variable where the data is measured.
				Should usually be an M-length sequence or an (k,M)-shaped array for
				functions with k predictors, but can actually be any object
	y :         array_like
				The dependent data, a length M array - nominally ``f(xdata, ...)``
	p0 :        array_like, optional
				Initial guess for the parameters (length N). If None, then the
				initial values will all be 1 (if the number of parameters for the
				function can be determined using introspection, otherwise a
				ValueError is raised).
	xerr :      array_like, optional
				Determines the uncertainty in `xdata` (used only for plotting).
	yerr :      None or M-length sequence or MxM array, optional
				Determines the uncertainty in `ydata`. If we define residuals as
				``r = ydata - f(xdata, *popt)``, then the interpretation of `sigma`
				depends on its number of dimensions:
					- A 1-D `sigma` should contain values of standard deviations of
					  errors in `ydata`. In this case, the optimized function is
					  ``chisq = sum((r / sigma) ** 2)``.
					- A 2-D `sigma` should contain the covariance matrix of
					  errors in `ydata`. In this case, the optimized function is
					  ``chisq = r.T @ inv(sigma) @ r``.
					- None (default) is equivalent of 1-D `sigma` filled with ones
	plot :      bool, optional
				Set to 'True' if you want to plot the data
	plot_data_and_curve_fit_kw :
	kwargs :    sent to 'scipy.optimize.curve_fit'

	Returns
	-------

	"""
	if plot_data_and_curve_fit_kw is None:
		plot_data_and_curve_fit_kw = {}

	x, xerr = to_numpy(x, xerr)
	y, yerr = to_numpy(y, yerr)
	p0 = val(p0)

	if xerr is not None and xerr.size == 1:
		xerr = np.repeat(xerr, len(x))
	if yerr is not None and yerr.size == 1:
		yerr = np.repeat(yerr, len(y))

	# Curve-Fit
	p_opt, p_cov = scipy.optimize.curve_fit(fit_fcn, x, y, p0=p0, sigma=yerr, **kwargs)

	chi2_red = chi_squared_test(f_exp=fit_fcn(x, *p_opt), f_obs=y, f_obs_err=yerr, ddof=len(p_opt), reduced=True)

	p_opt = from_numpy(p_opt, np.sqrt(np.diag(p_cov)))

	if plot:
		Ax = gr.Axes()
		Ax.plot_data_and_curve_fit(x, y, fit_fcn,
				xerr=xerr, yerr=yerr,
				p_opt=p_opt, p_cov=p_cov,
				**plot_data_and_curve_fit_kw)

		return p_opt, p_cov, chi2_red, Ax

	return p_opt, p_cov, chi2_red


def find_peaks(
		y, yerr=None,
		x=None, xerr=None,
		n_fit_points=None,
		plot=False,
		**kwargs):
	"""

	Parameters
	----------
	x :
	y :
	xerr :
	yerr :
	kwargs :

	Returns
	-------

	"""

	x, xerr = to_numpy(x, xerr)
	y, yerr = to_numpy(y, yerr)
	if x is None:
		x = np.arange(len(y))
	if xerr is not None and xerr.size == 1:
		xerr = np.repeat(xerr, len(x))
	if yerr is not None and yerr.size == 1:
		yerr = np.repeat(yerr, len(y))

	peaks, properties = scipy.signal.find_peaks(val(y), **kwargs)

	if n_fit_points is None:
		x_peaks = x[peaks]
		y_peaks = y[peaks]
		if xerr is not None:
			x_peaks = from_numpy(x_peaks, xerr[peaks])
		if yerr is not None:
			y_peaks = from_numpy(y_peaks, yerr[peaks])

	else:
		# fit quadratic around peaks
		def quadratic(x, a, b, c):
			return a * x ** 2 + b * x + c

		x_peaks = from_numpy(np.zeros(len(peaks)), 0)
		y_peaks = from_numpy(np.zeros(len(peaks)), 0)
		for i in range(len(peaks)):
			# Define a small range around the peak
			left = max(0, peaks[i] - n_fit_points)
			right = min(len(y), peaks[i] + n_fit_points + 1)

		# Perform quadratic fit
		x0 = np.mean(x[left:right])
		popt = curve_fit(fit_fcn=quadratic,
				x=x[left:right] - x0,
				y=y[left:right],
				xerr=xerr[left:right] if xerr is not None else None,
				yerr=yerr[left:right] if yerr is not None else None,
				p0=[0, 0, y[peaks[i]]],
		)[0]
		a_center, b_center, c_center = popt
		a = a_center
		b = b_center - 2 * a_center * x0
		c = a_center * x0 ** 2 - b_center * x0 + c_center

		if val(a) == 0:
			raise ValueError("Quadratic fit failed: a=0")

		x_peaks[i] = - b / (2 * a)  # Vertex of the parabola (peak location)
		y_peaks[i] = quadratic(x_peaks[i], a, b, c)

	if plot:
		Ax = gr.Axes()
		Ax.plot_errorbar(x, y,
				xerr=xerr, yerr=yerr)
		Ax.plot_errorbar(x_peaks, y_peaks,
				marker="o", color="black", linestyle="none")

		return x_peaks, y_peaks, peaks, properties, Ax

	return x_peaks, y_peaks, peaks, properties
