from os import listdir

print 'Warming up...'

from parsers import process_file

# Set up pyramid.

rows=125
cols=142

pyramid = [[None]*cols for i in range(rows)]


# Load in pyramid data.

print
print '---------------'
print 'Solving pyramid'
print '---------------'

for dirname in listdir('pyramid'):
    if dirname.startswith('row'):
        row = int(dirname[3:])
        for filename in listdir('pyramid/%s' % dirname):
            col = int(filename[(len(dirname) + 4):][:-4])
            pyramid[row][col] = process_file('pyramid/%s/%s' % (dirname, filename))
