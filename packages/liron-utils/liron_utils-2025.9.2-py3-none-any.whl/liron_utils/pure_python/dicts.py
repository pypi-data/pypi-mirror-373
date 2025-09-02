from collections import OrderedDict
import threading
import pandas as pd


class dict_(dict):
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__


def DL_to_LD(DL: dict) -> list:
	"""
	Convert dict of lists to list of dicts

	Args:
		DL ():      Dict of lists

	Returns:

	"""

	try:
		LD = pd.DataFrame(DL).to_dict(orient="records")
	except ValueError:  # If dict values are scalars
		LD = None

	return LD


def LD_to_DL(LD: list) -> dict:
	"""
	Convert list of dicts to dict of lists

	Args:
		LD ():      List of dicts

	Returns:

	"""

	DL = pd.DataFrame(LD).to_dict(orient="list")
	return DL


class NamedQueue:
	def __init__(self, max_size=0):
		"""Thread-safe queue with a maximum size.
		If the queue is full, the oldest item is removed when a new item is added."""
		self.maxsize = max_size
		self.queue = OrderedDict()
		self._lock = threading.Lock()

	def enqueue(self, name, item):
		"""Add an item to the queue. If the queue is full, remove the oldest item."""
		with self._lock:
			if name in self.queue:  # item already exists
				del self.queue[name]
			elif 0 < self.maxsize <= len(self.queue):  # queue is full
				self.queue.popitem(last=False)  # FIFO order
			self.queue[name] = item  # add new item

	def dequeue(self):
		"""Remove and return the oldest item from the queue. If the queue is empty, return None."""
		with self._lock:
			if self.queue:  # queue is not empty
				return self.queue.popitem(last=False)
			return None

	def remove(self, name):
		"""Remove an item from the queue by its name."""
		with self._lock:
			return self.queue.pop(name)

	def update(self, name, item):
		"""Update an item in the queue by its name. If the item does not exist, it is added."""
		with self._lock:
			if name in self.queue:
				self.queue[name] = item
			else:
				self.enqueue(name, item)

	def __contains__(self, name):
		"""Check if an item with the given name is in the queue."""
		with self._lock:
			return name in self.queue

	def __len__(self):
		return len(self.queue)

	def __getitem__(self, name):
		"""Get an item from the queue by its name."""
		with self._lock:
			return self.queue[name]

	def __repr__(self):
		"""Return a string representation of the queue."""
		with self._lock:
			return f"Queue({list(self.queue.items())})"

	def __iter__(self):
		"""Return an iterator over the queue."""
		with self._lock:
			return iter(self.queue.items())

	def __next__(self):
		"""Return the next item in the queue."""
		with self._lock:
			if self.queue:
				return self.queue.popitem(last=False)
			else:
				raise StopIteration

	def keys(self):
		"""Return the keys of the queue."""
		with self._lock:
			return self.queue.keys()

	def values(self):
		"""Return the values of the queue."""
		with self._lock:
			return self.queue.values()

	def items(self):
		"""Return the items of the queue."""
		with self._lock:
			return self.queue.items()

	def clear(self):
		"""Clear the queue."""
		with self._lock:
			self.queue.clear()
