from ..client.client import Client
import traceback, time
from typing import Mapping
from .property import classproperty
from requests import Response, Session
from .exceptions import (
	NotFoundException,
	PermissionDeniedException
)

BASE_URLS = {
	'spreadsheets': 'https://sheets.googleapis.com',
	'drive': 'https://www.googleapis.com'
}


class GoogleAPI:

	_headers_ = {
		'Content-Type': 'application/json'
	}
	_max_wait_ = 120

	@classmethod
	def add_query(
		cls,
		endpoint: str,
		**kwargs
	) -> str:
		conditions = []

		for k, v in kwargs.items():
			if v is not None:
				cond = f'{k}={v}'
				conditions.append(cond)

		query = '&'.join(conditions)
		return endpoint + '?' + query

	@classmethod
	def get_client(cls) -> Client:
		from ..auth.auth import _client
		if _client is None:
			raise Exception('CLIENT NOT ACTIVATED')
		return _client

	@classproperty
	def client(cls):
		return cls.get_client()

	@classmethod
	def base_url(cls, endpoint: str):
		for k, v in BASE_URLS.items():
			if k in endpoint:
				return v

		raise Exception('INVALID ENDPOINT')

	@classmethod
	def request(
		cls,
		method: str,
		endpoint: str,
		json: dict | None = None,
		headers: dict | None = None,
		data: str | None = None,
		**kwargs
	):
		base_url = cls.base_url(endpoint=endpoint)
		url = base_url + endpoint

		if headers is None:
			headers = cls._headers_

		wait_time = 0.5
		result = {}

		while wait_time < cls._max_wait_:
			session: Session = cls.client.session
			res: Response = session.request(
				method=method,
				url=url,
				json=json,
				headers=headers,
				data=data,
			)
			result:dict = res.json()

			if (error := result.get('error')) is not None:
				status = error['status']

				if status == 'NOT_FOUND':
					raise NotFoundException()
				elif status == 'PERMISSION_DENIED':
					raise PermissionDeniedException()
				elif status == 'RATE_LIMIT_EXCEEDED':
					print('RATE_LIMIT_EXCEEDED WAITING...')
				else:
					raise Exception(error, json, data)

				time.sleep(wait_time)
				wait_time *= (1+wait_time)
			else:
				break

		return result
