# object_startup_test.py
import datetime
import kipjak as kj

from test_person import *

table_Person_type = kj.def_type(kj.VectorOf(kj.VectorOf(kj.UserDefined(Person))))
table_world_type = kj.def_type(kj.VectorOf(kj.VectorOf(kj.WorldTime())))

def main(self, height: int=4, width: int=4, who: Person=None, when: datetime.datetime=None):
	self.console(f'width: {width}, height: {height}')

	if height < 1 or height > 1000 or width < 1 or width > 1000:
		return kj.Faulted(f'out of bounds')

	if who:
		table = [[who] * width] * height
		return kj.cast_to(table, table_Person_type)

	if when:
		table = [[when] * width] * height
		return kj.cast_to(table, table_world_type)

	return (True, kj.Boolean())

kj.bind(main, return_type=kj.Any())

if __name__ == '__main__':
	kj.create(main)
