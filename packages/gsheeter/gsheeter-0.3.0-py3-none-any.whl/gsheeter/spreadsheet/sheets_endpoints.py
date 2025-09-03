SHEETS_BASE_URL: str = 'https://sheets.googleapis.com'
SHEETS_ENDPOINTS: dict = {
	'spreadsheets': {
		'batchUpdate': {
			'method': 'post',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}:batchUpdate',
			'data': {}
		},
		'create': {
			'method': 'post',
			'endpoint': '/v4/spreadsheets'
		},
		'get': {
			'method': 'get',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}'
		},
		'copyTo': {
			'method': 'get',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo'
		},
		'developerMetadata': {
			'get': {
				'method': 'get',
				'endpoint': '/v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}'
			},
			'search': {
				'method': 'post',
				'endpoint': '/v4/spreadsheets/{spreadsheetId}/developerMetadata:search'
			}
		},
	},
	'sheets': {
		'copyTo': {
			'method': 'post',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo'
		}
	},
	'values': {
		'append': {
			'method': 'post',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/values/{range}:append'
		},
		'batchClear': {
			'method': 'post',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/values:batchClear'
		},
		'batchGet': {
			'method': 'get',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/values:batchGet'
		},
		'batchUpdate': {
			'method': 'post',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/values:batchUpdate'
		},
		'clear': {
			'method': 'post',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/values/{range}:clear'
		},
		'get': {
			'method': 'get',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/values/{range}'
		},
		'update': {
			'method': 'put',
			'endpoint': '/v4/spreadsheets/{spreadsheetId}/values/{range}'
		}
	}
}
