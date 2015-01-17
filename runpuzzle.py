import argparse
from os import listdir
import csv
import pprint

print 'Warming up...'

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

pyramid = [None for i in range(rows)]
pyramid_files = [['']*cols for i in range(rows)]

from parsers import process_file
from multiprocessing import Pool, cpu_count

# Load in pyramid data.

def process_all():
    print
    print '---------------'
    print 'Solving pyramid'
    print '---------------'

    files = []

    p = Pool(cpu_count())

    for dirname in listdir('pyramid'):
        if dirname.startswith('row'):
            row = int(dirname[3:])
            for filename in listdir('pyramid/%s' % dirname):
                
                col = int(filename[(len(dirname) + 4):][:-4])
                pyramid_files[row][col] = 'pyramid/%s/%s' % (dirname, filename)

    for row in range(rows):
        pyramid[row] = p.map(process_file, pyramid_files[row])
        
        with open('partial_results.txt', 'wb') as f:
            pprint.pprint(pyramid, f)
    
        print "Finished row %d" % row

    with open('output.csv', 'wb') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(pyramid)


def process_row(row):
    RESULTS = []
    for filename in listdir('pyramid/row%s' % row):
        print filename
        col = int(filename[(len('row%s' % row) + 4):][:-4])
        RESULTS.append((filename, process_file('pyramid/row%s/%s' % (row, filename))))
    RESULTS = sorted(RESULTS)
    sorted_answers = [list(r[1])[0] if len(r[1]) == 1 else str(len(r[1])) for r in RESULTS]
    print '\t'.join(sorted_answers)


parsed_args = _PARSER.parse_args()
if parsed_args.r and parsed_args.c:
    # Run for a single cell.
    words = process_file(
        'pyramid/row%s/row%s_col%s.txt' %
        (parsed_args.r, parsed_args.r, parsed_args.c))
    print words
elif parsed_args.r:
    # Run a single row.
    process_row(parsed_args.r)
else:
    process_all()
