import pandas as pd
import numpy as np
import datetime as dt
import re

DATETIME_TYPES = (
	dt.datetime,
	dt.timedelta,
	dt.date,
	dt.time,
	pd.Timestamp,
	np.datetime64,
)

DATETIME_REGEX = re.compile(r'^\d{1,4}[\-\/\.\s]{1,2}\d{1,4}[\-\/\.\s]{1,2}\d{1,4}.*\d{0,2}\:{0,1}\d{0,2}\:{0,1}\d{0,2}')
DIGIT_REGEX = re.compile(r'^\d+$')
NUM_REGEX = re.compile(r'^-?[\d,]+\.{0,1}[\d]*$')
PERC_REGEX = re.compile(r'^[\d\,]+\.{0,1}\d*\%{1}$')
