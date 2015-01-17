from __future__ import division
import hashlib
import re
from struct import *

from collections import defaultdict

from helpers import *

import lettersums_data

with open('pyramid/words.txt') as f:
    wordlist = set(word.upper().rstrip() for word in f.readlines())
m = hashlib.sha1()

with open('anagrams-0.txt') as f:
    anagrams_0 = set(word.upper().rstrip() for word in f.readlines())
with open('anagrams-1.txt') as f:
    anagrams_1 = set(word.upper().rstrip() for word in f.readlines())
with open('anagrams-2.txt') as f:
    anagrams_2 = set(word.upper().rstrip() for word in f.readlines())

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

caesar_shiftable = set()
most_common_letter_counts = {}
most_common_vowel_counts = {}
most_common_consonant_counts = {}
distinct_letter_counts = {}
distinct_vowel_counts = {}
distinct_consonant_counts = {}
match_wordlist_3_or_fewer = set()
sha_words = {}
start_vowel = set()
doubled_letter_1 = set()
doubled_letter_2_same = set()
doubled_letter_2_different = set()

for word in wordlist:
    double_found1, double_found2, double_found_same, double_found_different = doubledletter(word)
    if double_found1:
        doubled_letter_1.add(word)
    if double_found2:
        if double_found_same:
            doubled_letter_2_same.add(word)
        if double_found_different:
            doubled_letter_2_different.add(word)
    
    for shift in range(1,26):
        shifted = caesar(word, shift)
        if shifted in wordlist:
            caesar_shiftable.add(word)

    l, v, c = find_most_common_char_counts(word)
    most_common_letter_counts[word] = l
    most_common_vowel_counts[word] = v
    most_common_consonant_counts[word] = c

    l, v, c = find_unique_counts(word)
    distinct_letter_counts[word] = l
    distinct_vowel_counts[word] = v
    distinct_consonant_counts[word] = c

    m = hashlib.sha1(word.lower()).hexdigest()
    sha_words[word] = m

    if len(word) <= 3:
        match_wordlist_3_or_fewer.add(word.upper())

    if word[0] in 'aeiou'.upper():
        start_vowel.add(word)

have_anagrams = {True: anagrams_0, False: wordlist.difference(anagrams_0)}
have_anagrams_with_one = {True: anagrams_1, False: wordlist.difference(anagrams_1)}
have_anagrams_with_two = {True: anagrams_2, False: wordlist.difference(anagrams_2)}
can_caesar_shift = {True: caesar_shiftable, False: wordlist.difference(caesar_shiftable)}
starts_with_vowel = {True: start_vowel, False: wordlist.difference(start_vowel)}
have_doubled_letters = {True: doubled_letter_1, False: wordlist.difference(doubled_letter_1)}
have_same_doubled_letters = {True: doubled_letter_2_same, False: wordlist.difference(doubled_letter_2_same)}
have_different_doubled_letters = {True: doubled_letter_2_different, False: wordlist.difference(doubled_letter_2_different)}


def get_count(dataset):
    ret = {}
    for word in wordlist:
        ret[word] = find_nonoverlapping(word, dataset)
    return ret

country_count = get_count(match_country_codes)
postal_count = get_count(match_state_postal_codes)
element_count = get_count(match_chemical_element_symbols)
wordlist_count = get_count(match_wordlist_3_or_fewer)

# Parsers

has_at_least_anagram = re.compile(r'^Has at least one anagram that is also in the word list: (.*)')
can_be_combined_with_one_addtl_ltr = re.compile(r'^Can be combined with one additional letter to produce an anagram of something in the word list: (.*)')
can_be_combined_with_two_addtl_ltrs = re.compile(r'^Can be combined with two additional letters to produce an anagram of something in the word list: (.*)')
def parse_anagram(line):
    if 'anagram' in line:
        res = has_at_least_anagram.match(line)
        if res:
            return have_anagrams['YES' == res.group(1)]

        res = can_be_combined_with_one_addtl_ltr.match(line)
        if res:
            return have_anagrams_with_one['YES' == res.group(1)]

        res = can_be_combined_with_two_addtl_ltrs.match(line)
        if res:
            return have_anagrams_with_two['YES' == res.group(1)]

        assert False, 'Unknown anagram: %s' % line
    else:
        return None

parse_caesar_regex = re.compile(r'^Can be Caesar shifted to produce another word in the word list: (.+)')
def parse_caesar(line):
    res = parse_caesar_regex.match(line)
    if res:
        return can_caesar_shift['YES' == res.group(1)]
    else:
        return None

parse_common_regex = re.compile(r'^Most common (.+)\(s\) each a.+: (.+)')
def parse_common(line):
    res = parse_common_regex.match(line)
    if res:
        match_type = res.group(1)
        if match_type == 'letter':
            dataset = most_common_letter_counts
        elif match_type == 'vowel':
            dataset = most_common_vowel_counts
        elif match_type == 'consonant':
            dataset = most_common_consonant_counts
        else:
            assert False, 'Unknown location: %s' % res.group(1)
        lower, upper, percentage = helper_bounds(res.group(2))

        if percentage:
            dataset = {word: count/len(word)*100 for word, count in dataset.iteritems()}
        return [word for word, count in dataset.iteritems() if count >= lower and count <= upper]
    else:
        return None

parse_contains_regex = re.compile("^Contains: (.*)$")
def parse_contains(line):
    res = parse_contains_regex.match(line)
    if res:
        return [word for word in wordlist if res.group(1) in word]
    else:
        return None

parse_distinct_regex = re.compile(r'^Distinct (.+)s: (.+)')
def parse_distinct(line):
    res = parse_distinct_regex.match(line)
    if res:
        match_type = res.group(1)
        if match_type == 'letter':
            dataset = distinct_letter_counts
        elif match_type == 'vowel':
            dataset = distinct_vowel_counts
        elif match_type == 'consonant':
            dataset = distinct_consonant_counts
        else:
            assert False, 'Unknown location: %s' % res.group(1)
        lower, upper, percentage = helper_bounds(res.group(2))

        if percentage:
            dataset = {word: count/len(word)*100 for word, count in dataset.iteritems()}
        return [word for word, count in dataset.iteritems() if count >= lower and count <= upper]
    else:
        return None

parse_doubled_letters_1_regex = re.compile(r'^Contains at least one doubled letter: (.+)')
def parse_doubled_letters_1(line):
    res = parse_doubled_letters_1_regex.match(line)
    if res:
        return have_doubled_letters['YES' == res.group(1)]
    else:
        return None

parse_doubled_letters_2_same_regex = re.compile(r'^Contains at least two nonoverlapping occurrences of the same doubled letter: (.+)')
def parse_doubled_letters_2_same(line):
    res = parse_doubled_letters_2_same_regex.match(line)
    if res:
        return have_same_doubled_letters['YES' == res.group(1)]
    else:
        return None

parse_doubled_letters_2_different_regex = re.compile(r'^Contains at least two different doubled letters: (.+)')
def parse_doubled_letters_2_different(line):
    res = parse_doubled_letters_2_different_regex.match(line)
    if res:
        return have_different_doubled_letters['YES' == res.group(1)]
    else:
        return None

parse_end_regex = re.compile(r'^Ends with: (.+)')
def parse_end(line):
    res = parse_end_regex.match(line)
    if res:
        return [word for word in wordlist if word.endswith(res.group(1))]
    else:
        return None

words_keyboard_map = defaultdict(dict)
for word in wordlist:
    for dataset in ['qwertyuiop'.upper(), 'asdfghjkl'.upper(), 'zxcvbnm'.upper()]:
        words_keyboard_map[word][dataset] = sum(1 for c in word if c in dataset)

qwerty_keyboard_regex = re.compile(r'^Letters located in the (.+) row on a QWERTY keyboard: (.+)')
def parse_keyboard(line):
    res = qwerty_keyboard_regex.match(line)
    if res:
        match_type = res.group(1)
        if match_type == 'top':
            dataset = 'qwertyuiop'.upper()
        elif match_type == 'middle':
            dataset = 'asdfghjkl'.upper()
        elif match_type == 'bottom':
            dataset = 'zxcvbnm'.upper()
        else:
            assert False, 'Unknown location: %s' % res.group(1)
        lower, upper, percentage = helper_bounds(res.group(2))

        data = {word: sum(1 for c in word if c in dataset) for word in wordlist}
        if percentage:
            data = {word: count/len(word)*100 for word, count in data.iteritems()}
        return [word for word, count in data.iteritems() if count >= lower and count <= upper]
    else:
        return None

parse_length_regex = re.compile(r'^Length: (.+)')
def parse_length(line):
    res = parse_length_regex.match(line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        return [word for word in wordlist if len(word) >= lower and len(word) <= upper]
    else:
        return None

parse_marked_regex = re.compile(r'If you marked nonoverlapping (.*), you could mark at most: (.*)')
def parse_marked(line):
    res = parse_marked_regex.match(line)
    if res:
        match_type = res.group(1)
        if match_type == 'officially-assigned ISO 3166-1 alpha-2 country codes':
            dataset = country_count
        elif match_type == 'US state postal abbreviations':
            dataset = postal_count
        elif match_type == 'chemical element symbols (atomic number 112 or below)':
            dataset = element_count
        elif match_type == 'occurrences of words in the word list that are 3 or fewer letters long':
            dataset = wordlist_count
        else:
            assert False, 'Unknown marking: %s' % res.group(1)

        lower, upper, percentage = helper_bounds(res.group(2))

        if percentage:
            dataset = {word: count/len(word)*100 for word, count in dataset.iteritems()}
        return [word for word, count in dataset.iteritems() if count >= lower and count <= upper]
    else:
        return None

parse_scrabble_regex = re.compile(r'^Base Scrabble score: (.+)')
def parse_scrabble(line):
    res = parse_scrabble_regex.match(line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        dataset = {word: sum(scrabble_points[c.lower()] for c in word) for word in wordlist}
        return [word for word, score in dataset.iteritems() if score >= lower and score <= upper]
    else:
        return None

parse_sha1_regex = re.compile("^SHA-1 hash of lowercased word, expressed in hexadecimal, (.*)$")
parse_sha1_subres_startswith = re.compile(r'^starts with: ([0-9A-F]+)')
parse_sha1_subres_endswith = re.compile(r'^ends with: ([0-9A-F]+)')
parse_sha1_subres_contains = re.compile(r'^contains: ([0-9A-F]+)')
def parse_sha1(line):
    res = parse_sha1_regex.match(line)
    if res:
        subres = parse_sha1_subres_startswith.match(res.group(1))
        if (subres):
            g = subres.group(1).lower()
            return [word for (word, h) in sha_words.iteritems() if h.startswith(g)]

        subres = parse_sha1_subres_endswith.match(res.group(1))
        if (subres):
            g = subres.group(1).lower()
            return [word for (word, h) in sha_words.iteritems() if h.endswith(g)]

        subres = parse_sha1_subres_contains.match(res.group(1))
        if (subres):
            g = subres.group(1).lower()
            return [word for (word, h) in sha_words.iteritems() if g in h]

        assert False, 'Unknown SHA-1 matching: %s' % res.group(1)
    else:
        return None

parse_start_regex = re.compile(r'^Starts with: (.+)')
def parse_start(line):
    res = parse_start_regex.match(line)
    if res:
        return [word for word in wordlist if word.startswith(res.group(1))]
    else:
        return None

parse_start_vowel_regex = re.compile(r'^Starts with a vowel: (.+)')
def parse_start_vowel(line):
    res = parse_start_vowel_regex.match(line)
    if res:
        return starts_with_vowel['YES' == res.group(1)]
    else:
        return None

parse_sum_letters_regex = re.compile(r'^Sum of letters \(A=1, B=2, etc\): (.+)')
def parse_sum_letters(line):
    res = parse_sum_letters_regex.match(line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        result = []
        for letter_sum in range(lower, upper + 1):
            if letter_sum in lettersums_data.LETTERSUMS:
                result += lettersums_data.LETTERSUMS[letter_sum]
        return result
    else:
        return None

parse_sum_letters_divisible_regex = re.compile(r'^Sum of letters \(A=1, B=2, etc\) is divisible by ([0-9]): (.+)')
def parse_sum_letters_divisible(line):
    res = parse_sum_letters_divisible_regex.match(line)
    if res:
        divisor = int(res.group(1))
        divisible = 'YES' == res.group(2)

        result = []
        for letter_sum in lettersums_data.LETTERSUMS:
            if letter_sum % divisor == 0 and divisible:
                result += lettersums_data.LETTERSUMS[letter_sum]
            elif letter_sum % divisor != 0 and not divisible:
                result += lettersums_data.LETTERSUMS[letter_sum]
        return result
    else:
        return None

parse_vowels_regex = re.compile(r'^Vowels: (.+)')
def parse_vowels(line):
    res = parse_vowels_regex.match(line)
    if res:
        lower, upper, percentage = helper_bounds(res.group(1))

        dataset = {word: sum(1 for c in word if c in 'aeiou'.upper()) for word in wordlist}
        if percentage:
            dataset = {word: vowel_sum/len(word)*100 for word, vowel_sum in dataset.iteritems()}
        return [word for word, vowel_sum in dataset.iteritems() if vowel_sum >= lower and vowel_sum <= upper]
    else:
        return None

parse_word_divisible_regex = re.compile(r'^Word interpreted as a base 26 number \(A=0, B=1, etc\) is divisible by ([0-9]): (.+)')
def parse_word_divisible(line):
    res = parse_word_divisible_regex.match(line)
    if res:
        divisor = int(res.group(1))
        divisible = 'YES' == res.group(2)

        return [word for word in wordlist if (base26(word) % divisor == 0) == divisible]
    else:
        return None

parse_word_representation_regex = re.compile(r'^Word interpreted as a base 26 number \(A=0, B=1, etc\) is representable as (.+): (.+)')
parse_word_representation_exact_regex = re.compile(r'^Word interpreted as a base 26 number \(A=0, B=1, etc\) is exactly representable in (.+): (.+)')
def parse_word_representation(line):
    res = parse_word_representation_regex.match(line)
    if res:
        repr_type = res.group(1)
        representable = 'YES' == res.group(2)

        if repr_type == 'an unsigned 32-bit integer':
            return [word for word in wordlist if (len(bin(base26(word))[2:]) <= 32) == representable]
        elif repr_type == 'an unsigned 64-bit integer':
            return [word for word in wordlist if (len(bin(base26(word))[2:]) <= 64) == representable]
        else:
            assert False, 'Unknown representation: %s' % res.group(1)
    else:
        res = parse_word_representation_exact_regex.match(line)
        if res:
            repr_type = res.group(1)
            if repr_type == 'IEEE 754 single-precision floating point format':
                format_char = 'f'
            elif repr_type == 'IEEE 754 double-precision floating point format':
                format_char = 'd'
            else:
                assert False, 'Unknown format: %s' % res.group(1)
            representable = 'YES' == res.group(2)

            return [word for word in wordlist if (unpack(format_char, pack(format_char, base26(word)))[0] == base26(word)) == representable]
        else:
            return None

all_matchers = [
                parse_anagram,
                parse_caesar,
                parse_common,
                parse_contains,
                parse_distinct,
                parse_doubled_letters_1,
                parse_doubled_letters_2_same,
                parse_doubled_letters_2_different,
                parse_end,
                parse_keyboard,
                parse_length,
                parse_marked,
                parse_scrabble,
                parse_sha1,
                parse_start,
                parse_start_vowel,
                parse_sum_letters,
                parse_sum_letters_divisible,
                parse_vowels,
                parse_word_divisible,
                parse_word_representation,
]


# File processor

def process_file(fname, verbose=False, testword=None):
    if not fname:
        return []
    with open(fname) as f:
        lines = [line.rstrip() for line in f.readlines()]
    words = oldwords = None
    for line in lines:
        if not line:
            continue
        # TODO temporary, we don't understand properties yet
        if line.startswith('Has property') or line.startswith('This is a word with property') or line.startswith('This is NOT a word with property'):
            continue
        # TODO temporary, we don't understand colors yet
        if line.startswith('This word is associated with the color'):
            continue
        # TODO temporary, we don't understand concepts yet
        if line.startswith('This word is associated with the concept'):
            continue
        # Ignore these, they are from test files
        if line.startswith('True statements about') or line.startswith('Some statements that uniquely identify'):
            continue

        if verbose:
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
                words = words.intersection(set(res))
            break

        assert matched, "Line not matched: %s" % (line,)
        try:
            assert len(words) > 0, "Line removed all words: %s\n" % (line)
            if testword:
                assert testword in words, "Line removed test word %s: %s\n" % (testword, line)
        except AssertionError as e:
            if verbose:
                print 'ERROR! last words before it:'
                print oldwords
            raise e
        oldwords = words
    return words

