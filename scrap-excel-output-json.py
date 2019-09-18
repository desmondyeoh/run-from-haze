from datetime import datetime
import openpyxl
import requests
import re
from io import BytesIO

def prettify(x):
    return {
        'DK1 (280)': 'B_DK1',
        'DK2 (280)': 'B_DK2',
        'BK (75)':  'A_BK',
        'BK2 (30)': 'A_BK2',
        'BT1 (30)': 'B_BT1',
        'BT2 (30)': 'B_BT2',
        'BT3 (30)': 'B_BT3',
        'BT4 (30)': 'B_BT4',
        'BT5 (30)': 'B_BT5',
        'MM1 (50)': 'A_MM1',
        'MM2 (37)': 'A_MM2',
        'MM-CCNA (41)': 'A_CCNA',
        'ML (33)':  'A_ML',
        'iOS (18)': 'B_iOS',
        'MM6 (45)': 'B_MM6',
        'MS (40)':  'B_MS',
        'MM3 (60)': 'B_MM3',
        'MM4 (60)': 'B_MM4',
    }[x]

print('Beginning file download with requests')
url = 'http://jw.fsktm.um.edu.my/edit/data/jadualID.xlsx'
r = requests.get(url)
with open('jadualID.xlsx', 'wb') as f:
    f.write(r.content)

data = {}

wb = openpyxl.load_workbook('jadualID.xlsx', data_only=True)

for sheetname in wb.sheetnames:
    ws = wb[sheetname]
    data[sheetname] = []
    
    # Make dataframe
    df = pd.DataFrame(ws).applymap(lambda x: x.value)
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df = df.iloc[:18,:14]
    df = df.set_index(df.columns[0])
    
    # Format column and index
    df.columns = [datetime.strftime(datetime.strptime(col[:5].strip(), '%H.%M'), '%H%M') for col in df.columns]
    df.index = [prettify(s) for s in df.index.values]

    # Unmerge cells and fill the values
    merged_cell_ranges = list(map(lambda x: x.bottom, ws.merged_cells.ranges)) # get all merged cells
    merged_cell_ranges = np.array([(*x[0], *x[-1]) for x in merged_cell_ranges]) # get ranges
    merged_cell_ranges[:,[0,1]] = merged_cell_ranges[:,[0,1]] - 2 # excel -> pandas coord (r1-1,c2-1)
    merged_cell_ranges[:,[2,3]] = merged_cell_ranges[:,[2,3]] - 1 # excel -> pandas coord (c1-2)
    for r1,c1,r2,c2 in merged_cell_ranges:
        try:
            df.iloc[r1:r2, c1:c2] = df.iloc[r1, c1]
        except IndexError:
            pass
    
    # Get empty classes and append to data
    for time_idx, row in df.T.iterrows():
        empty_classes = row[row.isna()].index.values
        empty_classes = sorted(empty_classes)
        data[sheetname].append([time_idx, empty_classes])

import json

with open('output.json', 'w') as f:
    f.write(json.dumps(data))
    
