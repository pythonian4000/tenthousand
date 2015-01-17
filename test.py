import argparse
from os import listdir

print 'Warming up...'

from parsers import process_file

_PARSER = argparse.ArgumentParser()
_PARSER.add_argument(
    '-v',
    help='Verbose',
    action='store_true')

detailed = {}
normal = {}


for filename in listdir('pyramid/examples'):
    with open('pyramid/examples/%s' % filename) as f:
        wordline = f.readline()
        word = wordline.rsplit(' ', 1)[1][:-2]
        if filename.startswith('detailed'):
            detailed[word] = 'pyramid/examples/%s' % filename
        elif filename.startswith('normal'):
            normal[word] = 'pyramid/examples/%s' % filename

parsed_args = _PARSER.parse_args()

print
print '-------------------------------------------'
print 'First test set: true statements about words'
print '-------------------------------------------'
for word in detailed:
    print
    print 'Testing %s...' % (word,)
    guess = process_file(detailed[word], verbose=parsed_args.v, testword=word)
    print '%d guesses' % (len(guess))
    assert word in guess
    assert len(guess) == 1

print
print '--------------------------------------------------------'
print 'Second test set: statements that uniquely identify words'
print '--------------------------------------------------------'
for word in normal:
    print
    print 'Testing %s...' % (word,)
    guess = process_file(normal[word], verbose=parsed_args.v, testword=word)
    print '%d guesses' % (len(guess))
    assert word in guess
    assert len(guess) == 1
