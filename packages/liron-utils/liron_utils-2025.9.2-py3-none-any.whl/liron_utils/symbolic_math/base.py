import sympy


class SymExpr:

	def __init__(self, expression, subs_value=None, dev=None, units=None, info=None):
		"""

		Args:
			expression:
			subs_value:     dict {'x': 5, 'y': 6}
			dev:            dict{'x': .5, 'y': .6}
			units:          str
			info:           str
		"""

		self.expr = expression

		self.subs_value = subs_value
		self.dev = dev
		self.units = units
		self.info = info

	def __call__(self):
		return self.expr

	def subs(self, out_type=sympy.Expr):
		"""

		Args:
			out_type: sympy.Expr or str

		Returns:

		"""
		assert out_type in (sympy.Expr, str)
		value = self.expr
		dev = self.dev

		if isinstance(self.expr, sympy.Expr):
			if self.subs_value is None:
				print("No values to substitute.")
			else:
				value = self.expr.subs(self.subs_value)
				dev = self.calc_dev()

		if out_type is sympy.Expr:
			out = (value, dev)
		else:
			out = value.__str__()

			if dev is not None:
				out += f' +- {dev.__str__()}'

			if self.units is not None:
				out += f' [{self.units}]'

		return out

	def calc_dev(self, subs_value=True):
		gradient = dict()
		for sym in self.expr.free_symbols:
			gradient[sym] = self.expr.diff(sym)

		out = sympy.core.numbers.Zero()
		for sym in self.expr.free_symbols:
			if sym in self.dev.keys() and self.dev[sym] is not None:
				out += (gradient[sym] * self.dev[sym]) ** 2

		out = sympy.sqrt(out)

		if subs_value and self.subs_value is not None:
			out = out.subs(self.subs_value)

		return out

	def __str__(self):
		return f'{self.expr}, dev={self.dev}'

	def __repr__(self):
		return self.__str__()
