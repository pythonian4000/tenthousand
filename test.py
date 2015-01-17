from os import listdir

from parsers import process_file

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

print '-------------------------------------------'
print 'First test set: true statements about words'
print '-------------------------------------------'
for word in detailed:
    guess = process_file(detailed[word])
    print '%s: %d guesses' % word, len(guess)
    assert word in guess
    assert len(guess) == 1

print
print '--------------------------------------------------------'
print 'Second test set: statements that uniquely identify words'
print '--------------------------------------------------------'
for word in normal:
    guess = process_file(normal[word])
    print '%s: %d guesses' % word, len(guess)
    assert word in guess
    assert len(guess) == 1