# test_echo.py
import kipjak as kj
import test_library

def main(self):
	echo = self.create(kj.ProcessObject, test_library.main)		# Load the library process.

	self.send(kj.Ack(), echo)									# Request and
	m, i = self.select(kj.Ack, kj.Faulted, kj.Stop)			# response.
	assert isinstance(m, kj.Ack)

	m, i = self.select()			# response.
	return kj.Aborted()

	# Optional housekeeping.
	# self.send(kj.Stop(), echo)									# Unload the library.
	# m, i = self.select(kj.Returned, kj.Faulted, kj.Stop)		# Gone.
	# assert isinstance(m, kj.Returned)

kj.bind(main)

if __name__ == '__main__':
	kj.create(main)
