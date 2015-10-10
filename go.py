import csv
from datetime import datetime
import matplotlib

def load_csv_rows(path, start_date, end_date, timestamp_format = '%Y-%m-%d'):

	rows = []

	col_map = {}

	with open(source_path) as csv_file:
	    
	    dialect = csv.Sniffer().sniff(csv_file.read(1024))
	    csv_file.seek(0)
	    reader = csv.reader(csv_file, dialect)

	    header_skipped = False
	    for row in reader:

	    	if not header_skipped:
	    		header_skipped = True
	    		
	    		col_count = len(row) 

	    		for i in range(col_count):

	    			col_name = row[i].lower().strip()
	    			col_map[col_name] = i

	    		continue

	    	timestamp = datetime.strptime(row[col_map['date']], timestamp_format)

	    	if start_date:
	    		if (timestamp < start_date):
	    			continue
	    	if end_date:
	    		if (timestamp > end_date):
	    			break

	    	row_data = []
	    	for j in range(col_count):
	    		value = row[j]
	    		if j == col_map['date']:
	    			value = datetime.strptime(value, timestamp_format)
    			row_data.append(value)

    		rows.append(row_data)
	    	
	return col_map, rows

source_path = '/home/david/data/csv_data/equity_indices/^GSPC.csv'

start_date = datetime.strptime('2014-01-01', '%Y-%m-%d') 
end_date = None # datetime.strptime('2001-10-01', '%Y-%m-%d')4

col_map, rows = load_csv_rows(source_path, start_date, end_date)

plt_domain = []
plt_range = []

for row in rows:
	plt_domain.append(row[col_map['date']])
	plt_range.append(row[col_map['close']])

import matplotlib.pyplot as plt

plt.plot(plt_domain, plt_range)
plt.title('S&P500 Index')
plt.ylabel('Closing Price')
plt.show()



# load series - file path
# filter series - start, end - dates
# apply functions, producing plots for 1 x axis, 2 y axes (or 1 y axis) - with labels
# save to file

