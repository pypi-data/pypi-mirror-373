__all__ = ['BaseProgressBar', 'TextProgressBar',
	'EnhancedTextProgressBar', 'TqdmProgressBar',
	'HTMLProgressBar', 'tqdm_']

import time
import datetime
import sys
from collections.abc import Iterable, Callable
from tqdm import tqdm


class BaseProgressBar(object):
	"""
	An abstract progress bar with some shared functionality.

	Example usage:

		n_vec = linspace(0, 10, 100)
		pbar = TextProgressBar(len(n_vec))
		for n in n_vec:
			pbar.update()
			compute_with_n(n)
		pbar.finished()

	"""

	def __init__(self, iterations=0, chunk_size=10, **kwargs):
		self._start(iterations, chunk_size)

	def _start(self, iterations, chunk_size=10, **kwargs):
		self.N = float(iterations)
		self.n = 0
		self.p_chunk_size = chunk_size
		self.p_chunk = chunk_size
		self.t_start = time.time()
		self.t_done = self.t_start - 1

	def update(self):
		pass

	def total_time(self):
		return self.t_done - self.t_start

	def time_elapsed(self):
		return "%6.2fs" % (time.time() - self.t_start)

	def time_remaining_est(self, p):
		if 100 >= p > 0.0:
			t_r_est = (time.time() - self.t_start) * (100.0 - p) / p
		else:
			t_r_est = 0

		dd = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=t_r_est)
		time_string = "%02d:%02d:%02d:%02d" % \
		              (dd.day - 1, dd.hour, dd.minute, dd.second)

		return time_string

	def finished(self):
		self.t_done = time.time()


class TextProgressBar(BaseProgressBar):
	"""
	A simple text-based progress bar.
	"""

	def __init__(self, iterations=0, chunk_size=10, **kwargs):
		super()._start(iterations, chunk_size)

	def update(self):
		self.n += 1
		n = self.n
		p = (n / self.N) * 100.0
		if p >= self.p_chunk:
			print("%4.1f%%." % p +
			      " Run time: %s." % self.time_elapsed() +
			      " Est. time left: %s" % self.time_remaining_est(p))
			sys.stdout.flush()
			self.p_chunk += self.p_chunk_size

	def finished(self):
		self.t_done = time.time()
		print("Total run time: %s" % self.time_elapsed())


class EnhancedTextProgressBar(BaseProgressBar):
	"""
	An enhanced text-based progress bar.
	"""

	def __init__(self, iterations=0, chunk_size=10, **kwargs):
		super()._start(iterations, chunk_size)
		self.fill_char = '*'
		self.width = 25

	def update(self):
		self.n += 1
		n = self.n
		percent_done = int(round(n / self.N * 100.0))
		all_full = self.width - 2
		num_hashes = int(round((percent_done / 100.0) * all_full))
		prog_bar = ('[' + self.fill_char * num_hashes +
		            ' ' * (all_full - num_hashes) + ']')
		pct_place = (len(prog_bar) // 2) - len(str(percent_done))
		pct_string = '%d%%' % percent_done
		prog_bar = (prog_bar[0:pct_place] +
		            (pct_string + prog_bar[pct_place + len(pct_string):]))
		prog_bar += ' Elapsed %s / Remaining %s' % (
			self.time_elapsed().strip(),
			self.time_remaining_est(percent_done))
		print('\r', prog_bar, end='')
		sys.stdout.flush()

	def finished(self):
		self.t_done = time.time()
		print("\r", "Total run time: %s" % self.time_elapsed())


class TqdmProgressBar(BaseProgressBar):
	"""
	A progress bar using tqdm module
	"""

	def __init__(self, iterations=0, chunk_size=10, **kwargs):
		from tqdm.auto import tqdm
		self.pbar = tqdm(total=iterations, **kwargs)
		self.t_start = time.time()
		self.t_done = self.t_start - 1

	def update(self):
		self.pbar.update()

	def finished(self):
		self.pbar.close()
		self.t_done = time.time()


class HTMLProgressBar(BaseProgressBar):
	"""
	A simple HTML progress bar for using in IPython notebooks. Based on
	IPython ProgressBar demo notebook:
	https://github.com/ipython/ipython/tree/master/examples/notebooks

	Example usage:

		n_vec = linspace(0, 10, 100)
		pbar = HTMLProgressBar(len(n_vec))
		for n in n_vec:
			pbar.update()
			compute_with_n(n)
	"""

	def __init__(self, iterations=0, chunk_size=1.0, **kwargs):
		from IPython.display import HTML, Javascript, display
		import uuid

		self.display = display
		self.Javascript = Javascript
		self.divid = str(uuid.uuid4())
		self.textid = str(uuid.uuid4())
		self.pb = HTML(
				'<div style="border: 2px solid grey; width: 600px">\n  '
				f'<div id="{self.divid}" '
				'style="background-color: rgba(121,195,106,0.75); '
				'width:0%">&nbsp;</div>\n'
				'</div>\n'
				f'<p id="{self.textid}"></p>\n'
		)
		self.display(self.pb)
		super()._start(iterations, chunk_size)

	def update(self):
		self.n += 1
		n = self.n
		p = (n / self.N) * 100.0
		if p >= self.p_chunk:
			lbl = ("Elapsed time: %s. " % self.time_elapsed() +
			       "Est. remaining time: %s." % self.time_remaining_est(p))
			js_code = ("$('div#%s').width('%i%%');" % (self.divid, p) +
			           "$('p#%s').text('%s');" % (self.textid, lbl))
			self.display(self.Javascript(js_code))
			self.p_chunk += self.p_chunk_size

	def finished(self):
		self.t_done = time.time()
		lbl = "Elapsed time: %s" % self.time_elapsed()
		js_code = ("$('div#%s').width('%i%%');" % (self.divid, 100.0) +
		           "$('p#%s').text('%s');" % (self.textid, lbl))
		self.display(self.Javascript(js_code))


def tqdm_(iterable: Iterable,
		desc: str | Callable = None,
		total: int | float = None,
		disable: bool = False,
		unit: str = 'it',
		postfix: dict | Callable = None,
		**kwargs
):
	"""
	    Decorate an iterable object, returning an iterator which acts exactly
	    like the original iterable, but prints a dynamically updating
	    progressbar every time a value is requested.

	    Parameters
	    ----------
	    iterable  : iterable, optional
	        Iterable to decorate with a progressbar.
	        Leave blank to manually manage the updates.
	    desc  : str, optional
	        Prefix for the progressbar.
	    total  : int or float, optional
	        The number of expected iterations. If unspecified,
	        len(iterable) is used if possible. If float("inf") or as a last
	        resort, only basic progress statistics are displayed
	        (no ETA, no progressbar).
	        If `gui` is True and this parameter needs subsequent updating,
	        specify an initial arbitrary large positive number,
	        e.g. 9e9.
	    leave  : bool, optional
	        If [default: True], keeps all traces of the progressbar
	        upon termination of iteration.
	        If `None`, will leave only if `position` is `0`.
	    file  : `io.TextIOWrapper` or `io.StringIO`, optional
	        Specifies where to output the progress messages
	        (default: sys.stderr). Uses `file.write(str)` and `file.flush()`
	        methods.  For encoding, see `write_bytes`.
	    ncols  : int, optional
	        The width of the entire output message. If specified,
	        dynamically resizes the progressbar to stay within this bound.
	        If unspecified, attempts to use environment width. The
	        fallback is a meter width of 10 and no limit for the counter and
	        statistics. If 0, will not print any meter (only stats).
	    mininterval  : float, optional
	        Minimum progress display update interval [default: 0.1] seconds.
	    maxinterval  : float, optional
	        Maximum progress display update interval [default: 10] seconds.
	        Automatically adjusts `miniters` to correspond to `mininterval`
	        after long display update lag. Only works if `dynamic_miniters`
	        or monitor thread is enabled.
	    miniters  : int or float, optional
	        Minimum progress display update interval, in iterations.
	        If 0 and `dynamic_miniters`, will automatically adjust to equal
	        `mininterval` (more CPU efficient, good for tight loops).
	        If > 0, will skip display of specified number of iterations.
	        Tweak this and `mininterval` to get very efficient loops.
	        If your progress is erratic with both fast and slow iterations
	        (network, skipping items, etc) you should set miniters=1.
	    ascii  : bool or str, optional
	        If unspecified or False, use unicode (smooth blocks) to fill
	        the meter. The fallback is to use ASCII characters " 123456789#".
	    disable  : bool, optional
	        Whether to disable the entire progressbar wrapper
	        [default: False]. If set to None, disable on non-TTY.
	    unit  : str, optional
	        String that will be used to define the unit of each iteration
	        [default: it].
	    unit_scale  : bool or int or float, optional
	        If 1 or True, the number of iterations will be reduced/scaled
	        automatically and a metric prefix following the
	        International System of Units standard will be added
	        (kilo, mega, etc.) [default: False]. If any other non-zero
	        number, will scale `total` and `n`.
	    dynamic_ncols  : bool, optional
	        If set, constantly alters `ncols` and `nrows` to the
	        environment (allowing for window resizes) [default: False].
	    smoothing  : float, optional
	        Exponential moving average smoothing factor for speed estimates
	        (ignored in GUI mode). Ranges from 0 (average speed) to 1
	        (current/instantaneous speed) [default: 0.3].
	    bar_format  : str, optional
	        Specify a custom bar string formatting. May impact performance.
	        [default: '{l_bar}{bar}{r_bar}'], where
	        l_bar='{desc}: {percentage:3.0f}%|' and
	        r_bar='| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, '
	            '{rate_fmt}{postfix}]'
	        Possible vars: l_bar, bar, r_bar, n, n_fmt, total, total_fmt,
	            percentage, elapsed, elapsed_s, ncols, nrows, desc, unit,
	            rate, rate_fmt, rate_noinv, rate_noinv_fmt,
	            rate_inv, rate_inv_fmt, postfix, unit_divisor,
	            remaining, remaining_s, eta.
	        Note that a trailing ": " is automatically removed after {desc}
	        if the latter is empty.
	    initial  : int or float, optional
	        The initial counter value. Useful when restarting a progress
	        bar [default: 0]. If using float, consider specifying `{n:.3f}`
	        or similar in `bar_format`, or specifying `unit_scale`.
	    position  : int, optional
	        Specify the line offset to print this bar (starting from 0)
	        Automatic if unspecified.
	        Useful to manage multiple bars at once (eg, from threads).
	    postfix  : dict or *, optional
	        Specify additional stats to display at the end of the bar.
	        Calls `set_postfix(**postfix)` if possible (dict).
	    unit_divisor  : float, optional
	        [default: 1000], ignored unless `unit_scale` is True.
	    write_bytes  : bool, optional
	        Whether to write bytes. If (default: False) will write unicode.
	    lock_args  : tuple, optional
	        Passed to `refresh` for intermediate output
	        (initialisation, iterating, and updating).
	    nrows  : int, optional
	        The screen height. If specified, hides nested bars outside this
	        bound. If unspecified, attempts to use environment height.
	        The fallback is 20.
	    colour  : str, optional
	        Bar colour (e.g. 'green', '#00ff00').
	    delay  : float, optional
	        Don't display until [default: 0] seconds have elapsed.
	    gui  : bool, optional
	        WARNING: internal parameter - do not use.
	        Use tqdm.gui.tqdm(...) instead. If set, will attempt to use
	        matplotlib animations for a graphical output [default: False].

	    Returns
	    -------
	    out  : decorated iterator.
	    """

	if not callable(desc):
		desc_str = desc
		desc = lambda i: desc_str
	if not callable(postfix):
		postfix = lambda i: None

	if hasattr(iterable, '__len__'):
		total = len(iterable)

	pbar = tqdm(total=total, disable=disable, unit=unit, **kwargs)

	for i, iter in enumerate(iterable):
		pbar.set_description(desc(i))
		pbar.set_postfix(postfix(i))
		yield iter
		pbar.update(1)
