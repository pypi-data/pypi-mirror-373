# test_library_machine.py
import kipjak as kj

from test_api import *
from test_function import *

# A bare-bones, machine implementation
# of test_library.py.
class Library(kj.Threaded, kj.Stateless):
	def __init__(self):
		kj.Threaded.__init__(self)
		kj.Stateless.__init__(self)

def Library_Start(self, message):
	pass

def Library_Xy(self, message):
	table = texture(self, x=message.x, y=message.y)
	self.send(kj.cast_to(table, table_type), self.return_address)

def Library_Stop(self, message):
	self.complete(kj.Aborted())

kj.bind(Library, (kj.Start, Xy, kj.Stop), entry_point=[Xy,])

if __name__ == '__main__':
	kj.create(Library)
