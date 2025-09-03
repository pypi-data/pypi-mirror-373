import numpy as np, pandas as pd
import datetime as dt
from ..environ.environ import (
	TABLE_BUFFER,
	TABLE_FILLER,
	FLOAT_FORMAT,
)
from ..lego.types import (
  DATETIME_REGEX,
  DIGIT_REGEX,
  NUM_REGEX,
  PERC_REGEX
)
from typing import Iterable, Union
from pandas import RangeIndex, Index


def rectanglize(matrix: list) -> list:
	width = max([len(row) for row in matrix])

	for i, row in enumerate(matrix):
		diff = width - len(row)

		for j in range(0, diff):
			matrix[i].append(None)

	return matrix


def jsonify_matrix(matrix: np.ndarray,) -> list:
	output: np.ndarray= matrix.copy()
	output: np.ndarray = np.where(
		pd.isna(matrix),
		'',
		output)

	def format_datetime(val):
		if isinstance(val, np.datetime64):
			return dt.datetime.fromtimestamp(
				val.astype('datetime64[s]')).strftime('%Y-%m-%d %H:%M:%S')
		return val

	def format_numeric(val):
		if np.issubdtype(type(val), np.number):
			if np.issubdtype(type(val), np.floating):
				return FLOAT_FORMAT.format(val)
			return str(val)
		return str(val)

	def format_nan(val):
		if pd.isna(val):
			return ''
		return str(val)

	nan_formmater = np.vectorize(format_nan)
	datetime_formatter = np.vectorize(format_datetime)
	numeric_formatter = np.vectorize(format_numeric)
	output: np.ndarray = nan_formmater(output)
	output: np.ndarray = datetime_formatter(output)
	output: np.ndarray = numeric_formatter(output)
	output_lst: list = list(output.tolist())
	return output_lst


def ndarray_to_df(matrix: np.ndarray) -> pd.DataFrame:
	value_layers = get_value_layers(matrix)
	column_height = get_column_height(value_layers)
	index_width = get_index_width(value_layers)
	columns = make_frame_edges(
		matrix[0:column_height:, index_width:],
		'column'
	)
	data = matrix[column_height:, index_width:]
	frame_args = {
		'data': data,
		'columns': columns
	}

	if index_width > 0:
		indexes = make_frame_edges(
			matrix[column_height:, 0:index_width],
			'index'
		)
		frame_args['index'] = indexes

	df = pd.DataFrame(**frame_args)
	return df


def get_value_layers(matrix: np.ndarray):
	from .sheet_objects import ValueLayers
	return ValueLayers(matrix=matrix)


def get_column_height(value_layers) -> int:
	column_height = 1

	for i in range(0, len(value_layers.matrix)):
		row = value_layers.matrix[i]
		buffers = row[row == TABLE_BUFFER]
		bin_row = value_layers.bin_layer[i]
		row_sum = bin_row.sum() - len(buffers)
		row_len = len(row) - len(buffers)
		fillers = row[row == TABLE_FILLER]

		if row_sum == row_len and len(fillers) > 0:
			column_height += 1
		else:
			break

	return column_height


def get_index_width(value_layers) -> int:
	if has_digit_index(value_layers.matrix[:, 0]):
		return 0

	index_width = 0

	for i in range(0, len(value_layers.matrix[0])):
		column_matrix = value_layers.matrix[:, i]
		buffers = column_matrix[column_matrix == TABLE_BUFFER]
		fillers = column_matrix[column_matrix == TABLE_FILLER]

		if len(buffers) > 0 or len(fillers) > 0:
			index_width += 1
		else:
			break

	return index_width


def has_digit_index(
  matrix: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray]
) -> bool:
	if isinstance(matrix, pd.DataFrame):
		if isinstance(matrix.index, RangeIndex):
			return True
		elif isinstance(matrix.index, Index):
			return all([DIGIT_REGEX.match(str(val)) for val in matrix.index])
		else:
			return False
	return all([DIGIT_REGEX.match(str(val)) for val in matrix])


def make_frame_edges(
	edges: np.ndarray,
	edge_type: str,
) -> np.ndarray | pd.MultiIndex:
	if any([True if dim == 0 else False for dim in edges.shape]):
		return edges

	if edge_type not in ('column', 'index'):
		raise Exception(f'INVALID EDGE TYPE:{edge_type}')

	output = edges.copy() if edge_type == 'column' else edges.copy().transpose()

	for i, row in enumerate(output):
		for j, val in enumerate(row):
			if val == TABLE_FILLER:
				output[i, j] = output[i, j-1]

	if output.shape[0] == 1:
		return output[0]

	return pd.MultiIndex.from_arrays(output) # type: ignore


def to_ndarray(
	data: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray],
	keep_columns: bool,
) -> np.ndarray:
	if not isinstance(data, pd.DataFrame):
		if isinstance(data, pd.Series):
			return data.to_frame().T.values
		elif isinstance(data, (list, tuple)):
			return np.array(data)
		return data

	matrix = data.values

	if keep_columns:
		column_array = get_column_array(data)
		matrix = np.concatenate([column_array, matrix], axis=0)

	if not has_digit_index(data):
		index_array = get_index_array(data)
		matrix = np.concatenate((index_array, matrix), axis=1)

	return matrix


def get_column_char(column_index: int) -> str:
	alph = ''
	while column_index > -1:
		column_index, remainder = divmod(column_index, 26)
		alph = chr(65 + remainder) + alph
		column_index -= 1
	return alph


def get_index_array(data:pd.DataFrame) -> np.ndarray:
	indexes = data.index
	index_width = indexes.nlevels
	column_height = data.columns.nlevels
	index_array = np.empty(
		shape=(indexes.shape[0], index_width),
		dtype='object')

	for i, idx_row in enumerate(indexes):
		if isinstance(idx_row, tuple):
			for j, idx in enumerate(idx_row):
				if i > 0:
					if index_array[i-1, j] == idx:
						index_array[i, j] = TABLE_FILLER
					else:
						index_array[i, j] = idx
				else:
					index_array[i, j] = idx
		else:
			index_array[i] = idx_row

	full_array= np.full(
		shape=(column_height, index_width),
		fill_value=TABLE_BUFFER)
	index_array = np.concatenate(
		(full_array, index_array),
		axis=0)
	return index_array


def get_column_array(data:pd.DataFrame) -> np.ndarray:
	columns = data.columns
	col_height = columns.nlevels
	column_array = np.empty(shape=(col_height, columns.shape[0]), dtype='object')

	if col_height == 1:
		for i, col in enumerate(columns):
			column_array[0, i] = col
	else:
		for i, col_tup in enumerate(columns):
			for j, col in enumerate(col_tup):
				if i > 0:
					if column_array[j, i-1] == col:
						column_array[j, i] = TABLE_FILLER
					else:
						column_array[j, i] = col
				else:
					column_array[j, i] = col
	return column_array


def autotype_df(
  df: pd.DataFrame
) -> pd.DataFrame:
  for col in df.columns:
    vals = df[col][pd.notna(df[col])]

    if len(vals) == 0:
      continue

    if all([NUM_REGEX.match(str(val)) for val in vals]):
      df.loc[df[col].notna(),col] = pd.to_numeric(vals.astype(str).str.replace(',', '').str.strip())
    elif all([DATETIME_REGEX.match(str(val)) for val in vals]):
      df.loc[df[col].notna(), col] = pd.to_datetime(vals, format='mixed')
    elif all([PERC_REGEX.match(str(val)) for val in vals]):
      df.loc[df[col].notna(), col] = vals.str.replace('%', '').str.replace(',' ,'').str.strip()
      df.loc[df[col].notna(), col] = pd.to_numeric(df.loc[df[col].notna(), col])
      df[col] = df[col] / 100

  return df

def width(data: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray]) -> int:
	if isinstance(data, (list, tuple, np.ndarray)):
		pass
	elif isinstance(data, (pd.DataFrame, pd.Series)):
		pass
	raise Exception(f'INVALID DATA TYPE:{type(data)}')


def height(data: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray]) -> int:
	if isinstance(data, (list, tuple, np.ndarray)):
		pass
	elif isinstance(data, (pd.DataFrame, pd.Series)):
		pass
	raise Exception(f'INVALID DATA TYPE:{type(data)}')
