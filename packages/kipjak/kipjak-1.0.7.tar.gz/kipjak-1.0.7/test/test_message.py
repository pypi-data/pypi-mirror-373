#
#
import uuid
import kipjak as kj

from enum import Enum

__all__ = [
	'AutoTypes',
	'PlainTypes',
	'ContainerTypes',
	'SpecialTypes',
	'TimeTypes',
	'PointerTypes',
	'Item',
	'Brackets',
	'Letter',
	'Question',
	'Plus',
	'Parentheses',
	'Cat',
	'State',
	'MACHINE_STATE',
	'encode_decode'
]

#
#
class AutoTypes(object):
	def __init__(self, a=True, b=42, c=1.234,
			d=bytearray('Hello in bytes', 'ascii'),
			e=b'Hello in chars', f='Hello in codepoints', g=uuid.uuid4()):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.e = e
		self.f = f
		self.g = g

kj.bind_message(AutoTypes)

#
#
class MACHINE_STATE(Enum):
	INITIAL=1
	NEXT=2

class PlainTypes(object):
	def __init__(self, a=None, b=None, c=None, d=None, e=None,
			f=None, g=None, h=None, i=None, j=None, k=None,
			l=None, m=None, n=None, o=None, p=None, q=None):
		self.a = a or True
		self.b = b or int()
		self.c = c or bytes()
		self.d = d or str()
		self.e = e or int()
		self.f = f or int()
		self.g = g or int()
		self.h = h or int()
		self.i = i or int()
		self.j = j or int()
		self.k = k or float()
		self.l = l or float()
		self.m = m or bytearray()
		self.n = n or bytes()
		self.o = o or str()
		self.p = p or MACHINE_STATE.INITIAL
		self.q = q or uuid.uuid4()

kj.bind_message(PlainTypes,
	a=kj.Boolean(),
	b=kj.Byte(),
	c=kj.Character(),
	d=kj.Rune(),
	e=kj.Integer2(),
	f=kj.Integer4(),
	g=kj.Integer8(),
	h=kj.Unsigned2(),
	i=kj.Unsigned4(),
	j=kj.Unsigned8(),
	k=kj.Float4(),
	l=kj.Float8(),
	m=kj.Block(),
	n=kj.String(),
	o=kj.Unicode(),
	p=kj.Enumeration(MACHINE_STATE),
	q=kj.UUID(),
)

#
#
class ContainerTypes(object):
	def __init__(self, a=None, b=None, c=None, d=None, e=None,
			f=None, g=None, h=None, i=None, j=None, k=None, l=None):
		self.a = a or [bytes()] * 8
		self.b = b or [1.0, 1.1, 1.2]
		self.c = c or set([1, 2, 4, 8, 16])
		self.d = d or {"left": "right", "up": "down", "in": "out"}
		self.e = e or kj.deque([4, 5, 6])
		self.f = f or PlainTypes()
		self.g = g or [[bytes()] * 4] * 4
		self.h = h or [[2.0, 2.1, 2.2], [3.0, 3.1, 3.2], [4.0, 4.1, 4.2]]
		self.i = i or {42: {"LEFT": "RIGHT", "UP": "DOWN"}}
		self.j = j or kj.deque([kj.deque([14, 15, 16]), kj.deque([]), kj.deque([24, 25, 26])])
		self.k = k or [[bytes()]] * 4
		self.l = l or [[AutoTypes()] * 2]

kj.bind_message(ContainerTypes,
	a=kj.ArrayOf(kj.String, 8),
	b=kj.VectorOf(kj.Float8),
	c=kj.SetOf(kj.Integer8),
	d=kj.MapOf(kj.Unicode, kj.Unicode),
	e=kj.DequeOf(kj.Integer2),
	f=kj.UserDefined(PlainTypes),

	g=kj.ArrayOf(kj.ArrayOf(kj.String, 4), 4),
	h=kj.VectorOf(kj.VectorOf(kj.Float8)),
	i=kj.MapOf(kj.Integer8, kj.MapOf(kj.Unicode, kj.Unicode)),
	j=kj.DequeOf(kj.DequeOf(kj.Integer2)),
	k=kj.ArrayOf(kj.VectorOf(kj.String), 4),
	l=kj.VectorOf(kj.ArrayOf(kj.UserDefined(AutoTypes), 2)),
)

#
#
auto_types = kj.def_type(AutoTypes)
plain_types = kj.def_type(PlainTypes)

class SpecialTypes(object):
	def __init__(self, a=None, b=None, c=None, d=None, e=None, f=None):
		self.a = a or PlainTypes
		self.b = b or (3, 5, 7)	 # Will lose the 7.
		self.c = c or (2, 4, 6)	 # Add the return_proxy
		self.d = d
		self.e = {'auto': AutoTypes, 'plain': PlainTypes}
		self.f = f or []

kj.bind_message(SpecialTypes,
	a=kj.Type(),
	b=kj.TargetAddress(),
	c=kj.Address(),
	d=kj.Any(),
	e=kj.MapOf(kj.Unicode(), kj.Type()),
	f=kj.VectorOf(kj.Type()),
)

class TimeTypes(object):
	def __init__(self, a=None, b=None, c=None, d=None):
		self.a = a or kj.text_to_clock('2021-07-01T03:02:01.0')
		self.b = b or kj.text_to_span('1d2h3m4.5s')
		self.c = c or kj.text_to_world('2021-07-01T03:02:01.0+01:00')
		self.d = d or kj.text_to_delta('7:00:00:00')

kj.bind_message(TimeTypes,
	a=kj.ClockTime(),
	b=kj.TimeSpan(),
	c=kj.WorldTime(),
	d=kj.TimeDelta(),
)

#
#
class Item(object):
	def __init__(self, tag=None, next=None):
		self.tag = tag or '<blank>'
		self.next = next

kj.bind_message(Item,
	tag=kj.Unicode,
	next=kj.PointerTo(Item),
)

#
#
def linked(*tag):
	p = None
	for s in reversed(tag):
		i = Item(s, p)
		p = i
	return p

def circle(*tag):
	p = None
	t = None
	for s in reversed(tag):
		i = Item(s, p)
		if p is None:
			t = i
		p = i
	if p is not None:
		t.next = p
	return p

# Different elements of an abstract syntax
# tree.
class Brackets(object):
	def __init__(self, range=None):
		self.range = range

kj.bind_message(Brackets, range=kj.Unicode)

class Cat(object):
	def __init__(self, left=None, right=None):
		self.left = left
		self.right = right

kj.bind_message(Cat,
	left=kj.PointerTo(kj.Any),
	right=kj.PointerTo(kj.Any),
)

class Letter(object):
	def __init__(self, lone=None):
		self.lone = lone

kj.bind_message(Letter, lone=kj.Unicode)

class Question(object):
	def __init__(self, optional=None):
		self.optional = optional

kj.bind_message(Question, optional=kj.PointerTo(kj.Any))

class Plus(object):
	def __init__(self, one_or_more=None):
		self.one_or_more = one_or_more

kj.bind_message(Plus, one_or_more=kj.PointerTo(kj.Any))

class Parentheses(object):
	def __init__(self, expression=None):
		self.expression = expression

kj.bind_message(Parentheses, expression=kj.PointerTo(kj.Any))

# Parse of the following regular expression;
# [0-9]+(\.[0-9]+)?
tree = Cat(Plus(Brackets('0123456789')), Question(Cat(Letter('.'), Plus(Brackets('0123456789')))))

# Graph representation of the above AST, i.e. contains the information
# that can be used to generate transition tables.
SERIAL_ID = 1

class State(object):
	def __init__(self, number=None, edge=None):
		global SERIAL_ID
		if number is None:
			number = SERIAL_ID
			SERIAL_ID += 1
		self.number = number
		self.edge = edge or {}

kj.bind_message(State,
	number=kj.Integer8,
	edge=kj.MapOf(kj.Unicode, kj.PointerTo(State)),
)

# Build the state/edge representation for the AST above, i.e. a
# graph with pointers that can refer to any state in the network.
# In this case that includes edges referring to self and edges
# that take a shortcut to the end. Note that for simplicity of
# this example, only the edges for the 0 digit are created.
accept = State()

fraction = State(edge={'0': State(edge={None: accept})})
fraction.edge['0'].edge['0'] = fraction.edge['0']

digits = State(edge={'0': State(edge={None: accept})})
digits.edge['0'].edge['0'] = digits.edge['0']
digits.edge['0'].edge['.'] = fraction

graph = digits
#
#
class PointerTypes(object):
	def __init__(self, a=None, b=None, c=None,
			d=None, e=None, f=None, g=None):
		self.a = a or bool()
		self.b = b or self.a
		self.c = c or PlainTypes()
		self.d = d or linked('a', 'b', 'c', 'd', 'e')
		self.e = e or circle('X', 'Y', 'Z')
		self.f = f or tree
		self.g = g or graph

kj.bind_message(PointerTypes,
	a=kj.PointerTo(kj.Boolean),
	b=kj.PointerTo(kj.Boolean),
	c=kj.PointerTo(kj.UserDefined(PlainTypes)),
	d=kj.PointerTo(Item),	  # Linked using next
	e=kj.PointerTo(Item),	  # Linked using next and looped to start
	f=kj.PointerTo(kj.Any),	# AST for regular expression
	g=kj.PointerTo(State),	 # Graph for state machine
)

#
#
def encode_decode(c, test):
		t = kj.UserDefined(test)
		r = kj.make(t)

		try:
			s = c.encode(r, t)
		except kj.CodecError as e:
			print(e.note)
			return False

		# Recover the application data from the given
		# shipment.
		try:
			b = c.decode(s, t)
		except kj.CodecError as e:
			print(e.note)
			return False

		return kj.equal_to(b, r)
