# object_startup_test.py
import kipjak as kj
import test_main

def main(self):
	t = kj.text_to_world('1963-03-26T02:24')
	a = self.create(kj.ProcessObject, test_main.main, b=32, c=99, t=t)
	m, i = self.select(kj.Returned, kj.Stop)
	if isinstance(m, kj.Returned):
		return m.message					# Return type of main must match test_main.main.
	self.send(m, a)
	self.select(kj.Returned)
	return kj.Aborted()

kj.bind(main, return_type=kj.Any())

if __name__ == '__main__':
	kj.create(main)
