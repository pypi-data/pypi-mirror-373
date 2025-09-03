# test_subscriber.py
import kipjak as kj

from test_api import *

# A bare-bones implementation of a client subscribing to a network service.
DEFAULT_SEARCH = 'acme'

class Subscriber(kj.Point, kj.Stateless):
	def __init__(self, search: str=None, seconds: float=None, enduring: bool=False):
		kj.Point.__init__(self)
		kj.Stateless.__init__(self)
		self.search = search or DEFAULT_SEARCH
		self.seconds = seconds
		self.enduring = enduring

def Subscriber_Start(self, message):
	kj.subscribe(self, self.search)		# Connect this object with the named object.
	if self.seconds is not None:
		self.start(kj.T1, 5.0)			# Expect resolution with a few seconds.

def Subscriber_Available(self, message):
	self.send(Xy(x=2, y=2), self.return_address)

def Subscriber_list_list_float(self, message):
	if self.enduring:
		return
	self.complete(message)

def Subscriber_T1(self, message):
	self.complete(kj.TimedOut(message))

def Subscriber_Faulted(self, message):		# All faults routed here including
	self.complete(message)					# failure of subscribe().

def Subscriber_Stop(self, message):
	self.complete(kj.Aborted())			# Leave all the housekeeping to the framework.

kj.bind(Subscriber, (kj.Start, kj.Available, table_type, kj.T1, kj.Faulted, kj.Stop), return_type=table_type)


if __name__ == '__main__':		# Process entry-point.
	kj.create(Subscriber)
