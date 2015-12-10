# TODO
# - plot multiple series with shared x and y axes
# -- colour each series diff
# -- mark each series on legend


from datetime import datetime

# ---------------------------------------------------------
# config

import json

CONFIG_FILE_PATH = 'config/s&p500.json'

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

	# log
	# - actual data range
	# - target range

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
			
	return col_map, rows

# ---------------------------------------------------------
# plot

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

def line_plot_to_file(file_name, 
	plt_domain, plt_ranges_y1, plt_ranges_y2, 
	title, domain_label, range_label, range_2_label = 'UnNamed', 
	fore_color='white', back_color='black', 
	major_grid = False):

	# matplotlib.rc('axes',edgecolor='red', facecolor='purple')

	fig = plt.figure()

	lines_plots = []

	xFormatter = mdates.DateFormatter('%y-%m-%d') # date_out_format

	# Primary Y Axis ----------------------------------

	ax1 = fig.add_subplot(111, axisbg=back_color)

	for (plt_range_name, plt_range, plt_colour) in plt_ranges_y1:
		line_plot = ax1.plot(plt_domain, plt_range, label=plt_range_name, color=plt_colour)
		lines_plots.append(line_plot)

	# legend
	#
	legend_ax1 = ax1.legend(loc='lower left') # ax.get_legend()
	legend_ax1.get_frame().set_facecolor(back_color)
	for text in legend_ax1.get_texts():
		text.set_color(fore_color)
	legend_ax1.get_frame().set_edgecolor(back_color)

	start_date = min(plt_domain)
	end_date = max(plt_domain)

	ax1.set_xlabel(domain_label, color=fore_color)  
	
	ax1.xaxis.set_major_formatter(xFormatter)
	plt.xticks(color=fore_color, rotation=90)

	ax1.set_ylabel(range_label, color=fore_color)
	plt.yticks(color=fore_color)

	ax1.tick_params(axis='x', colors=fore_color)
	ax1.tick_params(axis='y', colors=fore_color)

	# matplotlib.rc('axes', edgecolor='yellow')

	# Y Axis - 2

	ax2 = None

	if len(plt_ranges_y2) > 0:

		ax2 = ax1.twinx()

		for (plt_range_name, plt_range, plt_colour) in plt_ranges_y2:
			line_plot = ax2.plot(plt_domain, plt_range, label=plt_range_name, color=plt_colour)
			lines_plots.append(line_plot)

		'''
		for y_tick in ax2.get_yticklabels():
			y_tick.set_color(fore_color)
		'''

		ax2.ticklabel_format(axis='y', style='sci', color=fore_color)

		ax2.set_ylabel(range_2_label, color=fore_color)  

		# legend
		#
		legend_ax2 = ax2.legend(loc='lower right') # ax.get_legend()
		legend_ax2.get_frame().set_facecolor(back_color)
		legend_ax2.get_frame().set_edgecolor(back_color)

		for text in legend_ax2.get_texts():
			text.set_color(fore_color)

		ax2.tick_params(axis='y', colors=fore_color, labelcolor=fore_color)
		ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.3e'))

	# plot area edge
	#
	for child in ax1.get_children():
		if isinstance(child, matplotlib.spines.Spine):
			child.set_color(fore_color)
	if ax2:
		for child in ax2.get_children():
			if isinstance(child, matplotlib.spines.Spine):
				child.set_color(fore_color)
	
	# common

	plt.title(title, color=fore_color)

	# ------------------------------------
	# GRID LINES

	if major_grid:
		ax1.grid(b=True, which='major', color='grey') # linestyle='-'

	# ------------------------------------
	# SAVE TO FILE

	fig.savefig(file_name, bbox_inches='tight', facecolor=back_color)

# ---------------------------------------------------------
# run

def main():

	# load config

	config = load_config(CONFIG_FILE_PATH)

	# data

	date_col_name = config['DateColName']

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

	plt_domain = []

	y1_series = config['SeriesY1']
	plt_ranges_y1 = []
	for series in y1_series:
		plt_ranges_y1.append((series[0], [], series[1]))

	y2_series = config['SeriesY2']
	plt_ranges_y2 = []
	for series in y2_series:
		plt_ranges_y2.append((series[0], [], series[1]))

	for row in rows:
		plt_domain.append(row[col_map[date_col_name]])
		
		for i in range(len(plt_ranges_y1)):
			name, series, colour = plt_ranges_y1[i] 
			series.append(row[col_map[name]])

		for i in range(len(plt_ranges_y2)):
			name, series, colour = plt_ranges_y2[i] 
			series.append(row[col_map[name]])

	# plot

	output_path = config['OutputPath']

	out_file_name = title.replace(' ', '').replace('\n', '') + '.png'
	out_file_path = output_path + out_file_name

	line_plot_to_file(out_file_path, 
		plt_domain, plt_ranges_y1, plt_ranges_y2, 
		title, config['XLabel'], config['Y1Label'], config['Y2Label'], 
		major_grid = config["MajorGridLines"])

main()