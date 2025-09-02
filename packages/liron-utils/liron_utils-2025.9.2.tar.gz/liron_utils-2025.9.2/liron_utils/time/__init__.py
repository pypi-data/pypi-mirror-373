from .base import *

TIME = get_time()  # time of Python console start
TIME_STR = get_time_str()  # time string of Python console start

__all__ = [s for s in dir() if not s.startswith('_')]
