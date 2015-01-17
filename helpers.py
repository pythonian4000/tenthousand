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
    for i,c in enumerate(word):
        if i == len(word) -1:
            break
        if c == word[i+1]:
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

def find_most_common_char_count(word, dataset):
    most_common = 0
    for letter in dataset:
        count = sum(1 for c in word if c == letter)
        if most_common < count:
            most_common = count
    return most_common