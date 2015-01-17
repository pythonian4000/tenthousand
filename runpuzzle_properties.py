import argparse
from os import listdir
import csv
import pprint

from collections import defaultdict

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

#pyramid = [['']*cols for i in range(rows)]
#properties = [['']*cols for i in range(rows)]
prop_strings = defaultdict(list)

with open("partial_results.txt") as datafile:
    with open("partial_results.py", "wb") as outfile:
        outfile.write("results = ");
        outfile.write(datafile.read())

from partial_results import results



def process_file_properties(fname, testword=None):
    with open(fname) as f:
        lines = [line.rstrip() for line in f.readlines()]
    props = []
    for line in lines:
        if not line:
            continue
        # TODO temporary, we don't understand properties yet
        if line.startswith('Has property') or line.startswith('This is a word with property') or line.startswith('This is NOT a word with property'):
            props.append(line)
        # TODO temporary, we don't understand colors yet
        if line.startswith('This word is associated with the color'):
            props.append(line)
        # TODO temporary, we don't understand concepts yet
        if line.startswith('This word is associated with the concept'):
            props.append(line)
        # Ignore these, they are from test files
        if line.startswith('True statements about') or line.startswith('Some statements that uniquely identify'):
            props.append(line)

    return props

def process_all():
    print
    print '---------------'
    print 'Solving pyramid'
    print '---------------'

    for dirname in listdir('pyramid'):
        if dirname.startswith('row'):
            row = int(dirname[3:])
            for filename in listdir('pyramid/%s' % dirname):
                col = int(filename[(len(dirname) + 4):][:-4])
                props = process_file_properties('pyramid/%s/%s' % (dirname, filename))

                for prop in props:
                    if results and results[row]:
                        prop_strings[prop].append(results[row][col])

            with open('property_results.txt', 'wb') as f:
                pprint.pprint(dict(prop_strings), f)
            print 'Finished row %s' % row


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
