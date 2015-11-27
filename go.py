import csv
from datetime import datetime
import matplotlib

import codecs

CONFIG_FILE_PATH = 'config.json'

import json

def load_json_config(path):

	j = None

	with open(path) as f:
		text = f.read()
		j = json.loads(text)

	return j

def load_csv_rows(source_path, start_date, end_date, date_col_name, val_col_name, timestamp_format = '%Y-%m-%d'):

	rows = []

	col_map = {}

	# codes required under python3 in order to strip BOM
	#
	with codecs.open(source_path, 'r', "utf-8-sig") as csv_file:
		
		dialect = csv.Sniffer().sniff(csv_file.read(1024))
		csv_file.seek(0)
		reader = csv.reader(csv_file, dialect)

		header_skipped = False
		for row in reader:

			if not header_skipped:
				header_skipped = True
				
				col_count = len(row) 

				for i in range(col_count):

					col_name = row[i]
					col_map[col_name] = i

				continue
			
			try:
				timestamp = datetime.strptime(row[col_map[date_col_name]], timestamp_format)
			except KeyError as ke:
				print(col_map.keys())

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
				row_data.append(value)

			rows.append(row_data)
			
	return col_map, rows


def main():

	config = load_json_config(CONFIG_FILE_PATH)

	title = config['Title']
	source_path = config['SourcePath']	
	start_date = datetime.strptime(config['StartDate'], '%Y-%m-%d') 
	end_date = datetime.strptime(config['EndDate'], '%Y-%m-%d')
	y_label = config['YLabel']

	date_col_name = config['DateColName']
	val_col_name = config['ValColName']

	file_name = title.replace(' ', '') + '.png'

	col_map, rows = load_csv_rows(source_path, start_date, end_date, date_col_name, val_col_name)

	plt_domain = []
	plt_range = []

	for row in rows:
		plt_domain.append(row[col_map[date_col_name]])
		plt_range.append(row[col_map[val_col_name]])

	import matplotlib.pyplot as plt

	plt.plot(plt_domain, plt_range)
	plt.title(title)
	plt.ylabel(y_label)
	plt.xticks(rotation=90)

	plt.savefig(file_name, bbox_inches='tight')

	plt.show()


main()