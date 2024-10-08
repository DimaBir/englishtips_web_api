import os
from os import listdir
from os.path import isfile, join

from app.utils import find_first_char_index


def find_wordiness(text):
    wordiness = {}
    wordiness_dict = {}
    wordiness_result = []

    original_text = text
    text = text.split()

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "wordiness")
    # path = "wordiness/"
    files = [f for f in listdir(path) if isfile(join(path, f))]

    for f in files:
        if f.startswith("Group"):
            wordiness[f] = (set(line.strip().lower() for line in open(join(path, f), "r", encoding="utf8")))

    # Fill wordiness dictionary
    for word in text:
        for key, values in wordiness.items():
            if word.lower() in values:
                wordiness_dict[word.lower()] = open(join(path, key.replace("Group", "Examples")), "r",
                                                    encoding="utf8").read()

    # Now find wordiness in text
    for word in list(set(text)):
        if word.lower() in wordiness_dict:
            # Finds indexes in the text
            indexes, length = find_first_char_index(original_text.lower(), word, one_based=False)
            dict = {
                "Wordiness": word,
                "Length": length,
                "Indexes": indexes,
                "Hint": wordiness_dict[word.lower()]
            }
            wordiness_result.append(dict)

    return wordiness_result


if __name__ == '__main__':
    result = find_wordiness("There are many students who like reading.")
