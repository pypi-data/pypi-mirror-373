# test_publisher_machine.py
import kipjak as kj

from test_api import *
from test_function import *

# A bare-bones, machine-based implementation of a published network service.
DEFAULT_NAME = 'acme'

class Publisher(kj.Point, kj.Stateless):
	def __init__(self, name: str=None):
		kj.Point.__init__(self)
		kj.Stateless.__init__(self)
		self.name = name or DEFAULT_NAME

def Publisher_Start(self, message):
	kj.publish(self, self.name)		# Register this object under the given name.

def Publisher_Xy(self, message):
	t = texture(self, x=message.x, y=message.y)
	m = kj.cast_to(t, table_type)
	self.reply(m)					# Respond to client.

def Publisher_Faulted(self, message):	# All faults routed here including
	self.complete(message)				# failure of publish().

def Publisher_Stop(self, message):
	self.complete(kj.Aborted())			# Leave all the housekeeping to the framework.

kj.bind(Publisher, (kj.Start, Xy, kj.Faulted, kj.Stop), entry_point=[Xy,])

if __name__ == '__main__':		# Process entry-point.
	kj.create(Publisher)
