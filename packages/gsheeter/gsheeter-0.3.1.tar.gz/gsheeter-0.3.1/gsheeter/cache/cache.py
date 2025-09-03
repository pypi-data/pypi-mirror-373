from typing import Any

IDENTIFIERS = [
	'id',
	'spreadsheetId',
	'name'
]
USE_CACHE = True

class CacheService:

	def __init__(self):
		self.items = []

	def get_item(self, target: str) -> Any:
		if not USE_CACHE:
			return None

		for item in self.items:
			for idf in IDENTIFIERS:
				if target == item.getattr(idf):
					return item
		return None

	def set_item(self, obj):
		if not USE_CACHE:
			return
		self.items.append(obj)

def set_cache_usage(use: bool):
	USE_CACHE = use

cache = CacheService()
