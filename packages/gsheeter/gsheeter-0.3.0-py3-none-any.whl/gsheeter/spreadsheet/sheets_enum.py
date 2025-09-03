from enum import Enum

class SheetEnum(Enum):
  @classmethod
  def _missing_(cls, value):
    if isinstance(value, str):
      for member in cls:
        if member.name.lower() == value.lower():
          return member
    return super()._missing__(value) # type: ignore

class Dimension(SheetEnum):
  ROWS = 'ROWS'
  COLUMNS = 'COLUMNS'

class IndexType(SheetEnum):
  FIRST = 'FIRST'
  LAST = 'LAST'
