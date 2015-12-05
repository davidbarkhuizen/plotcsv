'''
load text file of lines
for each line:
	find token
	if token is present, do replacement on line
save file
'''

file_path = ''

lines = []

with open(file_path, 'rt') as source_file:

	lines = source_file.read().split('\n')

# basic hygiene
#
lines = [line.replace('\r', '').replace('\n', '') for line in lines]

# transform

def transform(line):

	# skip header

	# Nov 27, 2015, ...

	columns = line.split(',')

	tail = columns[2:]

	date = columns[0] + ' ' + columns[1]
	mdy = date.split(' ')

	month_map = {
		"Jan" : 1,
		"Feb" : 2,
		"Mar" : 3,
		"Apr" : 4,
		"May" : 5,
		"June" : 6,
		"Jul" : 7,
		"Aug" : 8,
		"Sep" : 9,
		"Oct" : 10,
		"Nov" : 11,
		"Dec" : 12
	} 


	return s

lines = [transform(line) for line in lines]

transformed_text = '\n'.join(lines)

with open(file_path + '.out', 'wt') as dest_file:
	dest_file.write(transformed_text)