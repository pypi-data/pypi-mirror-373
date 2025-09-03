import json, os, platform
from pathlib import Path
from google.auth.api_key import Credentials as APIKeyCredentials
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.oauth2.service_account import Credentials as SACredentials
from requests import Session
from typing import (
	Any, Dict, Iterable, Mapping, Optional,
	Protocol, Tuple, Union,
)

DEFAULT_SCOPES = (
  "https://www.googleapis.com/auth/spreadsheets",
  "https://www.googleapis.com/auth/drive",
)

def get_config_dir(
	config_dir: str = 'gsheeter'
) -> Path:
	if platform.system() == 'Windows':
		return Path(os.environ['APPDATA'], config_dir)

	return Path(Path.home(), '.config', config_dir)

DEFAULT_CONFIG_DIR = get_config_dir()
DEFAULT_CREDENTIALS_FILENAME = DEFAULT_CONFIG_DIR / 'gcreds.json'
DEFAULT_AUTHORIZED_USER_FILENAME = DEFAULT_CONFIG_DIR /'auth_user.json'
DEFAULT_SERVICE_ACCOUNT_FILENAME = DEFAULT_CONFIG_DIR / 'service_account.json'


from ..client.client import Client

_credentials = None
_client = None


def service_account(
	input: Union[Path, str] | Mapping[str, Any],
	scopes: Iterable[str] = DEFAULT_SCOPES,
):
	global _client, _credentials
	info = None
	filename = None

	if input is None:
		input = DEFAULT_SERVICE_ACCOUNT_FILENAME

	if isinstance(input, Mapping):
		info = input
		_credentials = SACredentials.from_service_account_info(
			info=info,
			scopes=scopes
		)
	else:
		if not os.path.exists(input):
			raise Exception('SERVICE_ACCOUNT_FILE NOT FOUND')

		filename = input
		_credentials = SACredentials.from_service_account_file(
			filename=filename,
			scopes=scopes)

	if filename is None:
		raise Exception('FILE NOT FOUND')

	_client = Client(
		auth=_credentials,
		info=info,
		filename=filename)

def oauth():
	pass
