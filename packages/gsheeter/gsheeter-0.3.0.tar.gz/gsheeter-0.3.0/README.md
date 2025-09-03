# Google sheets API For Python3 v1

![main workflow](https://img.shields.io/github/actions/workflow/status/haydenkuk/gsheeter/main.yaml?logo=github)
![GitHub licence](https://img.shields.io/pypi/l/gsheeter?logo=github)
![GitHub downloads](https://img.shields.io/github/downloads-pre/haydenkuk/gsheeter/latest/total?logo=github)
![documentation](https://img.shields.io/readthedocs/gsheeter?logo=readthedocs)
![PyPi download](https://img.shields.io/pypi/dm/gsheeter?logo=pypi)
![PyPi version](https://img.shields.io/pypi/v/gsheeter?logo=pypi)
![python version](https://img.shields.io/pypi/pyversions/gsheeter?style=pypi)

Pandas-integrated, Auto-positioning library for Google Sheet API

Features:
- Auto-positioning for value updates on sheets
- Designed to minimize API calls
- Auto-parse values on sheet to get tables with positions and pd.DataFrame interpretations
- Multi-level indexes and columns supported

## 1. Installation
```sh
pip install gsheeter
```
Requires Python 3.9+.

## 2. Basic Usage

1. Authentication
(Only service account usage is allowed so far, I will develop functions to use other auth methods in the future)
```python
# using a service account will create a global api client for the project to use throughout
import gsheeter
filename = 'service-account.json' # add a path of your service account json file
gsheeter.service_account(filename)
```
2. Load spreadsheet
```python
from gsheeter import Drive

# 1. using fileId
fileId = 'spreadsheetFileId' # use the file id of the spreadsheet you want to access

spreadsheet = Drive.get_spreadsheet(fileId)

# 2. using filename
filename = 'spreadsheetFileName' # use the name of the spreadsheet you want to access
parentId = 'folderId' # use id of the parent folder of the spreadsheet above, I recommend using folderId when using filename, not fileId

spreadsheet = Drive.get_spreadsheet(
  target=filename,
  folderId=parentId)

```
3. Add(Create) spreadsheet
```python
from gsheeter import Drive

filename = 'yourspeadsheet' # use the name you want
sheetname = 'default' # default value is None, use only if you want to create the first sheet with a specific name
parentId = 'anyFolderId' # if empty, spreadsheet will be replaced in your root
spreadsheet = Drive.create_spreadsheet(
  filename=filename,
  sheetname=sheetname,
  parentId=parentId)

```

4. Load sheet
```python
from gsheeter import Drive


spreadsheet = Drive.get_spreadsheet(
  target='test',
  folderId='parentFolderId')

# 1. using sheetId
sheetId = 0
sheet = spreadsheet.get_sheet(sheetId)

# 2. using sheetname
sheetname = 'Sheet1'
sheet = spreadsheet.get_sheet(sheetname)
```

You can also use kwargs as follows when using Spreadsheet.get_sheet:
- delete_exist: bool = False: if the sheet being searched already exists and delete_exist is set to True, delete the existing sheet and create another one, otherwise, return the existing sheet
```python
# example
sheet = spreadsheet.get_sheet(sheetname, delete_exist=True)
```
- add: bool = True: if the sheet being searched does not exist, add one
```python
# example, throws exception if the sheet does not exist or is not added
sheet = spreadsheet.get_sheet(sheetname, add=False)
```

5. Add(Create) sheet
```python
from gsheeter import Drive

spreadsheet = Drive.get_spreadsheet(
  target='test',
  folderId='parentFolderId'
)

# default function behavior, Create a sheet with sheetname "Sheet1", 1000 rowCount and 26 columnCount and index of 0
sheet = spreadsheet.add_sheet()

# with a sheetname
sheetname = 'new_sheet'
sheet = spreadsheet.add_sheet(sheetname)

# create a smaller sheet with 100 rows and 10 columns
sheet = spreadsheet.add_sheet(
  sheetname=sheetname,
  rowCount=10,
  columnCount=10,
)
# after creating a new sheet named "new_sheet", with 10 rows and 10 columns
```
![Screenshot](doc_imgs/add_sheet_1.png)
![Screenshot](doc_imgs/add_sheet_2.png)

6. Read sheet values: entire sheet
```python
from gsheeter import Drive

fileId = 'fileId'
spreadsheet = Drive.get_spreadsheet(fileId)
sheetname = 'Sheet1'
sheet = spreadsheet.get_sheet(sheetname)
values = sheet.matrix # returns 2D np.ndarray filled with Values.
# If the sheet is empty, An empty np.ndarray with size of (sheet.rowCount, sheet.columnCount)
```
![Screenshot](doc_imgs/matrix_1.png)
![Screenshot](doc_imgs/matrix_2.png)

7. Read sheet values: tables
```python
from gsheeter import Drive

fileId = 'fileId'
spreadsheet = Drive.get_spreadsheet(fileId)
sheetname = 'Sheet1'
sheet = spreadsheet.get_sheet(sheetname)
tables = sheet.tables

for t in tables:
  print(t)
```

![Screenshot](doc_imgs/table_ex_1.png)
![Screenshot](doc_imgs/table_ex_2.png)

8. Read sheet values: a table
```python
from gsheeter import Drive

fileId = 'fileId'
spreadsheet = Drive.get_spreadsheet(fileId)
sheetname = 'Sheet1'
sheet = spreadsheet.get_sheet(sheetname)
table = sheet.table # by default, the first table(table #1) is assigned to sheet.table
```

9. Update values: using sheet
```python
from gsheeter import Drive

fileId = 'fileId'
spreadsheet = Drive.get_spreadsheet(fileId)
sheetname = 'Sheet1'
sheet = spreadsheet.get_sheet(sheetname)
```
```python
import numpy as np

# all coordinates follow array indexing convention, starting from 0
# gsheeter adds 1 to each coordinate to match cell address on sheet
# 1. set values of 2D np.ndarray with x, y coordinate on sheet
arr = np.zeros(shape=(4, 3))
y_offset = 0 # row 1
x_offset = 0 # column 1(A)
sheet.set_values(
  data=arr,
  y_offset=y_offset,
  x_offset=x_offset)
```
![Screenshot](doc_imgs/update_values_1.png)

```python
# 2. set values of 1D np.ndarray with x and y coordinate on sheet
arr = np.array([0,1,2,3,4])
y_offset = 1 # row 2
x_offset = 2 # column 3(C)
sheet.set_values(
  data=arr,
  y_offset=y_offset,
  x_offset=x_offset)
```
![Screenshot](doc_imgs/update_values_2.png)

```python
# 3. set values of pd.DataFrame with x and y coordinate on sheet
df = pd.DataFrame(...)
y_offset = 0
x_offset = 0
sheet.set_values(
  data=df,
  y_offset=y_offset,
  x_offset=x_offset)
```

```python
# 4. set values of pd.Series
row = pd.Series(...)
# default values of y_offset and x_offset are 0
# if the input to .set_values() is of type pd.Series, the output value is transposed.
sheet.set_values(row)
```
![Screenshot](doc_imgs/update_values_3.png)

```python
# 5. append values at the next row after the last non-empty row
# x_offset determines the index at which the search for non-empty row starts
arr = np.zeros(shape=(4, 3))
sheet.set_values(
  data=arr,
  x_offset=1, # searches for the next empty row after the last non-empty row starting from x coordinate of 1 to x coordinate of 1 + width of input data
  append=True)
```
![Screenshot](doc_imgs/update_values_4.png)
![Screenshot](doc_imgs/update_values_5.png)

```python
arr = np.zeros(shape=(4, 3))
sheet.set_values(
  data=arr,
  x_offset=1,
  y_offset=1, # paste the input data 1 index array along y-axis from the last-fill row
  append=True
)
```
![Screenshot](doc_imgs/update_values_4.png)
![Screenshot](doc_imgs/update_values_6.png)

10. Update values: replace values in a row of a table
```python
from gsheeter import Drive

fileId = 'fileId'
spreadsheet = Drive.get_spreadsheet(fileId)
sheet = spreadsheet.get_sheet('Sheet1')
table = sheet.table
row = table.df.iloc[2] # select third row from this table
row['x'] = 'test'
row['y'] = 'test'
table.update_row(row) # then update the values of the row
```
11. Update values: delete a row of a table
```python
from gsheeter import Drive

fileId = 'fileId'
spreadsheet = Drive.get_spreadsheet(fileId)
sheet = spreadsheet.get_sheet('Sheet1')
table = sheet.table

# delete second row
row = table.df.iloc[1]
table.delete_row(row)
```
12. Update values: delete a table
```python
from gsheeter import Drive

fileId = 'fileId'
spreadsheet = Drive.get_spreadsheet(fileId)
sheet = spreadsheet.get_sheet('Sheet1')
table = sheet.tables[2] # select third table in the sheet
sheet.delete_table(table)
sheet.delete_table(1) # you can also use table index
```


## Advanced Usage and Object structures

1. Drive
2. Spreadsheet
3. Sheet
4. Table

## Future updates
1. Chart
2. Other authentication methods
3. Cell format
