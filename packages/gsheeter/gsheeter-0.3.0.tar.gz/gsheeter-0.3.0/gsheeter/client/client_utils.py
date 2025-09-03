from google.auth.credentials import Credentials as Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from . import client_types

def convert_credentials(
	creds: Credentials
) -> Credentials:
	module = creds.__module__
	cls = creds.__class__.__name__

	if 'oauth2client' in module and cls == 'ServiceAccountCredentials':
		return _convert_to_service_account(creds)
	elif 'oauth2client' in module and cls in client_types.OAUTH_CREDENTIALS:
		return _convert_to_oauth(creds)
	elif isinstance(creds, Credentials):
		return creds

	raise TypeError('INVALID CREDENTIAL TYPE')

def _convert_to_service_account(credentials) -> Credentials:
    data = credentials.serialization_data
    data["token_uri"] = credentials.token_uri
    scopes = credentials._scopes.split() or [
        "https://www.googleapis.com/auth/drive",
        "https://spreadsheets.google.com/feeds",
    ]

    return ServiceAccountCredentials.from_service_account_info(data, scopes=scopes)

def _convert_to_oauth(credentials) -> Credentials:
    return UserCredentials(
        credentials.access_token,
        credentials.refresh_token,
        credentials.id_token,
        credentials.token_uri,
        credentials.client_id,
        credentials.client_secret,
        credentials.scopes,
    )
