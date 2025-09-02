import os
import platform
import subprocess
import shutil

move_file = os.rename
remove_file = os.remove


def natural_sort(seq, key=None, reverse=False, alg=None):
	"""
	Sorts an iterable naturally.

	Parameters
	----------
	seq : iterable
	    The input to sort.

	key : callable, optional
	    A key used to determine how to sort each element of the iterable.
	    It is **not** applied recursively.
	    It should accept a single argument and return a single value.

	reverse : {{True, False}}, optional
	    Return the list in reversed sorted order. The default is
	    `False`.

	alg : ns enum, optional
	    This option is used to control which algorithm `natsort`
	    uses when sorting. For details into these options, please see
	    the :class:`ns` class documentation. The default is `ns.INT`.

	Returns
	-------
	out: list
	    The sorted input.

	See Also
	--------
	natsort_keygen : Generates the key that makes natural sorting possible.
	realsorted : A wrapper for ``natsorted(seq, alg=ns.REAL)``.
	humansorted : A wrapper for ``natsorted(seq, alg=ns.LOCALE)``.
	index_natsorted : Returns the sorted indexes from `natsorted`.
	os_sorted : Sort according to your operating system's rules.

	Examples
	--------
	Use `natsorted` just like the builtin `sorted`::

	    >>> a = ['num3', 'num5', 'num2']
	    >>> natsorted(a)
	    ['num2', 'num3', 'num5']

	"""

	import natsort

	if alg is None:
		alg = natsort.ns.DEFAULT

	return natsort.natsorted(seq=seq, key=key, reverse=reverse, alg=alg)


def mkdirs(dirs, *args, **kwargs):
	"""
	Create (possibly multiple) directories

	Parameters
	----------
	dirs :
	args :
	kwargs :

	Returns
	-------

	"""

	kwargs = {"exist_ok": True} | kwargs

	os.makedirs(dirs, *args, **kwargs)


def rmdir(dir):
	try:
		os.rmdir(dir)
	except FileNotFoundError:
		pass


def copy(src, dst, overwrite=True, symlink=None):
	"""
	Copy file(s) or directories, or create symbolic links.

	Parameters
	----------
	src : str | list[str]
		Source file(s) or directory(ies).
	dst : str | list[str]
		- If 'src' is a string, 'dst' can be a target path or directory.
		- If 'src' is a list, 'dst' must be either a directory or a list of same length.
	overwrite : bool, default=True
		Overwrite destination if it exists.
	symlink : bool or None, default=None
		If True, create symbolic links instead of copying files/directories.
		If None, follow src's type (if `src` is a symlink, create a symlink; otherwise, copy).
	"""

	# convert to list
	if isinstance(src, str):
		src = [src]
	if isinstance(dst, str):
		dst = [dst]

	if len(src) == 1:  # src is a single file or directory
		if len(dst) > 1:
			raise ValueError("Cannot copy file/directory to multiple destinations.")
	else:  # len(src) > 1:
		if len(dst) == 1:  # dst is a directory
			dst = [os.path.join(dst[0], os.path.basename(s)) for s in src]
		else:  # dst is a list of destinations
			if len(src) != len(dst):
				raise ValueError("When copying multiple files, `dst` must be a list of the same length as `src`.")

	symlink = [symlink] * len(src)

	def create_symlink(src, dst, target_is_directory=False):
		"""Create a symbolic link to the source file or directory."""
		# Remove existing destination if exists
		if src == dst:
			raise ValueError("Source and destination cannot be the same.")
		if os.path.isdir(dst):
			raise ValueError(f"Directory '{dst}' is not empty.")
		elif os.path.exists(dst):
			os.remove(dst)

		os.symlink(src, dst, target_is_directory=target_is_directory)

	for s, d, lnk in zip(src, dst, symlink):
		if not overwrite and os.path.exists(d):  # Skip if not overwriting and destination exists
			continue

		if os.path.islink(s):  # If src is a symlink, resolve it
			s = os.readlink(s).replace("\\\\?\\", "")
			if lnk is True:
				pass
			elif lnk is None:
				lnk = True
			else:
				lnk = False
		if os.path.islink(d):  # If dst is a symlink, resolve it
			d = os.readlink(d).replace("\\\\?\\", "")

		if os.path.isdir(s):  # copy directory
			mkdirs(os.path.dirname(d))  # Ensure the parent directory exists
			if lnk:
				create_symlink(s, d, target_is_directory=True)
			else:
				shutil.copytree(s, d, dirs_exist_ok=True)  # Copy directory recursively

		elif os.path.isfile(s):  # copy file
			if not os.path.splitext(d)[1]:  # If destination is a directory (i.e., has no extension), append filename
				d = os.path.join(d, os.path.basename(s))
			mkdirs(os.path.dirname(d))  # Ensure the parent directory exists
			if lnk:
				create_symlink(s, d, target_is_directory=False)
			else:
				shutil.copy2(s, d)  # Copy file with metadata

		else:
			raise ValueError(f"Source {s} is neither a file nor a directory.")


def open_file(file):
	if platform.system() == "Windows":
		os.startfile(file)
	elif platform.system() == "Darwin":
		subprocess.Popen(["open", file])
	else:
		subprocess.Popen(["xdg-open", file])
