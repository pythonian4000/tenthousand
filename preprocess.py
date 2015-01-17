def anagrams(word):
    if len(word) < 2:
        yield word
    else:
        for i, letter in enumerate(word):
            if not letter in word[:i]:
                for j in anagrams(word[:i]+word[i+1:]):
                    yield j + letter

with open('pyramid/words.txt') as f:
    wordlist = set(word.upper().rstrip() for word in f.readlines())

print 'Anagrams on their own'
anagrams_0 = set()
for word in wordlist:
    for a in anagrams(word):
        if a in wordlist:
            anagrams_0.add(word + '/n')
            break
with open('anagrams-0.txt', 'w') as f:
    f.writelines(anagrams_0)

print 'Anagrams with one extra char'
anagrams_1 = set()
for word in wordlist:
    for i in range(ord('a'), ord('z')+1):
        for a in anagrams(word + chr(i)):
            if a in wordlist:
                anagrams_1.add(word + '/n')
                break
with open('anagrams-1.txt', 'w') as f:
    f.writelines(anagrams_1)

print 'Anagrams with two extra chars'
anagrams_2 = set()
for word in wordlist:
    for i in range(ord('a'), ord('z')+1):
        for j in range(ord('a'), ord('z')+1):
            for a in anagrams(word + chr(i) + chr(j)):
                if a in wordlist:
                    anagrams_2.add(word + '/n')
                    break
with open('anagrams-2.txt', 'w') as f:
    f.writelines(anagrams_2)
