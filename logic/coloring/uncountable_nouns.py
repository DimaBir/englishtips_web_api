import os
from app.utils import find_first_char_index


def find_uncountable_nouns(text=None):
    uncountable_nouns_dict = {}
    uncountable_nouns_result = []
    original_text = text
    text = text.split()
    path = os.path.abspath(os.path.dirname(__file__))
    # Creates uncountable nouns dictionary
    with open(os.path.join(path, '../uncountable_nouns.txt')) as file:
        for line in file:
            if len(line.strip()) == 0:
                continue
            line = line.split()
            noun = line[0]
            note = line[1:]
            uncountable_nouns_dict[noun.lower()] = ' '.join(note)

    # Now find nouns in dictionary
    for word in text:
        if word.lower() in uncountable_nouns_dict:
            # Finds indexes in the text
            indexes, length = find_first_char_index(original_text.lower(), word, one_based=False)
            dict = {
                "UncountableNoun": word,
                "Length": length,
                "Indexes": indexes
            }
            uncountable_nouns_result.append(dict)

    return uncountable_nouns_result


if __name__ == '__main__':
    print(find_uncountable_nouns("Vegetations is not very good but Underwears is better"))
