# test_echo.py
import kipjak as kj

def main(self, requested_ipp: kj.HostPort=None):
	requested_ipp = requested_ipp or kj.HostPort('127.0.0.1', 5010)

	self.console(requested_ipp=requested_ipp)

	# Establish the network listen.
	kj.listen(self, requested_ipp=requested_ipp)
	m, i = self.select(kj.Listening, kj.NotListening, kj.Stop)
	if i == 1:
		return m
	if i == 2:
		return kj.Aborted()

	# Errors, sessions and inbound client messages.
	while True:
		m, i = self.select(kj.NotListening,		# Listen failed.
			kj.Accepted, kj.Closed,				# Session notifications.
			kj.Stop,							# Intervention.
			kj.Unknown)							# An inbound message.

		if i == 0:				# Terminate with the fault.
			break
		elif i in (1, 2):		# Ignore.
			continue
		elif i == 3:			# Terminate as requested.
			m = kj.Aborted()
			break

		rt = type(self.received_type)
		self.console(typ=rt)
		if rt == kj.UserDefined:
			self.console(element=self.received_type.element)
		c = kj.cast_to(m, self.received_type)	# Send the message back over the connection.
		self.reply(c)

	return m

kj.bind(main, entry_point=(kj.Ack, kj.Enquiry))

if __name__ == '__main__':
	kj.create(main)
