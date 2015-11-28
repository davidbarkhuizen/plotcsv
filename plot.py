from datetime import datetime

# ---------------------------------------------------------
# config

import json

CONFIG_FILE_PATH = 'config/gold.json'

def load_config(path):

	j = None

	with open(path) as f:
		text = f.read()
		j = json.loads(text)

	return j

# ---------------------------------------------------------
# csv data

import csv
import codecs

def load_csv_rows(source_path, start_date, end_date, date_col_name, val_col_name, timestamp_format = '%Y-%m-%d'):

	rows = []

	col_map = {}

	# codec required under python3 in order to strip BOM
	#
	with codecs.open(source_path, 'r', "utf-8-sig") as csv_file:
		
		dialect = csv.Sniffer().sniff(csv_file.read(1024))
		csv_file.seek(0)
		reader = csv.reader(csv_file, dialect)

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
				row_data.append(value)

			rows.append(row_data)
			
	return col_map, rows

# ---------------------------------------------------------
# plot

import matplotlib
import matplotlib.pyplot as plt

def line_plot_to_file(file_name, plt_domain, plt_range, title, domain_label, range_label, fore_color='white', back_color='black'):

	plt.subplot(111, axisbg=back_color)

	lines_plots = plt.plot(plt_domain, plt_range)
	line_plot = lines_plots[0]
	line_plot.set_color(fore_color)

	# plt.xlabel('time (s)', color='r')
	plt.title(title, color=fore_color)
	plt.ylabel(range_label, color=fore_color)
	plt.xlabel(domain_label, color=fore_color)

	plt.yticks(color=fore_color)
	plt.xticks(rotation=90, color=fore_color)

	plt.savefig(file_name, bbox_inches='tight', facecolor=back_color)

# ---------------------------------------------------------
# run

def main():

	# load config

	config = load_config(CONFIG_FILE_PATH)

	# data

	date_col_name = config['DateColName']
	val_col_name = config['ValColName']

	# data filter

	# '%Y-%m-%d'

	start_date = datetime.strptime(config['StartDate'], '%Y-%m-%d') 
	end_date = datetime.strptime(config['EndDate'], '%Y-%m-%d')

	# load & filter data

	# ALSO GET actual start, end dates from load_csv_rows
	col_map, rows = load_csv_rows(config['SourcePath'], start_date, end_date, date_col_name, val_col_name)

	# plot labels

	title = config['Title']

	# define plot data

	plt_domain = []
	plt_range = []

	for row in rows:
		plt_domain.append(row[col_map[date_col_name]])
		plt_range.append(row[col_map[val_col_name]])

	# plot

	file_name = title.replace(' ', '').replace('\n', '') + '.png'
	line_plot_to_file(file_name, plt_domain, plt_range, title, config['XLabel'], config['YLabel'])

main()