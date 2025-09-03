DRIVE_BASE_URL:str = 'https://www.googleapis.com'
DRIVE_ENDPOINTS:dict = {
	'about': {
		'method': 'get',
		'endpoint': '/drive/v3/about'
	},
	'accessproposals': {
		'get': {
			'method': 'get',
			'endpoint': '/drive/v3/files/{fileId}/accessproposals/{proposalId}'
		},
		'list': {
			'method': 'get',
			'endpoint': '/drive/v3/files/{fileId}/accessproposals'
		},
		'resolve': {
			'method': 'post',
			'endpoint': '/drive/v3/files/{fileId}/accessproposals/{proposalId}:resolve'
		}
	},
	'apps': {
		'get':{
			'method': 'get',
			'endpoint': '/drive/v3/apps/{appId}'
		},
		'list': {
			'method': 'get',
			'endpoint': '/drive/v3/apps'
		}
	},
	'changes': {
		'getStartPageToken': {
			'method': 'get',
			'endpoint': '/drive/v3/changes/startPageToken'
		},
		'list': {
			'method': 'get',
			'endpoint': '/drive/v3/changes'
		},
		'watch': {
			'method': 'post',
			'endpoint': '/drive/v3/changes/watch'
		}
	},
	'channels': {
		'stop': {
			'method': 'post',
			'endpoint': '/drive/v3/channels/stop'
		}
	},
	'comments': {
		'create': {
			'method': 'post',
			'endpoint': '/drive/v3/files/{fileId}/comments'
		},
		'delete': {
			'method': 'delete',
			'endpoint': '/drive/v3/files/{fileId}/comments/{commentId}'
		},
		'get': {
			'method': 'get',
			'endpoint': '/drive/v3/files/{fileId}/comments/{commentId}'
		},
		'list': {
			'method': 'get',
			'endpoint': '/drive/v3/files/{fileId}/comments'
		},
		'update': {
			'method': 'patch',
			'endpoint': '/drive/v3/files/{fileId}/comments/{commentId}'
		}
	},
	'drives': {
		'create': {
			'method': 'post',
			'endpoint': '/drive/v3/drives'
		},
		'delete': {
			'method': 'delete',
			'endpoint': '/drive/v3/drives/{driveId}'
		},
		'get': {
			'method': 'get',
			'endpoint': '/drive/v3/drives/{driveId}'
		},
		'hide': {
			'method': 'post',
			'endpoint': '/drive/v3/drives/{driveId}/hide'
		},
		'list': {
			'method': 'get',
			'endpoint': '/drive/v3/drives/'
		},
		'unhide': {
			'method': 'post',
			'endpoint': '/drive/v3/drives/{driveId}/unhide'
		},
		'update': {
			'method': 'patch',
			'endpoint': '/drive/v3/drives/{driveId}'
		}
	},
	'files': {
		'copy': {
			'method': 'post',
			'endpoint': '/drive/v3/files/{fileId}/copy',
		},
		'create': {
			'method': 'post',
			'endpoint': '/drive/v3/files',
		},
		'delete': {
			'method': 'delete',
			'endpoint': '/drive/v3/files/{fileId}',
		},
		'download': {
			'method': 'post',
			'endpoint': '/drive/v3/files/{fileId}/download',
		},
		'emptyTrash': {
			'method': 'delete',
			'endpoint': '/drive/v3/files/trash',
		},
		'export': {
			'method': 'get',
			'endpoint': '/drive/v3/files/{fileId}/export',
		},
		'generateId': {
			'method': 'get',
			'endpoint': '/drive/v3/files/generateIds',
		},
		'get': {
			'method': 'get',
			'endpoint': '/drive/v3/files/{fileId}',
		},
		'list': {
			'method': 'get',
			'endpoint': '/drive/v3/files',
		},
		'listLabels': {
			'method': 'get',
			'endpoint': '/drive/v3/files/{fileId}/listLabels',
		},
		'modifyLabels': {
			'method': 'post',
			'endpoint': '/drive/v3/files/{fileId}/modifyLabels',
		},
		'update': {
			'method': 'patch',
			'endpoint': '/drive/v3/files/{fileId}',
		},
		'watch': {
			'method': 'post',
			'endpoint': '/drive/3/files/{fileId}/watch'
		}
	}

}