import re
import string

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

def find_nonoverlapping_recursive(word, dataset, i, _mem):
    if i >= len(word):
        return 0
    if _mem[i] != -1:
        return _mem[i]
    _mem[i] = 0

    found1 = found2 = found3 = False
    if word[i].upper() in dataset:
        found1 = True
    if i < len(word) - 1:
        if word[i:i+2].upper() in dataset:
            found2 = True
	if i < len(word) - 2:
		if word[i:i+3].upper() in dataset:
			found3 = True

    if found1:
        _mem[i] = max(_mem[i],find_nonoverlapping_recursive(word, dataset, i+1, _mem) + 1)
    if found2:
        _mem[i] = max(_mem[i],find_nonoverlapping_recursive(word, dataset, i+2, _mem) + 2)
    if found3:
        _mem[i] = max(_mem[i],find_nonoverlapping_recursive(word, dataset, i+3, _mem) + 3)
    
    _mem[i] = max(_mem[i], find_nonoverlapping_recursive(word, dataset, i+1, _mem))

    return _mem[i]

def find_nonoverlapping(word, dataset):
    _mem = [-1]*100
    find_nonoverlapping_recursive(word, dataset, 0, _mem)
    return _mem[0]

base26_alphabet = string.digits + string.ascii_uppercase[:16]
base26_table = string.maketrans(string.ascii_uppercase, base26_alphabet)
def base26(word):
    word = word.upper()
    return int(word.translate(base26_table), 26)

def caesar(plaintext, shift):
    alphabet = string.ascii_uppercase
    shifted_alphabet = alphabet[shift:] + alphabet[:shift]
    table = string.maketrans(alphabet, shifted_alphabet)
    return plaintext.translate(table)

def doubledletter(word):
    found1 = False
    found_char = set()
    found2 = False
    found_same = False
    found_different = False
    for i in range(len(word)-1):
        if word[i] == word[i+1]:
            i += 1
            c = word[i]
            if found1:
                found2 = True
                for x in found_char:
                    if c == x:
                        found_same = True
                    else:
                        found_different = True
                found_char.add(c)
            else:
                found1 = True
                found_char.add(c)
    return found1, found2, found_same, found_different

def find_most_common_char_counts(word):
    l = v = c = 0
    for letter in string.ascii_uppercase:
        count = sum(1 for k in word if k == letter)
        if l < count:
            l = count
        if letter in 'AEIOU':
            if v < count:
                v = count
        else:
            if c < count:
                c = count
    return l, v, c

def find_unique_counts(word):
    l = v = c = 0
    unique = ''.join(set(word))
    for ch in unique:
        for vowel in 'aeiou'.upper():
            if ch == vowel:
                v += 1
    for ch in unique:
        for consonant in 'bcdfghjklmnpqrstvwxyz'.upper():
            if ch == consonant:
                c += 1
    l = len(unique)
    return l, v, c
