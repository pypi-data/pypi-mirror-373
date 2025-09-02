import numpy as np
import scipy.fft
import scipy.signal
import scipy.ndimage.filters
import scipy.optimize
import scipy.linalg

# Fourier Transform
fft = scipy.fft.fft
fft2 = scipy.fft.fft2
fftn = scipy.fft.fftn
fftshift = scipy.fft.fftshift
ifft = scipy.fft.ifft
ifft2 = scipy.fft.ifft2
ifftn = scipy.fft.ifftn
ifftshift = scipy.fft.ifftshift
dft_matrix = scipy.linalg.dft  # in 'scipy.linalg._special_matrices'
fftfreq = scipy.fft.fftfreq
# todo: Fractional Fourier Transform: pip install git+ssh://git@github.com/audiolabs/python_frft.git#egg=frft


def nextpow2(a):
	"""
	Exponent of next higher power of 2. Returns the exponents for the smallest powers
	of two that satisfy 2**p > a

	Parameters
	----------
	a :     array_like

	Returns
	-------
	p :     array_like

	"""

	if np.isscalar(a):
		if a == 0:
			p = 0
		else:
			p = int(np.ceil(np.log2(a)))
	else:
		a = np.asarray(a)
		p = np.zeros(a.shape, dtype=int)
		idx = (a != 0)
		p[idx] = np.ceil(np.log2(a[idx]))

	return p


# Convolution
conv = scipy.signal.convolve
conv2 = scipy.signal.convolve2d
convn = scipy.signal.convolve
deconv = scipy.signal.deconvolve
convolution_matrix = scipy.linalg.convolution_matrix  # in 'scipy.linalg._special_matrices'

# Digital filtering
filter = scipy.signal.lfilter
filtfilt = scipy.signal.filtfilt  # Zero-phase digital filtering
movmedian = scipy.ndimage.filters.median_filter
movmax = scipy.ndimage.filters.maximum_filter
movmin = scipy.ndimage.filters.minimum_filter


def filter2(h, x, shape="full"):
	"""
	2-D digital FIR filter

	Parameters
	----------
	h :     array_like
		The filter, given as a 2D matrix
	x :     array_like
		The data, given as a 2D matrix
	shape : str {'full', 'valid', 'same'}, optional
		A string indicating the size of the output:

		``full``
		   Return the full 2-D filtered data.
		``valid``
		   Return only parts of the filtered data that are computed without zero-padded edges.
		``same``
		   Return the central part of the filtered data, which is the same size as x.

	Returns
	-------
	out :   array_like
		The filtered data
	"""

	out = scipy.signal.convolve2d(x, np.rot90(h, 2), mode=shape)
	return out


def movsum(x: np.ndarray, N: int, mode: str = 'same') -> np.ndarray:
	"""
	Moving sum filter

	Args:
		x:          Input array
		N:          Filter size
		mode:       Mode

	Returns:
		Filtered array
	"""

	return np.correlate(x, np.ones(N), mode=mode)


def movmean(x: np.ndarray, N: int, *args, **kwargs) -> np.ndarray:
	"""
	Moving average filter

	Args:
		x:          Input array
		N:          Filter size
		mode:       Mode

	Returns:
		Filtered array
	"""

	return movsum(x, N, *args, **kwargs) / N


def movrms(x: np.ndarray, N: int, *args, **kwargs) -> np.ndarray:
	"""
	Moving RMS filter

	Args:
		x:          Input array
		N:          Filter size
		mode:       Mode

	Returns:
		Filtered array
	"""

	return np.sqrt(movmean(x ** 2, N, *args, **kwargs))


def movvar(x: np.ndarray, N: int, ddof: int = 1, *args, **kwargs) -> np.ndarray:
	"""
	Moving variance filter

	Args:
		x:          Input array
		N:          Filter size
		ddof:

	Returns:
		Filtered array
	"""

	out = movmean(x ** 2, N, *args, **kwargs) - movmean(x, N, *args, **kwargs) ** 2
	out *= N / (N - ddof)
	return out


def movstd(x: np.ndarray, N: int, *args, **kwargs) -> np.ndarray:
	"""
	Moving std filter

	Args:
		x:          Input array
		N:          Filter size
		mode:       Mode

	Returns:
		Filtered array
	"""
	out = np.sqrt(movvar(x, N, *args, **kwargs))
	return out
