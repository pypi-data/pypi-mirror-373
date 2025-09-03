from google.auth.credentials import Credentials
from requests import Session
from google.auth.transport.requests import AuthorizedSession
from typing import (
	Mapping, Any, Union
)
from pathlib import Path
from .client_utils import convert_credentials


class Client:

	def __init__(
		self,
		auth: Credentials,
		info: Mapping[str, Any] | None,
		filename: Union[Path, str, None]
  ) -> None:
		self._auth = auth
		self.info = info
		self.filename = filename
		self._session = None
		self._drive_service = None
		self._spreadsheet_service = None

	@property
	def auth(self):
		return convert_credentials(self._auth)

	@property
	def session(self) -> Session:
		if self._session is None:
			self._session = AuthorizedSession(self.auth)
		return self._session
