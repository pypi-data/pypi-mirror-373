# test_publisher.py
import kipjak as kj

from test_api import *
from test_function import *

# A bare-bones implementation of a published network service.
DEFAULT_NAME = 'acme'

def publisher(self, name: str=None):
	'''Establish a named service, wait for clients and their enquiries. Return nothing.'''
	name = name or DEFAULT_NAME

	kj.publish(self, name, scope=kj.ScopeOfDirectory.LAN)		# Register this object under the given name.

	m = self.input()
	if isinstance(m, kj.Published):		# Name registered with directory.
		pass

	elif isinstance(m, kj.Faulted):		# Any fault, e.g. NotPublished.
		self.complete(m)

	# Run a live directory service. Framework notifications and
	# client requests.
	while True:
		m = self.input()
		if isinstance(m, (kj.Delivered, kj.Dropped)):	# Subscribers coming and going.
			continue

		elif isinstance(m, Xy):
			t = texture(self, x=m.x, y=m.y)
			m = kj.cast_to(t, table_type)
			self.reply(m)					# Respond to client.

		elif isinstance(m, kj.Stop):
			self.complete(kj.Aborted())

kj.bind(publisher)				# Register with framework.

if __name__ == '__main__':		# Process entry-point.
	kj.create(publisher)
