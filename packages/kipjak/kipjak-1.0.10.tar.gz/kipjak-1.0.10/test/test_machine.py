#
#
import kipjak as kj

# MESSAGES ------------------------------------------------------------------------------
class Cook(object):
	def __init__(self, a: int=None, b: dict[int, str]=None, c=None):	# Cant hint here (-> int). Would annoy checkers.
		self.a = a
		self.b = b
		self.c = c

class Radiating(object):
	pass

kj.bind_message(Cook, c=kj.PointerTo(kj.Boolean))
kj.bind_message(Radiating)

# 1. List of args and their types and a return type, from function hints.
# 2. Still must be default callable (policy around persisted settings).
# 3. Types provided on bind when hints fall short.
'''
# POINT AS STATELESS MACHINE ------------------------------------------------------------
class DbQuery(kj.Point, kj.Stateless):
	def __init__(self, a: int=None, b: dict[int, str]=None, c=None):
		super().__init__()
		self.a = a
		self.b = b
		self.c = c

def DbQuery_Start(self, message):
	pass

def DbQuery_T1(self, message):
	pass

def DbQuery_Stop(self, message):
	self.complete()

kj.bind_stateless(DbQuery, (kj.Start, kj.T1, kj.Stop),
	return_type=dict[int, str],
	c=kj.TimeSpan())

# 1. List of args and their types, from __init__ function hints.
# 2. Dispatch table (list of received types) on bind.
# 3. Dispatch types should be hints where possible, Portable when not.
# 4. A return_type is passed to bind.
# 2. Still must be default callable (policy around persisted settings).
# 3. Types provided on bind when hints fall short.

# POINT AS FINITE-STATE MACHINE ---------------------------------------------------------
class INITIAL: pass
class IDLE: pass
class COOKING: pass

class Microwave(kj.Threaded, kj.StateMachine):
	def __init__(self, a: int=None, b: dict[int, str]=None, c=None):
		super().__init__(INITIAL)
		self.a = a
		self.b = b
		self.c = c
		self.temperature = 0
		self.timeout = 0

def Microwave_INITIAL_Start(self, message):
	return IDLE

def Microwave_IDLE_Cook(self, message):
	self.reply(Radiating())
	return COOKING

def Microwave_COOKING_Stop(self, message):
	self.complete(44)

kj.bind_stateful(Microwave,
	{
		INITIAL: (
			(kj.Start,),
			()
		),
		IDLE: (
			(Cook,),
			()
		),
		COOKING: (
			(kj.Stop,),
			()
		)
	},
	return_type=dict[int, str],
	c=kj.TimeSpan())


class Cook(object):
	def __init__(self, a: int=None, b: dict[int, str]=None, c=None):	# Cant hint here (-> int). Would annoy checkers.
kj.bind_message(Cook, c=kj.PointerTo(kj.Boolean))
BR_1 = kj.branch(int, dict[int, str], kj.Start)
def main(self, a: int=None, b: dict[int, str]=None, c=None) -> int:
	i, m = self.select(BR_1)
RT_2 = kj.register(dict[int, str])

def poly(self, a: int=None, b: dict[int, str]=None, c=None) -> kj.Any:	# Or typing.Any? NO - DIFFERENT
	b = b or {}

	isinstance(a, int)
	isinstance(b, dict)

	m, i = self.select(BR_1)
	if i == 0:
		return (0, RT_1)

	return ({'a':1}, RT_2)

class DbQuery(kj.Point, kj.Stateless):
	def __init__(self, a: int=None, b: dict[int, str]=None, c=None):

kj.bind_stateless(DbQuery, (kj.Start, kj.T1, kj.Stop),

class Microwave(kj.Threaded, kj.StateMachine):
	def __init__(self, a: int=None, b: dict[int, str]=None, c=None):
		super().__init__(INITIAL)

kj.bind_stateful(Microwave,
	{
		INITIAL: (
			(kj.Start,),
			()
		),

1. Message.__init__(self, a: int=None, b: dict[int, str]=None, c=None):
2. bind_message(Cook, c=kj.PointerTo(kj.Boolean)))
3. BR_1 = kj.branch(int, dict[int, str], kj.Start)
4. def main(self, a: int=None, b: dict[int, str]=None, c=None) -> int:
5. i, m = self.select(BR_1)
6. RT_2 = kj.register(dict[int, str])
7. def poly(self, a: int=None, b: dict[int, str]=None, c=None) -> kj.Any:
8. m, i = self.select(BR_1)
9. return ({'a':1}, RT_2)
10: class DbQuery(kj.Point, kj.Stateless): def __init__(self, a: int=None, b: dict[int, str]=None, c=None):
11: kj.bind_stateless(DbQuery, (kj.Start, kj.T1, kj.Stop), return_type=dict[str,int])
12: class Microwave(kj.Threaded, kj.StateMachine): def __init__(self, a: int=None, b: dict[int, str]=None, c=None):
13. kj.bind_stateful(Microwave,	{ INITIAL: ((kj.Start,), () ),


1. get_type_hints(Message.__init__) --------------------------- bind_message, hints to Portable, lookup/install
2. compile_schema(Message, c=kj.PointerTo(kj.Boolean))--------- compile_schema, if k in kw, override
3. def branch(*a)
4. get_type_hints(main) --------------------------------------- bind_function, hints to Portable, return type, lookup/install
5. BR_2 = kj.branch_table(dict[int, str]) --------------------- branch_table, hints to Portable, lookup/install, return tuple
6. i, m = self.branch(table-of-types) ------------------------- i, m = self.select(table), new input strategy for new type system
7. RT_2 = kj.return_type(dict[int, str]) ---------------------- RT = return_type(), hint to Portable, lookup/install
8. get_type_hints(Stateless.__init__) ------------------------- bind_stateless, hints to Portable, lookup/install
9. compile_schema(Stateless, c=kj.PointerTo(kj.Boolean)) ------ bind_stateless, return_type
10. get_type_hints(StateMachine.__init__) --------------------- bind_statemachine, hints to Portable, lookup/install
11. compile_schema(StateMachine, c=kj.PointerTo(kj.Boolean)) -- bind_statemachine, return_type
12. def main(self, b: dict[int, str]=None) -> int: ------------ argv -> codec -> settings, return -> codec -> stdout

13. self.select(int, Start, ...) ------------------------------ keep as easy-but-slow, for learning
'''
