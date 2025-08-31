# test_main_return.py
import kipjak as kj

def main(self, return_an_int: bool=False, return_an_int_any: int=None):
	if return_an_int:
		return 42
	if return_an_int_any is not None:
		return (return_an_int_any, kj.Integer8())
	pass

kj.bind(main)

if __name__ == '__main__':
	kj.create(main)
