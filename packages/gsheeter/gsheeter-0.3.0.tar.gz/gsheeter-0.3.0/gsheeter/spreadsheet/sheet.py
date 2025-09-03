import pandas as pd
import numpy as np
import datetime as dt
import sys


from pandas import RangeIndex
from .base import SheetBase
from .sheets_enum import Dimension
from typing import (
  Union, Iterable, Generator, List
)
from .sheet_objects import (
  Table, ValueLayers,
  SheetSquared
)
from .sheet_utils import (
  get_value_layers,
  to_ndarray,
  autotype_df
)
from ..environ.environ import (
  TABLE_BUFFER,
  TABLE_FILLER,
  AUTOTYPING,
)
from icecream import ic


ic.configureOutput(includeContext=True)


class Sheet(SheetBase):

  def __init__(
    self,
    t_idx: int = 0,
    **kwargs,
  ) -> None:
    super().__init__(**kwargs)
    self.t_idx = t_idx
    self._tables = []

  @property
  def tables(self) -> List[Table]:
    self._tables = self.ndarray_to_tables(self.matrix)
    return self._tables

  @property
  def table(self) -> Table:
    if len(self.tables) == 0:
      return Table(
        anchor=(0, 0),
        outer_height=0,
        outer_width=0,
        parent=self)
    if self.t_idx >= len(self.tables):
      return self.tables[-1]
    return self.tables[self.t_idx]

  @property
  def df(self) -> pd.DataFrame:
    if len(self.tables) == 0:
      self._df = pd.DataFrame()
    else:
      if self.table is None:
        self._df = pd.DataFrame()
      else:
        if AUTOTYPING:
          self._df = autotype_df(self.table.df)
        else:
          self._df = self.table.df

    return self._df

  @df.setter
  def df(self, value):
    self._df = value

  def get_table(
    self,
    anchor: tuple,
    outer_height: int,
    outer_width: int,
  ) -> Table:
    table_items = self.get_table_items(
      anchor,
      outer_height,
      outer_width)
    return Table(**table_items)

  def get_table_items(
    self,
    anchor: tuple,
    outer_height: int,
    outer_width: int,
  ) -> dict:
    return {
      'spreadsheetId': self.spreadsheetId,
      'sheetId': self.sheetId,
      'title': self.title,
      'anchor': anchor,
      'matrix': self.matrix,
      'outer_height': outer_height,
      'outer_width': outer_width,
      'rowCount': self.rowCount,
      'columnCount': self.columnCount,
      'parent': self,
    }

  def get_nth_table(self, idx: int) -> Table | None:
    if idx >=  len(self.tables):
      return None
    return self.tables[idx]

  def ndarray_to_tables(
    self,
    matrix: np.ndarray
  ) -> List[Table]:
    if self.has_single_table(matrix):
      return [self.get_single_table(matrix)]

    tables = []
    layers = get_value_layers(matrix)

    for i in range(0, matrix.shape[0]):
      for j in range(0, matrix.shape[1]):
        anchor = (i, j)
        ver = layers.ver_layer[anchor]
        bin = layers.bin_layer[anchor]
        square = None

        if ver != -1 and bin == 1:
          square, layers = SheetSquared.get_square(
            anchor, layers)

        if square is not None:
          table = self.get_table(anchor, *square.shape)
          columns = np.array([
            '-'.join(c)
            for c in table.df.columns
          ])
          unique_cols = np.unique(columns)
          add_table = len(columns) == len(unique_cols)

          if not isinstance((index := table.df.index), RangeIndex) and add_table:
            index = np.array([str(r) for r in index])
            unique_idx = np.unique(index)
            add_table = len(index) == len(unique_idx)

          if add_table:
            tables.append(table)

    return tables

  def get_single_table(
    self,
    matrix: np.ndarray
  ) -> Table:
    vl = get_value_layers(matrix)
    first_fill_idx = vl.first_fill_idx
    last_fill_idx = vl.last_fill_idx

    if first_fill_idx is None or last_fill_idx is None:
      raise Exception('GET_SINGLE_TABLE FAILED')

    width = vl.width
    height = last_fill_idx - first_fill_idx + 1
    table = self.get_table(
      anchor=(0, 0),
      outer_height=height,
      outer_width=width)
    return table

  def has_single_table(
    self,
    matrix: np.ndarray
  ) -> bool:
    vl = get_value_layers(matrix=matrix)
    first_fill_idx = vl.first_fill_idx
    max_fill_idx = vl.max_fill_idx

    if (first_fill_idx is None
      and max_fill_idx is None):
      return False

    first_fill_row = matrix[first_fill_idx]
    if any(
      [
        TABLE_FILLER in first_fill_row,
        TABLE_BUFFER in first_fill_row
      ]
    ):
      return False

    first_row = matrix[first_fill_idx]
    unique_arr = np.unique(first_row[pd.notna(first_row)])
    return (
      first_fill_idx == max_fill_idx and
      len(first_row) == len(unique_arr)
    )

  def delete_table(
    self,
    target: Table | int,
  ): 
    if isinstance(target, Table):
      for i, t in enumerate(self.tables):
        if t == target:
          self.clear_range(
            x_offset=target.x_anchor,
            y_offset=target.y_anchor,
            width=target.outer_width,
            height=target.outer_height)
          self.tables.pop(i)
          break
    elif isinstance(target, int):
      if target < len(self.tables):
        t = self.tables[target]
        self.clear_range(
          x_offset=t.x_anchor,
          y_offset=t.y_anchor,
          width=t.outer_width,
          height=t.outer_height)
        self.tables.pop(target)

  def set_values(
    self,
    data: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray],
    x_offset: int = 0,
    y_offset: int = 0,
    append: bool = False,
    rng: str | None = None,
  ) -> None:
    if len(data) == 0:
      return

    data = self.convert_input(data)
    appended = False

    if append:
      if y_offset == 0:
        appended = self.append_to_table(
          data=data,
          x_offset=x_offset)

      if appended:
        return

    if not appended:
      self.paste_data(
        data=data,
        x_offset=x_offset,
        y_offset=y_offset,
        append=append)

  def paste_data(
    self,
    data: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray],
    x_offset: int,
    y_offset: int,
    append: bool,
  ) -> bool:
    input_matrix = to_ndarray(
      data=data, keep_columns=True)
    x_anchor = x_offset
    y_anchor = y_offset

    if append:
      y_anchor += self.get_last_filled_y(
        self.matrix,
        x_offset=x_offset,
        width=input_matrix.shape[1]
      ) + 1

    result = self.update_sheet(
      matrix=input_matrix,
      x_offset=x_anchor,
      y_offset=y_anchor)

    return result

  def append_to_table(
    self,
    data: Union[pd.DataFrame, pd.Series, list, tuple, np.ndarray],
    x_offset: int,
  ) -> bool:
    result = False
    
    for table in self.tables:
      if x_offset != table.x_anchor:
        continue
      
      x_anchor = table.x_anchor
      y_anchor = table.y_anchor
      outer_width = table.outer_width
      overlap = False
      
      for i in range(y_anchor, len(self.matrix)):
        row = self.matrix[i, x_anchor:x_anchor+outer_width]
        
        if len(row[pd.notna(row)]) > 0:
          overlap = True
          break
        
      if not overlap:
        result = table.append(data)

      if result:
        break

    return result

  def format(self):
    pass
