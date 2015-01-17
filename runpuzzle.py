import argparse
from os import listdir

print 'Warming up...'

from parsers import process_file

_PARSER = argparse.ArgumentParser()
_PARSER.add_argument(
    '-r',
    help='Row number of cell',
    type=str)
_PARSER.add_argument(
    '-c',
    help='Column number of cell',
    type=str)

# Set up pyramid.

rows=125
cols=142

pyramid = [[None]*cols for i in range(rows)]


# Load in pyramid data.

print
print '---------------'
print 'Solving pyramid'
print '---------------'

def process_all():
	for dirname in listdir('pyramid'):
	    if dirname.startswith('row'):
	        row = int(dirname[3:])
	        for filename in listdir('pyramid/%s' % dirname):
	            col = int(filename[(len(dirname) + 4):][:-4])
	            pyramid[row][col] = process_file('pyramid/%s/%s' % (dirname, filename))


parsed_args = _PARSER.parse_args()
if not parsed_args.r or not parsed_args.c:
	process_all()
else:
	process_file(
		'pyramid/row%s/row%s_col%s.txt' %
		(parsed_args.r, parsed_args.r, parsed_args.c))
