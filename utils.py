import re


def find_word_index(text, word, one_based=False):
    word = word.lower()
    splitted = text.split()
    indexes = []

    for i in range(len(splitted)):
        if splitted[i].lower() == word:
            i = i + 1 if one_based else i
            indexes.append(i)

    return indexes


def find_first_char_index(text, word, one_based=False):
    word = word.lower()
    index_starts = 1 if one_based else 0
    indexes = [m.start() + index_starts for m in re.finditer(word, text)]

    return indexes, len(word)
