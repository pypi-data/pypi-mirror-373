import numpy as np
import scipy.stats
from collections import namedtuple

from ..uncertainties_math import val, to_numpy

Power_divergenceResult = namedtuple('Power_divergenceResult',
		('statistic', 'pvalue'))


def chi_squared_test(
		f_exp, f_obs,
		f_obs_err=None,
		ddof: int = 0,
		reduced: bool = False):
	"""
	Compute the chi-squared statistic and p-value for the goodness-of-fit test (see ref. [1]).
	Same as scipy.stats.chisquare(f_obs, f_exp, ddof)

    Parameters
    ----------
    f_exp :     array-like
        Expected (theoretical) values.
    f_obs :     array-like
        Observed values.
    f_obs_err : array-like, optional
    	Uncertainties in the observed values.
    ddof :      int, optional
        Degrees of freedom adjustment (e.g., number of fitted parameters). Default is 0.
    reduced :   bool, optional
        If True, the reduced chi-squared test is performed (see ref. [2]). Default is False.
        - chi2 >> 1 indicates a poor model fit.
        - chi2 > 1 indicates that the fit has not fully captured the data (or that the error variance has been
                underestimated).
        - A value of chi2 ~ 1 around indicates that the extent of the match between observations and estimates is
                in accord with the error variance.
        - chi2 < 1 indicates that the model is overfitting the data (either the model is improperly fitting noise,
                or the error variance has been overestimated).

    Returns
    -------
    chi2 : float
        Chi-squared statistic.
    p_value : float
        p-value for the goodness-of-fit test.

    References
    ----------
    [1] https://en.wikipedia.org/wiki/Pearson%27s_chi-squared_test
    [2] https://en.wikipedia.org/wiki/Reduced_chi-squared_statistic
	"""

	f_exp, f_exp_err = to_numpy(f_exp)
	f_obs, f_obs_err = to_numpy(f_obs, f_obs_err)

	if reduced:
		assert f_obs_err is not None, "f_exp_err, f_obs_err must be provided."
		if f_exp_err is None:
			f_exp_err = 0
		sigma2 = np.sqrt(f_exp_err ** 2 + f_obs_err ** 2)
		chi2 = np.sum((f_obs - f_exp) ** 2 / sigma2 ** 2)
	else:
		f_exp /= f_exp.sum()
		f_obs /= f_obs.sum()
		chi2 = np.sum((f_obs - f_exp) ** 2 / f_exp)

	dof = len(f_exp) - 1 - ddof
	p_value = scipy.stats.chi2.sf(val(chi2), dof)

	return Power_divergenceResult(chi2, p_value)
