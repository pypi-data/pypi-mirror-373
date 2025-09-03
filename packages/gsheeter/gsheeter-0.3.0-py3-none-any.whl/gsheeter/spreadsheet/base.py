import numpy as np, pandas as pd
import sys


from ..lego.lego import Lego
from typing import Iterable, Union, Mapping
from ..lego.api import GoogleAPI
from .sheets_endpoints import SHEETS_ENDPOINTS
from .sheets_enum import Dimension
from .sheet_utils import (
	get_column_char,
	jsonify_matrix,
	rectanglize,
	get_value_layers,
)
from copy import deepcopy
from icecream import ic


ic.configureOutput(includeContext=True)
ENDPOINT_FORMATTERS = ['spreadsheetId', 'sheetId']


class SpreadsheetBase(Lego, GoogleAPI):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._requests:list = []
		self._endpoints = None

	@property
	def endpoints(self) -> dict:
		if self._endpoints is None:
			self._endpoints = self.format_endpoints(ENDPOINT_FORMATTERS)
		return self._endpoints

	@property
	def spreadsheetId(self):
		return self.getattr('spreadsheetId')

	@property
	def requests(self) -> list:
		return self._requests

	def format_endpoints(self, match_strings: list) -> dict:
		endpoints = deepcopy(SHEETS_ENDPOINTS)
		attrs = dir(self)
		attrs = list(set(attrs) & set(match_strings))

		def format_endpoint(d):
			if isinstance(d, dict):
				for k, v in d.items():
					if k == 'endpoint':
						for string in match_strings:
							if string in v:
								rep_string = '{' + string + '}'
								attr_val = str(self.getattr(string))
								v = str(v).replace(rep_string, attr_val)
						d[k] = v

					elif isinstance(v, dict):
						format_endpoint(v)

		format_endpoint(endpoints)
		return endpoints

	def batchUpdate(
		self,
		requests: list = [],
		object: str = 'spreadsheets',
	) -> dict | None:
		if len(requests) == 0:
			requests = self.requests

		if type(requests) != list:
			requests = [requests]

		if len(requests) == 0:
			return None

		endpoint_items = deepcopy(self.endpoints[object]['batchUpdate'])
		endpoint_items['data']['requests'] = requests
		result = self.request(**endpoint_items)
		return result

class SheetBase(SpreadsheetBase):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.max_packet_size = 1.9

	@property
	def title(self) -> str:
		return self.getattr('title')

	@property
	def sheetId(self) -> str:
		return self.getattr('sheetId')

	@property
	def matrix(self) -> np.ndarray:
		matrix = self.getattr('matrix')

		if matrix is None:
			matrix = self.get_matrix()
			self.setattr('matrix', matrix)

		return matrix

	@matrix.setter
	def matrix(self, value):
		self.setattr('matrix', value)

	@property
	def rowCount(self) -> int:
		return self.getattr('rowCount')

	@property
	def columnCount(self) -> int:
		return self.getattr('columnCount')

	def format(
		self,
	):
		pass

	def clear_range(
		self,
		x_offset: int,
		y_offset: int,
		width: int,
		height: int,
	):
		empty_array = np.empty(
			shape=(height, width),
			dtype='object')
		self.update_sheet(
			matrix=empty_array,
			x_offset=x_offset,
			y_offset=y_offset)

	def update_sheet(
		self,
		matrix: np.ndarray,
		x_offset: int,
		y_offset: int,
	) -> bool:
		packets = self.make_packets(
			matrix=matrix,
			x_offset=x_offset,
			y_offset=y_offset)
		self.auto_dimension(
			matrix=matrix,
			x_offset=x_offset,
			y_offset=y_offset)
		self.send_packets(packets)
		self.apply_value_changes(
			matrix=matrix,
			x_offset=x_offset,
			y_offset=y_offset)
		return True

	def get_last_filled_y(
		self,
		matrix: np.ndarray,
		x_offset: int,
		width: int,
	) -> int:
		y_coord = -1
		layers = get_value_layers(matrix)

		for i in range(x_offset, x_offset+width):
			if i >= matrix.shape[1]:
				break

			col = layers.bin_layer[:, i]
			indices = np.where(col == 1)[0]

			if len(indices) > 0:
				last_idx = indices[-1]

				if last_idx > y_coord:
					y_coord = last_idx

		return y_coord

	def apply_value_changes(
		self,
		matrix: np.ndarray,
		x_offset: int,
		y_offset: int,
	) -> None:
		self.extend_array(
			attach=matrix,
			x_offset=x_offset,
			y_offset=y_offset)
		ver_ext = slice(y_offset, y_offset+matrix.shape[0])
		hor_ext = slice(x_offset, x_offset+matrix.shape[1])
		self.matrix[ver_ext, hor_ext] = matrix

	def extend_array(
		self,
		attach: np.ndarray,
		x_offset: int,
		y_offset: int,
	):
		attach_height = y_offset + attach.shape[0]
		attach_width = x_offset + attach.shape[1]

		if attach_height > self.matrix.shape[0] or attach_width > self.matrix.shape[1]:
			new_height = max(self.matrix.shape[0], attach_height)
			new_width = max(self.matrix.shape[1], attach_width)
			new_shape = (new_height, new_width)
			new_base = np.empty(new_shape, dtype=self.matrix.dtype)
			new_base[:self.matrix.shape[0], :self.matrix.shape[1]] = self.matrix
			self.matrix = new_base

	def two_dimensionalize(
		self,
		data: Union[np.ndarray, list, tuple],
	) -> np.ndarray:
		if not isinstance(data[0], (np.ndarray, list, tuple)):
			data = [data]

		if isinstance(data, (list, tuple)):
			data = np.array(data, dtype='object')
		return data

	def convert_input(
		self,
		data: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray],
	) -> Union[pd.DataFrame, np.ndarray, pd.Series]:
		if isinstance(data, (list, tuple, np.ndarray)):
			data = self.two_dimensionalize(data=data)
		return data

	def get_matrix(self) -> np.ndarray:
		endpoint_items = deepcopy(self.endpoints['values']['get'])
		endpoint_items['endpoint'] = endpoint_items['endpoint'].format(
			range=self.title)
		result = self.request(**endpoint_items)
		rowCount = self.getattr('rowCount')
		columnCount = self.getattr('columnCount')
		matrix = result.get(
			'values',
			np.empty(
				(rowCount, columnCount),
				dtype='object'
			)
		)

		if type(matrix) == list:
			matrix = rectanglize(matrix)
			matrix = np.array(matrix, dtype='object')
			matrix = np.where(
        matrix == '',
        None, # type: ignore
        matrix)

		return matrix

	def send_packets(
		self,
		packets: list,
	) -> None:
		endpoint_items = deepcopy(self.endpoints['values']['batchUpdate'])

		for packet in packets:
			endpoint_items['json'] = {
				'valueInputOption': 'USER_ENTERED',
				'data': packet
			}
			result = self.request(**endpoint_items)

	def get_range(
		self,
		x_offset: int,
		y_offset: int,
		width: int,
		height: int,
	) -> str:
		start_col = get_column_char(x_offset)
		end_col = get_column_char(x_offset + width - 1)
		start_row = y_offset + 1
		end_row = y_offset + height
		start_rng = f'{start_col}{start_row}'
		end_rng = f'{end_col}{end_row}'
		return f'{self.title}!{start_rng}:{end_rng}'

	def make_packets(
		self,
		matrix: np.ndarray,
		x_offset: int,
		y_offset: int,
	) -> list:
		packets = []
		start = 0
		end = len(matrix)

		while start < end:
			batch = matrix[start:end]
			data_size = sys.getsizeof(batch) / (1024 * 1024)

			if data_size > self.max_packet_size:
				end -= 1
			else:
				rng = self.get_range(
					x_offset=x_offset,
					y_offset=y_offset,
					width=len(batch[0]),
					height=len(batch)
				)
				data: list = jsonify_matrix(batch)
				packet = {
					'range': rng,
					'values': data
				}
				packets.append(packet)
				start += len(batch)

		return packets

	def auto_dimension(
		self,
		matrix: np.ndarray,
		x_offset: int,
		y_offset: int,
	) -> None:
		shape = matrix.shape
		row_diff = int((shape[0] + y_offset) - self.rowCount)
		col_diff =  int((shape[1] + x_offset) - self.columnCount)

		if row_diff > 0:
			self.append_dimension('ROWS', row_diff, False)

		if col_diff > 0:
			self.append_dimension('COLUMNS', col_diff, False)

		self.batchUpdate()

	def append_dimension(
		self,
		dimension: str,
		length: int,
		send: bool = True,
	):
		if dimension not in Dimension:
			raise Exception('INVALID DIMENSION VAR')

		req = {
			'appendDimension': {
				'sheetId': self.getattr('sheetId'),
				'dimension': dimension,
				'length': length
			}
		}

		if send:
			self.batchUpdate(requests=[req])
		else:
			self.requests.append(req)

		return req
