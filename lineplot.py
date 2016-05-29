import sys
if (sys.version_info < (3, 0)): raise Exception("!python3")

from time import perf_counter

# TODO
# plot series from 2 diff CSV files, with common x date axis
# allow mapping of series name

# ---------------------------------------------------------
# command line optionss

import argparse

def get_command_line_options():

	parser = argparse.ArgumentParser(prog='plotcsv - plot csv time series with python & matplotlib')

	parser.add_argument('--config_file_path', help='config file path', required=True)

	values = parser.parse_args()

	options = {}
	options['config_file_path'] = values.config_file_path

	return options

# ---------------------------------------------------------
# config

import json

def load_config(path):

	j = None

	with open(path) as f:
		text = f.read()
		j = json.loads(text)

	return j

# ---------------------------------------------------------
# CSV

from loadcsv import load_csv_rows

# ---------------------------------------------------------
# plot

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

from datetime import datetime

def line_plot_to_file(file_name, 
	plt_domain, plt_ranges_y1, plt_ranges_y2, 
	date_out_format,
	title, domain_label, y_axis_1, y_axis_2,
	font_size_large,
	fore_color='white', back_color='black',  
	major_grid = False):

	# matplotlib.rc('axes',edgecolor='red', facecolor='purple')

	ts_plot_start = perf_counter(); ts_plot_end = None;

	fig = plt.figure()

	lines_plots = []

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

	ax1.set_xlabel(domain_label, color=fore_color, fontsize=font_size_large)  

	xFormatter = mdates.DateFormatter(date_out_format)
	ax1.xaxis.set_major_formatter(xFormatter)
	plt.xticks(color=fore_color, rotation=90)

	y_axis_1_label, y_axis_1_precision = y_axis_1 

	ax1.set_ylabel(y_axis_1_label, color=fore_color, fontsize=font_size_large)
	plt.yticks(color=fore_color)

	ax1.tick_params(axis='x', colors=fore_color)
	ax1.tick_params(axis='y', colors=fore_color)

	ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.' + str(y_axis_1_precision) + 'e'))

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

		y_axis_2_label, y_axis_2_precision = y_axis_2

		ax2.set_ylabel(y_axis_2_label, color=fore_color, fontsize=font_size_large)  

		# legend
		#
		legend_ax2 = ax2.legend(loc='lower right') # ax.get_legend()
		legend_ax2.get_frame().set_facecolor(back_color)
		legend_ax2.get_frame().set_edgecolor(back_color)

		for text in legend_ax2.get_texts():
			text.set_color(fore_color)

		ax2.tick_params(axis='y', colors=fore_color, labelcolor=fore_color)
		ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.' + str(y_axis_2_precision) + 'e'))

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

	plt.title(title, color=fore_color, fontsize=font_size_large)

	# ------------------------------------
	# GRID LINES

	if major_grid:
		ax1.grid(b=True, which='major', color='grey') # linestyle='-'

	ts_plot_end = perf_counter();
	print('plot fig', ts_plot_end - ts_plot_start)


	# ------------------------------------
	# SAVE TO FILE

	ts_save_fig_start = perf_counter(); ts_save_fig_end = None;

	fig.savefig(file_name, bbox_inches='tight', facecolor=back_color)

	ts_save_fig_end = perf_counter();
	print('save fig to file', ts_save_fig_end - ts_save_fig_start)


# ---------------------------------------------------------
# run

DATE_FORMAT = '%Y-%m-%d'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def parse_as_date_or_date_time(s):
	
	dt = None
	try:
		dt = datetime.strptime(s, DATE_TIME_FORMAT)
	except Exception as e:
		try:
			dt = datetime.strptime(s, DATE_FORMAT)
		except Exception as ee:
			print(ee)
			raise ee
	finally:
		if dt:
			return dt
		else:
			raise Exception('date string "{0}" does not match either expected date "{1}" or datetime "{2}" formats'.format(s, DATE_FORMAT, DATE_TIME_FORMAT))

def main():

	# command line options
	#
	command_line_options = get_command_line_options()

	# load config
	#
	config_file_path = command_line_options['config_file_path']
	print('loading config file @ ' + config_file_path)
	config = load_config(config_file_path)

	# data

	start_date = parse_as_date_or_date_time(config['StartDate']) 
	end_date = parse_as_date_or_date_time(config['EndDate'])
	print('analysis period: %s - %s' % (start_date, end_date))

	# load & filter data

	# ALSO GET actual start, end dates from load_csv_rows
	#
	date_col_name = config['DateColName']
	time_stamp_format = config['TimeStampFormat']
	print('timestamp column: %s, format: %s' % (date_col_name, time_stamp_format))
	
	print()
	col_map, rows = load_csv_rows(config['SourcePath'], start_date, end_date, date_col_name, time_stamp_format)

	# plot labels
	#
	title = config['Title']

	# define plot data

	ts_construct_series_start = perf_counter(); ts_construct_series_end = None;
	
	plt_domain = []

	y1_series = config['SeriesY1']
	plt_ranges_y1 = []
	plt_range_y1_source_cols = []
	for (source_label, colour, display_label) in y1_series:
		plt_ranges_y1.append((display_label, [], colour))
		plt_range_y1_source_cols.append(source_label)

	y2_series = config['SeriesY2']
	plt_ranges_y2 = []
	plt_range_y2_source_cols = []
	for (source_label, colour, display_label) in y2_series:
		plt_ranges_y2.append((display_label, [], colour))
		plt_range_y2_source_cols.append(source_label)

	for row in rows:
		plt_domain.append(row[col_map[date_col_name]])
		
		for i in range(len(plt_ranges_y1)):
			name, series, colour = plt_ranges_y1[i]
			source_name = plt_range_y1_source_cols[i]			
			series.append(row[col_map[source_name]])

		for i in range(len(plt_ranges_y2)):
			name, series, colour = plt_ranges_y2[i]
			source_name = plt_range_y2_source_cols[i] 
			series.append(row[col_map[source_name]])

	ts_construct_series_end = perf_counter();
	print('construct series', ts_construct_series_end - ts_construct_series_start)

	# plot

	output_path = config['OutputPath']

	out_file_name = title.replace(' ', '').replace('\n', '') + '.png'
	out_file_path = output_path + out_file_name

	print('output file @ %s' % out_file_path)

	line_plot_to_file(
		out_file_path, 
		plt_domain, plt_ranges_y1, plt_ranges_y2, 
		config['DateOutFormat'],
		title, config['XLabel'], config['YAxis1'], config['YAxis2'], 
		config['FontSizeLarge'],
		major_grid = config["MajorGridLines"])

main()