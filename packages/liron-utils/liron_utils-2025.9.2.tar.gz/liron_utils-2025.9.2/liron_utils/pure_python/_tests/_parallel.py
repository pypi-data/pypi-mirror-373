import time
from tqdm import tqdm
from liron_utils.pure_python import parallel


def foo(i, x, y):
	time.sleep(0.1)
	return i


def no_parallel(func, iterable, **kwargs) -> list:
	"""Run a function on an iterable without parallelization."""
	return [func(i, **kwargs) for i in tqdm(iterable)]


if __name__ == '__main__':
	for par_func in [parallel.parallel_map, parallel.parallel_threading]:
		t0 = time.time()
		out = par_func(func=foo, iterable=range(500), x=1, y=2,
				tqdm_kw=dict(desc=par_func.__name__, postfix=lambda i: dict(iter=i)))
		print(out[:5])
		print(f"{par_func.__name__} time: {time.time() - t0:.3f} sec")
		time.sleep(0.1)

	"""
	Results:
	--------
	len(iterable)	                    | 100   | 1000  | 10000 |
	parallel_map                        | 4.0   | 10.2  | 72.7  | [sec]
	parallel_threading (10 threads)     | 1.1   | 11.1  | 111.2 | [sec]
	"""
	pass
