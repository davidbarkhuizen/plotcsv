import csv
import codecs
from datetime import datetime

from time import perf_counter

def load_csv_rows(source_path, start_date, end_date, date_col_name, timestamp_format):

	# log
	# - actual data range
	# - target range

	rows = []

	col_map = {}

	ts_file_open = perf_counter(); ts_file_close = None
	ts_parse_start = None; ts_parse_stop = None

	# codec required under python3 in order to strip BOM
	#	
	with codecs.open(source_path, 'r', "utf-8-sig") as csv_file:
		
		# csv_file.seek(0)
		reader = csv.reader(csv_file, delimiter = ',')

		ts_file_close = perf_counter()
		print('file read', ts_file_close - ts_file_open)

		ts_parse_start = perf_counter()

		header_skipped = False
		for row in reader:

			# handle header row
			#
			if not header_skipped:

				header_skipped = True
				
				col_count = len(row) 

				for i in range(col_count):

					col_name = row[i]
					col_map[col_name] = i

				continue
			
			timestamp = None
			try:
				timestamp = datetime.strptime(row[col_map[date_col_name]], timestamp_format)
			except KeyError as ke:
				print(col_map.keys())
				raise

			if start_date:
				if (timestamp < start_date):
					continue
			if end_date:
				if (timestamp > end_date):
					break

			row_data = []
			for j in range(col_count):
				value = row[j]
				if j == col_map[date_col_name]:
					value = datetime.strptime(value, timestamp_format)
				else:
					value = float(value)
				row_data.append(value)

			rows.append(row_data)

		ts_parse_stop = perf_counter()
		print('parse', ts_parse_stop - ts_parse_start)		
			
	return col_map, rows
