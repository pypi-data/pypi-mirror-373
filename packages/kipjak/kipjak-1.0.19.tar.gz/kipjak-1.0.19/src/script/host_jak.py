# Author: Scott Woods <scott.suzuki@gmail.com>
# MIT License
#
# Copyright (c) 2025 Scott Woods
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Directory at the HOST scope.

Run the pub-sub name service at the HOST level.
"""
__docformat__ = 'restructuredtext'

import kipjak as kj

#
#
class INITIAL: pass
class RUNNING: pass
class CLEARING: pass

class Host(kj.Threaded, kj.StateMachine):
	def __init__(self, directory_at_host: kj.HostPort=None, directory_at_lan: kj.HostPort=None, encrypted_directory: bool=None):
		kj.Threaded.__init__(self)
		kj.StateMachine.__init__(self, INITIAL)
		self.directory_at_host = directory_at_host
		self.directory_at_lan = directory_at_lan
		self.encrypted_directory = encrypted_directory

def Host_INITIAL_Start(self, message):
	connect_to_directory = self.directory_at_lan
	accept_directories_at = self.directory_at_host or kj.DIRECTORY_AT_HOST

	self.directory = self.create(kj.ObjectDirectory, directory_scope=kj.ScopeOfDirectory.HOST,
		connect_to_directory=connect_to_directory,
		accept_directories_at=accept_directories_at,
		encrypted=self.encrypted_directory)

	self.assign(self.directory, 1)
	return RUNNING

def Host_RUNNING_Returned(self, message):
	f = kj.Faulted('directory terminated')
	self.complete(f)

def Host_RUNNING_Faulted(self, message):
	self.abort(message)
	return CLEARING

def Host_RUNNING_Stop(self, message):
	self.abort(kj.Aborted())
	return CLEARING

def Host_CLEARING_Returned(self, message):
	self.complete(self.aborted_message)

HOST_DISPATCH = {
	INITIAL: (
		(kj.Start,),
		()
	),
	RUNNING: (
		(kj.Returned, kj.Faulted, kj.Stop),
		()
	),
	CLEARING: (
		(kj.Returned,),
		()
	),
}

kj.bind(Host, HOST_DISPATCH)

# For package scripting.
def main():
	kj.create(Host)

if __name__ == '__main__':
	main()
