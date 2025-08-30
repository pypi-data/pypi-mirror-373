# object_startup_test.py
import kipjak as kj
import test_main

class Main(kj.Point, kj.Stateless):
	def __init__(self):
		kj.Point.__init__(self)
		kj.Stateless.__init__(self)
		self.temperature = 0
		self.timeout = 0

def Main_Start(self, message):
	t = kj.text_to_world('1963-03-26T02:24')
	a = self.create(kj.ProcessObject, test_main.main, b=32, c=99, t=t)

	def test_main_complete(self, value, _):
		self.complete(value)

	self.on_return(a, test_main_complete)

def Main_Returned(self, message):
	d = self.debrief()
	if isinstance(d, kj.OnReturned):
		d(self, message)

def Main_Stop(self, message):
	self.abort()

kj.bind(Main, dispatch=(kj.Start, kj.Returned, kj.Stop), return_type=kj.Any())

if __name__ == '__main__':
	kj.create(Main)
