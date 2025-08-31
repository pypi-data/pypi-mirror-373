# test_subscriber.py
import kipjak as kj

from test_api import *

# A bare-bones implementation of a client subscribing to a network service.
DEFAULT_SEARCH = 'acme'

def subscriber(self, search: str=None, enduring: bool=False) -> list[list[float]]:
	'''Open communications with a named service and exchange messages. Return table.'''
	search = search or DEFAULT_SEARCH

	kj.subscribe(self, search, scope=kj.ScopeOfDirectory.LAN)		# Connect this object with the named object.

	m = self.input()
	if isinstance(m, kj.Subscribed):		# Search registered with directory.
		pass

	elif isinstance(m, kj.Faulted):			# Any fault, e.g. NotSubscribed
		self.complete(m)

	# Run a live directory client. Framework notifications followed by
	# requests and responses.
	while True:
		m = self.input()

		if isinstance(m, kj.Available):		# Connected to the service.
			self.send(Xy(x=2, y=2), self.return_address)

		elif isinstance(m, list):			# Table.
			if enduring:
				continue
			self.complete(m)

		elif isinstance(m, kj.Dropped):		# Lost the server.
			continue

		elif isinstance(m, kj.Stop):
			self.complete(kj.Aborted())

kj.bind(subscriber)				# Register with framework.

if __name__ == '__main__':		# Process entry-point.
	kj.create(subscriber)
