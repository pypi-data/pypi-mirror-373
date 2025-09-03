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

"""Directory at the LAN scope.

Run the pub-sub name service at the LAN level.
"""
__docformat__ = 'restructuredtext'

import kipjak as kj

#
#
class INITIAL: pass
class RUNNING: pass
class CLEARING: pass

class Lan(kj.Threaded, kj.StateMachine):
	def __init__(self, directory_at_lan: kj.HostPort=None, encrypted_directory: bool=None):
		kj.Threaded.__init__(self)
		kj.StateMachine.__init__(self, INITIAL)
		self.directory_at_lan = directory_at_lan
		self.encrypted_directory = encrypted_directory

def Lan_INITIAL_Start(self, message):
	# Does not try to infer listening IP. Its either an argument or its all interfaces.
	accept_directories_at = self.directory_at_lan or kj.HostPort('0.0.0.0', kj.DIRECTORY_PORT)

	self.directory = self.create(kj.ObjectDirectory, directory_scope=kj.ScopeOfDirectory.LAN,
		accept_directories_at=accept_directories_at,
		encrypted=self.encrypted_directory)

	self.assign(self.directory, 1)
	return RUNNING

def Lan_RUNNING_Returned(self, message):
	f = kj.Faulted('directory terminated')
	self.complete(f)

def Lan_RUNNING_Faulted(self, message):
	self.abort(message)
	return CLEARING

def Lan_RUNNING_Stop(self, message):
	self.abort(kj.Aborted())
	return CLEARING

def Lan_CLEARING_Returned(self, message):
	self.complete(self.aborted_message)

LAN_DISPATCH = {
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

kj.bind(Lan, LAN_DISPATCH)

# For package scripting.
def main():
	kj.create(Lan)

if __name__ == '__main__':
	main()
