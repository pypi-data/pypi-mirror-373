from collections import UserDict
import datetime as dt
import re
from .funcs import (
	parse_date,
	update_key,
	set_nested_value,
	nested_recursive_search,
	get_all_keys
)
from typing import Any

class Lego(UserDict):

	def __init__(self, **kwargs):
		for k in kwargs.keys():
			v = kwargs[k]
			kwargs[k] = parse_date(v)

		self.data = kwargs
		self.data['created_at'] = dt.datetime.now() if kwargs.get('created_at') is None else kwargs['created_at']
		self.data['updated_at'] = None if kwargs.get('updated_at') is None else kwargs['updated_at']

	@property
	def created_at(self):
		return self.getattr('created_at')

	@property
	def updated_at(self):
		return self.getattr('updated_at')

	def stamp(self):
		self.setattr('updated_at', dt.datetime.now())

	def setAll(self, **kwargs):
		for k, v in kwargs.items():
			self.setattr(k, v)

	def setattr(self, key:str | list, value):
		completed = False

		if type(key) == str:
			completed = update_key(self.data, key, value)

		if not completed:
			keys = key if type(key) == list else [key]
			set_nested_value(self.data, keys, value)

	def getattr(self, key) -> Any:
		return nested_recursive_search(self.data, key)

	def to_dict(self, to_json=False):
		obj_dict = self.__dict__
		output = obj_dict.copy()

		for k in get_all_keys(obj_dict):

			if k == '_data':
				data = output.get(k)

				if data is not None:
					for key, value in data.items():
						output[key] = value

					output.pop(k)
			else:
				v = output.get(k)

				if to_json:
					if isinstance(v, dt.datetime):
						nv = v.strftime('%Y-%m-%d %H:%M:%S')
						result = update_key(output, k, nv)

		return output
