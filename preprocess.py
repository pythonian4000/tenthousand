with open('pyramid/words.txt') as f:
    wordlist = set(word.upper().rstrip() for word in f.readlines())

anagrams_0 = set()
anagrams_1 = set()
anagrams_2 = set()
sorted_words_count = {}
for word in wordlist:
    sorted_word = ''.join(sorted(word))
    if sorted_words_count.has_key(sorted_word):
        sorted_words_count[sorted_word] += 1
    else:
        sorted_words_count[sorted_word] = 1
for word in wordlist:
    if sorted_words_count[''.join(sorted(word))] > 1:
        anagrams_0.add(word + '\n')
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for wildcard in letters:
        if sorted_words_count.has_key(''.join(sorted(word + wildcard))):
            anagrams_1.add(word + '\n')
        for wildcard2 in letters:
            if sorted_words_count.has_key(''.join(sorted(word + wildcard + wildcard2))):
                anagrams_2.add(word + '\n')
with open('anagrams-0.txt', 'w') as f:
    f.writelines(anagrams_0)
with open('anagrams-1.txt', 'w') as f:
    f.writelines(anagrams_1)
with open('anagrams-2.txt', 'w') as f:
    f.writelines(anagrams_2)
