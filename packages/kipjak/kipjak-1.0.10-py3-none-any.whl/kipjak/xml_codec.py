# Author: Scott Woods <scott.suzuki@gmail.com>
# MIT License
#
# Copyright (c) 2017-2023 Scott Woods
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

"""Implementation of the XML codec.

The plug-in part of the encoding/decoding stack and the default. Involves
two functions that transform between the internal, flattened memory
representation and the actual encoding. With a little luck there is not
much more to do than call the read/write, or load/save methods on the
encoding-specific parser module.

* word_to_xml - generate the JSON representation of an application word.
* xml_to_word - recovers an application word from a JSON representation.

Also refer to;

* https://www.w3.org/XML/
* https://en.wikipedia.org/wiki/XML
"""

__docformat__ = 'restructuredtext'

# .. autoclass:: CodecXml
# .. autofunction:: word_to_xml
# .. autofunction:: xml_to_word

import base64
import uuid
import types
import io

#
#
from defusedxml.ElementTree import fromstring, ParseError
from defusedxml import DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden

from xml.dom import minidom

from .virtual_memory import *
from .convert_memory import *
from .virtual_runtime import *
from .message_memory import *
from .virtual_codec import *

__all__ = [
	'word_to_xml',
	'xml_to_word',
	'CodecXml'
]

# Code fragment per generic type, for output
# of pretty_format XML.

# Output a simple XML element - bool, int, float.
def name_value_pretty(c, tag, name, value, tabs):
	r = c.representation
	tab = c.find_tab(tabs)
	r.write(tab)
	r.write('<')
	r.write(tag)
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	if value:
		r.write(' value="')
		r.write(value)
		r.write('"')
	r.write('/>\n')

# Output of an ansar String or Unicode. Special XML
# characters need escaping and XML does not do
# non-ascii completely.
ampersand = {
	'&': '&amp;',
	'<': '&lt;',
	'>': '&gt;',
	'\'': '&apos;',
	'"': '&quot;',
}

# Printables according to
# XML specs.
xml_printing = set()

xml_printing.add(9)	# TAB
xml_printing.add(10)   # LF
xml_printing.add(13)   # CR

# From space to tilde, i.e. 127
# below is exclusive boundary.
for i in range(32, 127):
	xml_printing.add(i)

# Remove the tag/escape chars.
for k, v in ampersand.items():
	i = ord(k)
	xml_printing.discard(i)

def escaped_str(c, w):
	r = c.representation
	for c in w:
		i = ord(c)
		# 1. Printable
		# 2. Named character reference
		# 3. Numeric character reference
		if i in xml_printing:
			r.write(c)
			continue
		try:
			escaped = ampersand[c]
			r.write(escaped)
			continue
		except KeyError:
			pass
		numeric = '&#%d;' % (i,)
		r.write(numeric)

def w2t_pretty_bool(c, w, name, tabs):
	if w:
		name_value_pretty(c, 'boolean', name, 'true', tabs)
	else:
		name_value_pretty(c, 'boolean', name, 'false', tabs)

def w2t_pretty_int(c, w, name, tabs):
	value = '%d' % (w,)
	name_value_pretty(c, 'integer', name, value, tabs)

def w2t_pretty_float(c, w, name, tabs):
	value = '%f' % (w,)
	name_value_pretty(c, 'float', name, value, tabs)

def w2t_pretty_str(c, w, name, tabs):
	r = c.representation
	tab = c.find_tab(tabs)
	r.write(tab)
	r.write('<string')
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	r.write('>')
	escaped_str(c, w)
	# Tab here might be included in the recovered
	# value. Leave it dangling.
	r.write('</string>\n')

def w2t_pretty_list(c, w, name, tabs):
	r = c.representation
	tab = c.find_tab(tabs)
	r.write(tab)
	r.write('<list')
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	r.write('>\n')
	for a in w:
		word_to_text_pretty(c, a, None, tabs + 1)
	r.write(tab)
	r.write('</list>\n')

def w2t_pretty_dict(c, w, name, tabs):
	r = c.representation
	tab = c.find_tab(tabs)
	r.write(tab)
	r.write('<message')
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	r.write('>\n')
	for k, v in w.items():
		word_to_text_pretty(c, v, k, tabs + 1)
	r.write(tab)
	r.write('</message>\n')

def w2t_pretty_none(c, w, name, tabs):
	name_value_pretty(c, 'null', name, None, tabs)

# Map the generic type to a dedicated
# transform function.
w2t_pretty = {
	bool: w2t_pretty_bool,
	int: w2t_pretty_int,
	float: w2t_pretty_float,
	str: w2t_pretty_str,
	list: w2t_pretty_list,
	dict: w2t_pretty_dict,
	NoneType: w2t_pretty_none,
}

def word_to_text_pretty(c, w, name, tabs=0):
	try:
		a = getattr(w, '__class__')
	except AttributeError:
		raise TypeError('word is unusable')

	try:
		f = w2t_pretty[a]
	except KeyError:
		raise TypeError('no transformation for word %s' % (a.__name__,))

	# Apply the transform function
	return f(c, w, name, tabs)

# Code fragment per generic type, for output
# of non-pretty_format XML.

# Output a simple XML element - bool, int, float.
def name_value(c, tag, name, value):
	r = c.representation
	r.write('<')
	r.write(tag)
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	if value:
		r.write(' value="')
		r.write(value)
		r.write('"')
	r.write('/>')

def w2t_bool(c, w, name):
	if w:
		name_value(c, 'boolean', name, 'true')
	else:
		name_value(c, 'boolean', name, 'false')

def w2t_int(c, w, name):
	value = '%d' % (w,)
	name_value(c, 'integer', name, value)

def w2t_float(c, w, name):
	value = '%f' % (w,)
	name_value(c, 'float', name, value)

def w2t_str(c, w, name):
	r = c.representation
	r.write('<string')
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	r.write('>')
	escaped_str(c, w)
	# Tab here might be included in the recovered
	# value. Leave it dangling.
	r.write('</string>')

def w2t_list(c, w, name):
	r = c.representation
	r.write('<list')
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	r.write('>')
	for a in w:
		word_to_text(c, a, None)
	r.write('</list>')

def w2t_dict(c, w, name):
	r = c.representation
	r.write('<message')
	if name:
		r.write(' name="')
		r.write(name)
		r.write('"')
	r.write('>')
	for k, v in w.items():
		word_to_text(c, v, k)
	r.write('</message>')

def w2t_none(c, w, name):
	name_value(c, 'null', name, None)

w2t = {
	bool: w2t_bool,
	int: w2t_int,
	float: w2t_float,
	str: w2t_str,
	list: w2t_list,
	dict: w2t_dict,
	NoneType: w2t_none,
}

# Transform the generic data to rather inconvenient XML form.
def word_to_text(c, w, name):
	try:
		a = getattr(w, '__class__')
	except AttributeError:
		raise TypeError('word is unusable')

	try:
		f = w2t[a]
	except KeyError:
		raise TypeError('no transformation for word %s' % (a.__name__,))

	# Apply the transform function
	return f(c, w, name)

# Generate XML text representation of a
# generic word.
def word_to_xml(c, w):
	"""Generate the XML representation of a generic word.

	:param c: an active codec
	:type c: a Codec-based object
	:param w: a generic word
	:rtype: the XML text.
	"""
	c.representation = io.StringIO()
	if c.pretty_format:
		c.representation.write('<?xml version="1.0" ?>\n')
		word_to_text_pretty(c, w, None)
	else:
		c.representation.write('<?xml version="1.0" ?>')
		word_to_text(c, w, None)

	return c.representation.getvalue()

# Decoding - from parsing of JSON to transformation
# into app data items.

def xml_to_word(c, x):
	"""Produce a generic word from the parsing of a text XML representation.

	:param c: an active codec
	:type c: a Codec-based instance
	:param x: the XML text
	:type x: string
	:rtype: a generic word.
	"""
	try:
		e = fromstring(x, forbid_dtd=True, forbid_entities=True, forbid_external=True)
	except ParseError as t:
		raise ValueError(str(t))
	except DTDForbidden as t:
		raise ValueError(str(t))
	except EntitiesForbidden as t:
		raise ValueError(str(t))
	except ExternalReferenceForbidden as t:
		raise ValueError(str(t))

	w = element_to_word(c, e)
	return w

# From generic data (after parsing) to final python
# representation in the application.

def e2w_boolean(c, e):
	v = e.get('value')
	return v == 'true'

def e2w_integer(c, e):
	v = e.get('value')
	return int(v)

def e2w_float(c, e):
	v = e.get('value')
	return float(v)

def e2w_string(c, e):
	# An empty string is encoded as an empty XML element
	# and the parser considers that to be a None string.
	# If the original value was a None it would have been
	# encoded as a null element.
	if e.text is None:
		return str()
	return e.text

def e2w_list(c, e):
	v = [element_to_word(c, s) for s in e]
	return v

def e2w_message(c, e):
	v = {s.get('name'): element_to_word(c, s) for s in e}
	return v

def e2w_null(c, w):
	return None

#
#
e2w = {
	'boolean': e2w_boolean,
	'integer': e2w_integer,
	'float': e2w_float,
	'string': e2w_string,
	'list': e2w_list,
	'message': e2w_message,
	'null': e2w_null,
}

#
#
def element_to_word(c, e):
	a = e.tag	 # The XML element.

	try:
		f = e2w[a]
	except KeyError:
		raise TypeError('no transformation for XML tag "%s"' % (a,))

	return f(c, e)

# Define the wrapper around the JSON encoding
# primitives.
class CodecXml(Codec):
	"""Encoding and decoding of XML representations."""

	EXTENSION = 'xml'
	SINGLE_TAB = '  '

	def __init__(self, return_proxy=None, local_termination=None, pretty_format=False, decorate_names=True):
		"""Construct an XML codec."""
		Codec.__init__(self,
			CodecXml.EXTENSION,
			word_to_xml,
			xml_to_word,
			return_proxy, local_termination, pretty_format, decorate_names)
		self.representation = None
		self.tabstops = {}

	def find_tab(self, tabs):
		"""Generate the tab-space indicated by the tabs count. Return a string of spaces."""
		try:
			tab = self.tabstops[tabs]
		except KeyError:
			tab = CodecXml.SINGLE_TAB * tabs
			self.tabstops[tabs] = tab
		return tab
