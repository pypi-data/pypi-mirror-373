import numpy as np

"""
Prints:
	f"{a:.2fP}" -> "a±0.01"  (P = pretty-print ±)

Math functions 
	umath and unumpy has all the math functions that math has, but for arrays of ufloats

"""


def __repr__(self):
	# Not putting spaces around "+/-" helps with arrays of
	# Variable, as each value with an uncertainty is a
	# block of signs (otherwise, the standard deviation can be
	# mistaken for another element of the array).

	std_dev = self.std_dev  # Optimization, since std_dev is calculated

	# A zero standard deviation is printed because otherwise,
	# ufloat_fromstr() does not correctly parse back the value
	# ("1.23" is interpreted as "1.23(1)"):

	if std_dev:
		std_dev_str = repr(std_dev)
	else:
		std_dev_str = '0'

	return "%r±%s" % (self.nominal_value, std_dev_str)


try:
	import uncertainties

	uncertainties.core.AffineScalarFunc.__repr__ = __repr__
except ImportError:
	pass


def is_unumpy(arr):
	import uncertainties

	try:
		return any([isinstance(arr[i], uncertainties.core.AffineScalarFunc) for i in range(len(arr))])
	except TypeError:
		return False


def is_ufloat(x):
	return hasattr(x, "std_dev")


def to_numpy(x, xerr=None):
	"""
	Convert unumpy->numpy and ufloat->float. If already numpy, return as is.
	Args:
		x ():           unumpy or ufloat. In this case, don't need to provide xerr as it is already contained in x
		xerr ():        Needed only in case x is numpy instead of unumpy

	Returns:

	"""
	import uncertainties
	from uncertainties import unumpy

	def unumpy_to_numpy(arr):
		val = unumpy.nominal_values(arr)
		dev = unumpy.std_devs(arr)
		# if not np.any(dev):
		# 	dev = None
		return val, dev

	def ufloat_to_float(x):
		val = uncertainties.nominal_value(x)
		dev = uncertainties.std_dev(x)
		# if dev == 0:
		# 	dev = None
		return val, dev

	if is_unumpy(x):
		x, xerr = unumpy_to_numpy(x)

	elif is_ufloat(x):
		x, xerr = ufloat_to_float(x)

	return x, xerr


def from_numpy(x, xerr=0):
	from uncertainties import ufloat, unumpy

	if type(x) is float:
		return ufloat(x, xerr)
	else:
		return unumpy.uarray(x, xerr)


def val(x, xerr=None):
	return to_numpy(x, xerr)[0]


def dev(x, xerr=None):
	return to_numpy(x, xerr)[1]


def uncertainty(x, xerr=None):
	return dev(x, xerr) / val(x, xerr)


def make_independent(x, xerr=None):
	from uncertainties import unumpy

	x, xerr = to_numpy(x, xerr)

	return unumpy.uarray(x, xerr)


def histogram(x, xerr=None, **kwargs):
	x, xerr = to_numpy(x, xerr)

	density = kwargs.pop("density", False)

	hist, bins = np.histogram(x, **kwargs)

	hist_err = np.zeros(len(hist))
	for i in range(len(hist)):
		in_bin = (bins[i] <= x) & (x < bins[i + 1])
		hist_err[i] = np.sqrt(np.sum(xerr[in_bin] ** 2))

	hist = from_numpy(hist, hist_err)

	if density:
		hist /= np.sum(hist)

	return hist, bins
