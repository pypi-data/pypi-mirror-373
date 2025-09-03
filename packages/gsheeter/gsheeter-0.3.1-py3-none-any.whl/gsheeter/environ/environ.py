TABLE_FILLER = '-'
TABLE_BUFFER = '/'
FLOAT_FORMAT = '{:.2f}'
AUTOTYPING = True


def set_table_filler(val: str) -> None:
  global TABLE_FILLER
  TABLE_FILLER = val

def set_table_buffer(val: str) -> None:
	global TABLE_BUFFER
	TABLE_BUFFER = val

def set_float_format(val: str) -> None:
	global FLOAT_FORMAT
	FLOAT_FORMAT = val

def set_autotype(val: bool) -> None:
	global AUTOTYPING
	AUTOTYPING = val
