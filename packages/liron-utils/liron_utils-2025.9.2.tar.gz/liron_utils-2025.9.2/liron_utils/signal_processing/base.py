import numpy as np
import scipy.special
import scipy.signal
import scipy.interpolate

norm_axis_idx = np.core.multiarray.normalize_axis_index
meshgrid = np.mgrid
gamma = scipy.special.gamma
windows = scipy.signal.windows
sliding_window = np.lib.stride_tricks.sliding_window_view


def array(*args):
	"""
	Convert any data type to numpy.ndarray

	Example:
		>>> x = range(5)  # x = [0,1,2,3,4]
		>>> y = array(x)  # y = np.array([0,1,2,3,4])

	Args:
		*args:          Send as many arrays as you'd like

	Returns:

	"""
	args = list(args)
	for i in range(len(args)):
		if args[i] is not None:
			args[i] = np.asarray(args[i]).squeeze()
	if len(args) == 1:
		return args[0]
	return args


def sigmoid(x: np.ndarray, L: float = 1, k: float = 1, x0: float = 0):
	"""
	Sigmoid/logistic function with parameters L,k,x0 (standard sigmoid has values 1,1,0)

	Args:
		x:          Points to evaluate
		L:          Supremum / maximal asymptotic value
		k:          Steepness
		x0:         Center

	Returns:

	"""
	out = L / (1 + np.exp(-k * (x - x0)))
	return out


def buffer(y: np.ndarray, frame: int, overlap: int) -> np.ndarray:
	"""
	Buffer a 1D array into segments with overlap. Output is a 2D matrix.
	Equivalent to MATLAB's <buffer> function.

	Args:
		y ():               Input array
		frame ():           Length of each segment
		overlap ():         Overlap of every two adjacent segments

	Returns:
		2D buffered array
	"""

	assert y.ndim == 1, "Input array must be 1D"

	hop = frame - overlap
	nframes = int(np.ceil(y.size / hop))

	y_padded = np.concatenate([np.zeros(overlap), y, np.zeros(frame)])
	indices = np.sum(meshgrid[0:frame, 0:nframes * hop:hop], axis=0)
	out = np.take(y_padded, indices, axis=0)
	return out


def unbuffer(y: np.ndarray, frame: int, overlap: int) -> np.ndarray:
	"""
	Perform the inverse operation of the <buffer> function.

	Args:
		y ():               Buffered matrix
		frame ():           Length of each segment
		overlap ():         Overlap of every two adjacent segments

	Returns:
		1D unbuffered array
	"""
	if y.ndim == 1:
		y = np.tile(y, (frame, 1))
	assert y.ndim == 2
	frame = y.shape[0]
	out = y[min(overlap + 1, frame) - 1:, :]
	out = np.reshape(out.T, -1)
	return out


def interp1(y: np.ndarray, n: int, axis: int = -1, *args, **kwargs) -> np.ndarray:
	"""
	1D interpolation or extrapolation.

	Args:
		y:                  Input array
		n:                  Desired length of output array
		axis:               Axis along which to interpolate
		*args:              Passed to scipy.interpolate.interp1d
		**kwargs:           Passed to scipy.interpolate.interp1d

	Returns:

	"""

	if y.shape[axis] == n:
		return y

	h = scipy.interpolate.interp1d(np.linspace(0, n - 1, y.shape[axis]), y, axis=axis, *args, **kwargs)
	out = h(range(n))
	return out


def rms(x: np.ndarray, *args, **kwargs):
	"""
	Root mean squared

	Args:
		x:
		*args:
		**kwargs:

	Returns:

	"""
	return np.sqrt(np.mean(x ** 2, *args, **kwargs))


def rescale(x: np.ndarray, lower=0, upper=1):
	x = x.astype(float)
	# bring to [0, 1]
	x -= np.min(x)
	x /= np.max(x)
	# bring to [lower, upper]
	x *= upper - lower
	x += lower
	return x
