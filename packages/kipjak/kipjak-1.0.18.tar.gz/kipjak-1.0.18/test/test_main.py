# test_main.py
import kipjak as kj

def main(self, message: str=None):
	message = message or 'Hello world'
	self.console(message)

kj.bind(main)

if __name__ == '__main__':
	kj.create(main)
