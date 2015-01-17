from __future__ import division
import hashlib
from os import listdir
import re

with open('pyramid/words.txt') as f:
    wordlist = set(word.upper().rstrip() for word in f.readlines())
m = hashlib.sha1()
sha_words = {}
match_wordlist_3_or_fewer = set()

for word in wordlist:
    m = hashlib.sha1(word.lower()).hexdigest()
    sha_words[word] = m
    if len(word) <= 3:
        match_wordlist_3_or_fewer.add(word)

anagrams_0 = set()
anagrams_1 = set()
anagrams_2 = set()
with open('anagrams-0.txt') as f:
    anagrams_0 = set(word.upper().rstrip() for word in f.readlines())
with open('anagrams-1.txt') as f:
    anagrams_1 = set(word.upper().rstrip() for word in f.readlines())
with open('anagrams-2.txt') as f:
    anagrams_2 = set(word.upper().rstrip() for word in f.readlines())

have_anagrams = {True: anagrams_0, False: wordlist.difference(anagrams_0)}
have_anagrams_with_one = {True: anagrams_1, False: wordlist.difference(anagrams_1)}
have_anagrams_with_two = {True: anagrams_2, False: wordlist.difference(anagrams_2)}

with open('country-codes.txt') as f:
    match_country_codes = set(word.upper().rstrip() for word in f.readlines())
with open('USPS-state-codes.txt') as f:
    match_state_postal_codes = set(word.upper().rstrip() for word in f.readlines())
with open('chemical-elements.txt') as f:
    match_chemical_element_symbols = set(word.upper().rstrip() for word in f.readlines())

scrabble_points = {
    'a':  1, 'b':  3, 'c': 3, 'd': 2,
    'e':  1, 'f':  4, 'g': 2, 'h': 4,
    'i':  1, 'j':  8, 'k': 5, 'l': 1,
    'm':  3, 'n':  1, 'o': 1, 'p': 3,
    'q': 10, 'r':  1, 's': 1, 't': 1,
    'u':  1, 'v':  4, 'w': 4, 'x': 8,
    'y':  4, 'z': 10,
}


# Helper functions

def helper_bounds(bounds):
    lower = upper = 0;
    percentage = False

    res = re.match(r'^exactly ([0-9.]+)\%', bounds)
    res2 = re.match(r'^between ([0-9.]+)\% and ([0-9.]+)\% \(inclusive\)', bounds)
    if res:
        # A percentage
        lower = upper = float(res.group(1))
        percentage = True
    elif res2:
        # Also a percentage
        lower = float(res2.group(1))
        upper = float(res2.group(2))
        percentage = True
    else:
        # An absolute number or range
        res = re.match(r'^([0-9]+)', bounds)
        if res:
            lower = upper = int(res.group(1))
        else:
            res = re.match(r'^between ([0-9]+) and ([0-9]+) \(inclusive\)', bounds)
            if res:
                lower = int(res.group(1))
                upper = int(res.group(2))

    return lower, upper, percentage

def find_nonoverlapping(word, dataset, recurse):
    count = 0
    start = 0
    first_match = -1
    for end in range(1, len(word) + 1):
        if word[start:end].upper() in dataset:
            count += end - start
            start = end
            if first_match < 0:
                first_match = end

    if recurse and (first_match > 0):
        for i in range(1, first_match):
            subcount = find_nonoverlapping(word[i:], dataset, False)
            if subcount > count:
                count = subcount

    return count

def base26(word):
    word = word.upper()
    val = 0
    for i, c in enumerate(word):
        letter_val = ord(c) - ord('A')
        if i == len(word) - 1:
            val += letter_val
        else:
            val += 26**(len(word)-i-1) + letter_val
    return val


# Parsers

def parse_contains(line):
    res = re.match("^Contains: (.*)$", line)
    if res:
        result = []
        for word in wordlist:
            include = True
            for c in res.group(1):
                include = include and c in word
            if include:
                result.append(word)
        return result
    else:
        return None

def parse_anagram(line):
    if 'anagram' in line:
        res = re.match(r'^Has at least one anagram that is also in the word list: (.*)', line)
        if res:
            return have_anagrams['YES' == res.group(1)]

        res = re.match(r'^Can be combined with one additional letter to produce an anagram of something in the word list: (.*)', line)
        if res:
            return have_anagrams_with_one['YES' == res.group(1)]

        res = re.match(r'^Can be combined with two additional letters to produce an anagram of something in the word list: (.*)', line)
        if res:
            return have_anagrams_with_two['YES' == res.group(1)]

        assert False, 'Unknown anagram: %s' % line
    else:
        return None

def parse_common_letters(line):
    res = re.match(r'^Most common letter\(s\) each account\(s\) for: (.+)', line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        result = []
        for word in wordlist:
            most_common = 0
            for vowel in 'aeiou':
                count = sum(1 for c in word)
                if most_common < count:
                    most_common = count
            if percentage:
                most_common = most_common/len(word)*100
            if most_common >= lower and most_common <= upper:
                result.append(word)
        return result
    else:
        return None

def parse_common_vowels(line):
    res = re.match(r'^Most common vowel\(s\) each appear\(s\): (.+)', line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        result = []
        for word in wordlist:
            most_common = 0
            for vowel in 'aeiou':
                count = sum(1 for c in word if c == vowel)
                if most_common < count:
                    most_common = count
            if percentage:
                most_common = most_common/len(word)*100
            if most_common >= lower and most_common <= upper:
                result.append(word)
        return result
    else:
        return None

def parse_marked(line):
    res = re.match(r'If you marked nonoverlapping (.*), you could mark at most: (.*)', line)
    if res:
        match_type = res.group(1)
        if match_type == 'officially-assigned ISO 3166-1 alpha-2 country codes':
            dataset = match_country_codes
        elif match_type == 'US state postal abbreviations':
            dataset = match_state_postal_codes
        elif match_type == 'chemical element symbols (atomic number 112 or below)':
            dataset = match_chemical_element_symbols
        elif match_type == 'occurrences of words in the word list that are 3 or fewer letters long':
            dataset = match_wordlist_3_or_fewer
        else:
            assert False, 'Unknown marking: %s' % res.group(1)

        lower, upper, percentage = helper_bounds(res.group(2))

        result = []
        for word in wordlist:
            count = find_nonoverlapping(word, dataset, True)
            if percentage:
                count = count/len(word)*100
            if count >= lower and count <= upper:
                result.append(word)
        return result
    else:
        return None

def parse_scrabble(line):
    res = re.match(r'^Base Scrabble score: (.+)', line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        result = []
        for word in wordlist:
            score = sum(scrabble_points[c.lower()] for c in word)
            if score >= lower and score <= upper:
                result.append(word)
        return result
    else:
        return None

def parse_sha1(line):
    res = re.match("^SHA-1 hash of lowercased word, expressed in hexadecimal, (.*)$", line)
    if res:
        subres = re.match(r'^starts with: ([0-9A-F]+)', res.group(1))
        if (subres):
            g = subres.group(1).lower()
            return [word for (word, h) in sha_words.iteritems() if h.startswith(g)]

        subres = re.match(r'^ends with: ([0-9A-F]+)', res.group(1))
        if (subres):
            g = subres.group(1).lower()
            return [word for (word, h) in sha_words.iteritems() if h.endswith(g)]

        subres = re.match(r'^contains: ([0-9A-F]+)', res.group(1))
        if (subres):
            g = subres.group(1).lower()
            return [word for (word, h) in sha_words.iteritems() if g in h]

        assert False, 'Unknown SHA-1 matching: %s' % res.group(1)
    else:
        return None

def parse_sum_letters(line):
    res = re.match(r'^Sum of letters \(A=1, B=2, etc\): (.+)', line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        result = []
        for word in wordlist:
            letter_sum = sum(ord(c) - ord('A') + 1 for c in word)
            if letter_sum >= lower and letter_sum <= upper:
                result.append(word)
        return result
    else:
        return None

def parse_sum_letters_divisible(line):
    res = re.match(r'^Sum of letters \(A=1, B=2, etc\) is divisible by ([0-9]): (.+)', line)
    if res:
        divisor = int(res.group(1))
        divisible = 'YES' == res.group(2)

        result = []
        for word in wordlist:
            letter_sum = sum(ord(c) - ord('A') + 1 for c in word)
            if letter_sum % divisor == 0 and divisible:
                result.append(word)
            elif letter_sum % divisor != 0 and not divisible:
                result.append(word)
        return result
    else:
        return None

def parse_vowels(line):
    res = re.match(r'^Vowels: (.+)', line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        result = []
        for word in wordlist:
            vowel_sum = sum(1 for c in word if c in 'aeiou')
            if percentage:
                vowel_sum = vowel_sum/len(word)*100
            if vowel_sum >= lower and vowel_sum <= upper:
                result.append(word)
        return result
    else:
        return None

def parse_word_divisible(line):
    res = re.match(r'^Word interpreted as a base 26 number \(A=0, B=1, etc\) is divisible by ([0-9]): (.+)', line)
    if res:
        divisor = int(res.group(1))
        divisible = 'YES' == res.group(2)

        result = []
        for word in wordlist:
            word_num = base26(word)
            if word_num % divisor == 0 and divisible:
                result.append(word)
            elif word_num % divisor != 0 and not divisible:
                result.append(word)
        return result
    else:
        return None

all_matchers = [parse_contains,
                parse_anagram,
                parse_common_letters,
                parse_common_vowels,
                parse_marked,
                parse_scrabble,
                parse_sha1,
                parse_sum_letters,
                parse_sum_letters_divisible,
                parse_vowels,
                parse_word_divisible,
]


# File processor

def process_file(fname):
    with open(fname) as f:
        lines = [line.rstrip() for line in f.readlines()]
    words = None
    for line in lines:
        print line
        matched = 0
        for matcher in all_matchers:
            res = matcher(line)
            if res is None:
                continue
            matched = 1
            if words is None:
                words = set(res)
            else:
                if not set(res):
                    print 'About to fail. Last set of words:'
                    print words
                words = words.intersection(set(res))
            break
        assert matched, "Line %s not matched" % (line,)
    return words

print process_file("pyramid/row0/row0_col62.txt")


# Set up pyramid.

rows=125
cols=142

pyramid = [[None]*cols for i in range(rows)]


# Load in pyramid data.

pyramid_data = [[{}]*cols for i in range(rows)]

for dirname in listdir('pyramid'):
    if dirname.startswith('row'):
        row = int(dirname[3:])
        for filename in listdir('pyramid/%s' % dirname):
            col = int(filename[(len(dirname) + 4):][:-4])
            pyramid_data[row][col] = process_file('pyramid/%s/%s' % (dirname, filename))
