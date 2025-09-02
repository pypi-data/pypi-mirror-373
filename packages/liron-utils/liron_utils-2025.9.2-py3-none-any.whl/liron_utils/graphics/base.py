def hex2rgb(h):
	"""
	Convert hex color to RGB.

	Examples
	--------
	>>> hex2rgb("#FF5733")  # returns (255, 87, 51)

	Parameters
	----------
	h :             str or list of str
		Hex color string or list of hex color strings.

	Returns
	-------
	3-tuple or list of 3-tuples
	"""

	def hex2rgb_inner(h):
		return tuple(int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))

	if isinstance(h, str):
		return hex2rgb_inner(h)

	return [hex2rgb_inner(hh) for hh in h]


def rgb2hex(rgb):
	"""
	Convert RGB color to hex.
	Examples
	--------
	>>> rgb2hex((255, 87, 51))  # returns "#FF5733"

	Parameters
	----------
	rgb :           3-tuple or list of 3-tuples

	Returns
	-------
	str or list of str
	"""

	def rgb2hex_inner(rgb):
		rgb = [int(c, 16) for c in rgb * 255]
		return "#{:02x}{:02x}{:02x}".format(*rgb).upper()

	if len(rgb) == 3 and isinstance(rgb[0], int):
		return rgb2hex_inner(rgb)

	return [rgb2hex_inner(r) for r in rgb]
