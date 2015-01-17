import argparse
from os import listdir
import csv

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
_PARSER.add_argument(
    '-v',
    help='Verbose',
    action='store_true')

# Set up pyramid.

rows=125
cols=142

pyramid = [[None]*cols for i in range(rows)]


# Load in pyramid data.

def process_all(verbose):
    print
    print '---------------'
    print 'Solving pyramid'
    print '---------------'

    for dirname in listdir('pyramid'):
        if dirname.startswith('row'):
            row = int(dirname[3:])
            for filename in listdir('pyramid/%s' % dirname):
                col = int(filename[(len(dirname) + 4):][:-4])
                try :
                    pyramid[row][col] = process_file('pyramid/%s/%s' % (dirname, filename), verbose=verbose)
                except AssertionError as e:
                    print 'ERROR at row %d col %d:' % (row, col)
                    raise e

    with open('output.csv', 'wb') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(pyramid)


parsed_args = _PARSER.parse_args()
if not parsed_args.r or not parsed_args.c:
    process_all(parsed_args.v)
else:
    # Run for a single cell.
    words = process_file(
        'pyramid/row%s/row%s_col%s.txt' %
        (parsed_args.r, parsed_args.r, parsed_args.c), verbose=parsed_args.v)
    print words
