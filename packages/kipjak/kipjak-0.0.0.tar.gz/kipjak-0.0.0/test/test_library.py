# test_library.py
import kipjak as kj

from test_api import *
from test_function import *


def library(self):
	'''Provide an API to the framework. Return nothing.'''

	# The process runs until it receives a Stop.
	while True:
		m = self.input()

		if isinstance(m, Xy):				# Expected request.
			pass
		elif isinstance(m, kj.Faulted):		# Any fault.
			return m
		elif isinstance(m, kj.Stop):		# Terminate, e.g. control-c.
			return kj.Aborted()
		else:
			continue

		# Process the framework request.
		# Commits the entire process to the function call.
		table = texture(self, x=m.x, y=m.y)
		self.send(kj.cast_to(table, table_type), self.return_address)

kj.bind(library, entry_point=[Xy,])		# Register with the framework. Declare the API.

if __name__ == '__main__':		# Process entry-point.
	kj.create(library)
