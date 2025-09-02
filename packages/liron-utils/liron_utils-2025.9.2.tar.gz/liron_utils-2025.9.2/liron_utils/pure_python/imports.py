import os
import sys


def import_module(file_name):
	"""
	Import a module/file into Python session.


	Args:
		file_name:   file name

	Returns:

	"""
	dir, file_name = os.path.split(file_name)
	sys.path.append(dir)
	h = __import__(file_name)
	sys.path.pop(-1)
	return h
