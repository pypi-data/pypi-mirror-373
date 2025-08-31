# test_echo.py
import kipjak as kj
from kipjak.listen_connect import *

import test_echo

def main(self, requested_ipp: kj.HostPort=None):
	requested_ipp = requested_ipp or kj.HostPort('127.0.0.1', 5010)

	self.console(requested_ipp=requested_ipp)

	echo = self.create(kj.ProcessObject, test_echo.main)

	self.start(kj.T1, 2.0)
	m, i = self.select(kj.T1, kj.Faulted, kj.Stop)

	connect(self, requested_ipp=kj.HostPort('127.0.0.1', 5010))
	m, i = self.select(Connected, kj.Faulted, kj.Stop)
	assert isinstance(m, Connected)
	server = self.return_address

	self.send(kj.Ack(), server)
	m, i = self.select(kj.Ack, kj.Faulted, kj.Stop)
	assert isinstance(m, kj.Ack)

	self.start(kj.T1, 5.0)
	self.select()

	self.send(Close(), server)
	m, i = self.select(Closed, kj.Faulted, kj.Stop)
	assert isinstance(m, Closed)

	self.send(kj.Stop(), echo)
	m, i = self.select(kj.Returned, kj.Faulted, kj.Stop)
	assert isinstance(m, kj.Returned)

kj.bind(main)

if __name__ == '__main__':
	kj.create(main)
