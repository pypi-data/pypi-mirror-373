# test_api.py
import kipjak as kj

class Xy(object):
	def __init__(self, x: int=1, y: int=1):
		self.x = x
		self.y = y

kj.bind(Xy)

table_type = kj.def_type(list[list[float]])
