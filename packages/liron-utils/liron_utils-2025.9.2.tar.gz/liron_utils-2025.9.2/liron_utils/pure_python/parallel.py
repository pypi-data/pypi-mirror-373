import warnings
import sys
import functools
import multiprocessing as mp
import threading
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .progress_bar import tqdm_

NUM_CPUS = mp.cpu_count()
NUM_PROCESSES_TO_USE = NUM_CPUS
NUM_THREADS_TO_USE = 20


def parallel_map(func: callable,
		iterable: Iterable,
		callback=None,
		error_callback=None,
		num_processes: int = NUM_PROCESSES_TO_USE,
		tqdm_kw=None,
		**kwargs) -> list:
	"""
	Run function 'func' in parallel.
	See qutip.parallel.parallel_map for reference.

	Notes
	-----
	- 'func' must be a global function (can't be nested inside another function).
	- parallel_map uses 'spawn' [1,2] by default in Windows, which starts a Python child process from scratch.
	  This means that everything not under an 'if __name__==__main__' block will be executed multiple times.
	- In UNIX we use 'fork'.

	References
	----------
	[1] https://stackoverflow.com/questions/64095876/multiprocessing-fork-vs-spawn/66113051#66113051
	[2] https://stackoverflow.com/questions/72935231/statements-before-multiprocessing-main-executed-multiple-times-python
	[3] https://superfastpython.com/multiprocessing-pool-issue-tasks

	Examples
	--------
	>>> import time
	>>> def func(iter, x, y):
	>>> 	time.sleep(1)
	>>> 	return (x + y) ** iter
	>>>
	>>> if __name__ == '__main__':
	>>> 	x = 1
	>>> 	y = 2
	>>> 	t0 = time.time()
	>>> 	out = parallel_map(func=func, iterable=range(100), num_processes=8, x=x, y=y)
	>>> 	print(out[:5])
	>>> 	print(f"time: {time.time() - t0}sec")

	Notes
	-----
	- If you get UserWarning: Can't pickle local object 'func.<locals>.func_partial', try to define 'func' in
	  the global scope.

	Parameters
	----------
	func :              callable
						The function to evaluate in parallel. The first argument is the changing value of each iteration
	iterable :          array_like
						First input argument for 'func'
	callback :          callable
						function to call after each iteration is done
	error_callback :    callable
						function to call if an error occurs
	num_processes :     int
						number of processes to use
	progress_bar :     bool
						if True, show a progress bar using tqdm
	desc :              str
						description for tqdm
	postfix :           callable
						postfix for tqdm description. If callable, should return a dict.
	tqdm_kw :           dict
						kwargs for tqdm.
	kwargs :            passed to func

	Returns
	-------
	list of 'func' outputs, organized by the order of 'iter'.

	"""
	if sys.platform == 'darwin':  # in UNIX 'fork' can be used (faster but more dangerous)
		Pool = mp.get_context('fork').Pool
	else:  # In Windows only 'spwan' is available
		Pool = mp.Pool
		mp.Process()

	if num_processes > NUM_CPUS:
		warnings.warn(f"Requested number of processes {num_processes} is larger than number of CPUs {NUM_CPUS}.\n"
		              f"For better performance, consider reducing 'num_processes'.", category=UserWarning)
	num_processes = min(num_processes, NUM_CPUS, len(iterable))

	with Pool(processes=num_processes) as pool:
		func_partial = functools.partial(func, **kwargs)  # pass kwargs to func

		out_async = [pool.apply_async(
				func=func_partial,
				args=(i,),
				callback=callback,
				error_callback=error_callback
		) for i in iterable]

		out = []

		for out_async_i in tqdm_(out_async, **tqdm_kw):
			try:
				out += [out_async_i.get()]

			except KeyboardInterrupt as e:
				raise e

			except Exception as e:
				warnings.warn(f"Exception at index {out_async_i}: {e}")

	return out


def parallel_threading(func: callable,
		iterable: Iterable,
		lock: bool = False,
		num_threads: int = NUM_THREADS_TO_USE,
		tqdm_kw=None,
		**kwargs) -> list:
	"""
	Run function 'func' in parallel using threads.

	Parameters
	----------
	func :          callable
					The function to evaluate using threads. The first argument is the changing value of each iteration.
	iterable :      array_like
					First input argument for 'func'
	lock :          bool
					Use a lock to prevent concurrent access to shared resources.
	num_threads :   int
					Number of threads to use.
	progress_bar : bool
					If True, show a progress bar using tqdm.
	desc :          str or callable
					Description for tqdm. If callable, should return a string.
	postfix :       callable
					Postfix for tqdm description. If callable, should return a dict.
	tqdm_kw :       dict
					kwargs for tqdm.
	kwargs :        Passed to func.

	Returns
	-------
	List of 'func' outputs, organized by the order of 'iterable'.
	"""
	if lock:
		lock = threading.Lock()

	def wrapped_func(index, item):
		try:
			if lock:
				with lock:
					result = func(item, **kwargs)
			else:
				result = func(item, **kwargs)
			return index, result
		except Exception as e:
			warnings.warn(f"Exception at index {index}: {e}")
			return index, None

	out = [None] * len(iterable)
	with ThreadPoolExecutor(max_workers=num_threads) as executor:
		futures = [executor.submit(wrapped_func, i, item) for i, item in enumerate(iterable)]

		if tqdm_kw is None:
			tqdm_kw = dict()
		tqdm_kw = dict(total=len(futures)) | tqdm_kw

		for future in tqdm_(as_completed(futures), **tqdm_kw):
			index, result = future.result()
			out[index] = result

	return out
