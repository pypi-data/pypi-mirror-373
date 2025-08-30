# test_main_args.py
import datetime
import uuid
import kipjak as kj

from test_person import *

class Catcher(kj.Point, kj.Stateless):
	def __init__(self, ):
		kj.Point.__init__(self)
		kj.Stateless.__init__(self)

def Catcher_Start(self, message):
	pass

def Catcher_dict_str_list_Person(self, message):
	person = []
	for v in message.values():
		for p in v:
			person.append(p.given_name)

	csv = ','.join(person)
	self.console(table=csv)

def Catcher_int(self, message):
	self.console(message=message)

def Catcher_float(self, message):
	self.console(message=message)

def Catcher_Person(self, message):
	self.console(person=message.given_name)

def Catcher_datetime(self, message):
	self.console(message=message)

def Catcher_UUID(self, message):
	self.complete()

kj.bind(Catcher, dispatch=(kj.Start,
	dict[str,list[Person]],
	int, float,
	Person,
	datetime.datetime,uuid.UUID))

#
table_type = kj.def_type(dict[str,list[Person]])

class Main(kj.Point, kj.Stateless):
	def __init__(self, table: dict[str,list[Person]]=None,
		count: int=10, ratio: float=0.5,
		who: Person=None, when: datetime.datetime=None,
		unique_id: uuid.UUID=None):
		kj.Point.__init__(self)
		kj.Stateless.__init__(self)
		self.table = table or dict(recent=[Person('Felicity'), Person('Frederic')])
		self.who = who or Person('Wilfred')
		self.when = when or kj.world_now()
		self.unique_id = unique_id or uuid.uuid4()
		self.count = count
		self.ratio = ratio

def Main_Start(self, message):
	j = self.create(Catcher)
	self.send(kj.cast_to(self.table, table_type), j)
	self.send(kj.cast_to(self.count, kj.int_type), j)
	self.send(kj.cast_to(self.ratio, kj.float_type), j)
	self.send(self.who, j)
	self.send(kj.cast_to(self.when, kj.datetime_type), j)
	self.send(kj.cast_to(self.unique_id, kj.uuid_type), j)

def Main_Returned(self, message):
	# Catcher terminates on receiving UUID.
	self.complete()

def Main_Stop(self, message):
	self.complete()

kj.bind(Main, dispatch=(kj.Start, kj.Returned, kj.Stop))

if __name__ == '__main__':
	kj.create(Main)
