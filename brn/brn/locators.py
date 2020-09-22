from typing import Any

class Locator:
	def __init__(self, value:Any):
		self.value = value

	def __repr__(self):
		return self.__class__.__name__ + '(' + repr(self.value) + ')'


class Path(Locator):
	pass
class AbsPath(Path):
	pass
