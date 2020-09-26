
class Dotdict:
	"""
	Wraps a dict and allows access by both attributes and index.
	The semantic is such that only keys not beginning with an underscore are allowed.
	for example: ch = Dotdict(); ch._dict = {a:1}; ch.a = ch[a] + 1
	Furthermore, calling _lock() puts the object in a "locked" state, which causes it to throw an error when setting a key which is not already present.
	"""
	def __init__(s, seq=[], **kwargs):
		object.__setattr__(s, "_dict", dict(seq, **kwargs))
		object.__setattr__(s, "_locked", False)

	def _lock(s):
		object.__setattr__(s, "_locked", True)

	def __setattr__ (s, k, v):
		if object.__getattribute__(s, "_locked"):
			if not k in s._dict:
				raise Exception("setting an unknown item of a locked-down Dotdict")
		if k != "_dict":
			if k.startswith('_'):
				raise Exception("keys starting with an underscore are not allowed")
			s._dict[k] = v
		else:
			object.__setattr__(s, "_dict", v)

	def __getattr__ (s, k):
		if k.startswith('_'):
			return super().__getattr__(k)
		else:
			try:
				return s._dict[k]
			except KeyError:
				raise AttributeError()

	def __setitem__(s, k, v):
		s._dict[k] = v

	def __getitem__ (s, k):
		return s._dict[k]

	def __repr__(s):
		return 'Dotdict('+s._dict.__repr__()+')'

	def __len__(s):
		return len(s._dict)



"""

# alternatives:

## subclassing a dict
inherits many atributtes, do not want.


## with SimpleNamespace:

	python 3.3 introduces SimpleNamespace, equivalent to an empty object with nice __repr__.
	could use that and just add __getitem__ and __setitem__ (access by index)
	and locking, locking is useful.
	see:
	https://docs.python.org/3/library/types.html#types.SimpleNamespace


from types import SimpleNamespace

but i dont want _locked to be in the dict. give up on locking, or ..??

class Dotdict(SimpleNamespace):
	def __init__(s, **kwargs):
		super().__init__(**kwargs)
		object.__setattr__(s, "_locked", False)
	def _lock(s):
		object.__setattr__(s, "_locked", True)
	def __setattr__ (s, k, v):
		if s._locked:
			if not k in s.__dict__:
				raise Exception("setting an unknown item of a locked-down Dotdict")
		s.__dict__[k] = v

	def __setitem__(s, k, v):
		s.__dict__[k] = v
	def __getitem__ (s, k):
		return s.__dict__[k]
	def __len__(s):
		return len(s.__dict__)
	@property
	def _dict(s):
		return s.__dict__



## https://docs.python.org/3/library/collections.html#collections.namedtuple


## others:

there is a couple of other "dotdict"-like things on pypi.



"""
