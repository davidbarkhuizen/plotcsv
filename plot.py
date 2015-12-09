# TODO
# - plot multiple series with shared x and y axes
# -- colour each series diff
# -- mark each series on legend


from datetime import datetime

# ---------------------------------------------------------
# config

import json

CONFIG_FILE_PATH = 'config/moore.json'

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

def load_csv_rows(source_path, start_date, end_date, date_col_name, timestamp_format):

	rows = []

	col_map = {}

	# codec required under python3 in order to strip BOM
	#
	with codecs.open(source_path, 'r', "utf-8-sig") as csv_file:
		
		csv_file.seek(0)
		reader = csv.reader(csv_file, delimiter = ',')

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

def line_plot_to_file(file_name, plt_domain, plt_ranges, title, domain_label, range_label, fore_color='white', back_color='black'):

	fig = plt.figure()
	ax1 = fig.add_subplot(111, axisbg=back_color)

	'''
	ax1.scatter(x[:4], y[:4], s=10, c='b', marker="s", label='first')
	ax1.scatter(x[40:],y[40:], s=10, c='r', marker="o", label='second')
	plt.legend(loc='upper left');
	plt.show()
	'''
	lines_plots = []

	for (plt_range_name, plt_range) in plt_ranges:
		line_plot = ax1.plot(plt_domain, plt_range, label=plt_range_name)
		lines_plots.append(line_plot)

	plt.title(title, color=fore_color)
	plt.ylabel(range_label, color=fore_color)
	plt.xlabel(domain_label, color=fore_color)

	plt.yticks(color=fore_color)
	plt.xticks(rotation=90, color=fore_color)

	# LEGEND

	# location
	#
	legend_ax1 = ax1.legend(loc='lower left') # ax.get_legend()
	
	# background color
	#
	legend_ax1.get_frame().set_facecolor(back_color)

	# text color
	#
	for text in legend_ax1.get_texts():
		text.set_color(fore_color)

	fig.savefig(file_name, bbox_inches='tight', facecolor=back_color)

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
	time_stamp_format = config['TimeStampFormat']
	col_map, rows = load_csv_rows(config['SourcePath'], start_date, end_date, date_col_name, time_stamp_format)

	# plot labels

	title = config['Title']

	# define plot data

	y1_col_names = config['SeriesY1']

	plt_domain = []

	plt_ranges = []
	for col in y1_col_names:
		plt_ranges.append((col, []))

	for row in rows:
		plt_domain.append(row[col_map[date_col_name]])
		
		for i in range(len(y1_col_names)):
			y1_series = y1_col_names[i]
			name, series = plt_ranges[i] 
			series.append(row[col_map[y1_series]])

	# plot

	file_name = title.replace(' ', '').replace('\n', '') + '.png'
	line_plot_to_file(file_name, plt_domain, plt_ranges, title, config['XLabel'], config['YLabel'])

main()