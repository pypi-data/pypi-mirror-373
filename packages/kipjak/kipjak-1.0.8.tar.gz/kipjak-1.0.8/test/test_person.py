# object_startup_test.py
import kipjak as kj


class Person(object):
	def __init__(self, given_name: str=None):
		self.given_name = given_name

kj.bind(Person)
