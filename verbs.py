import nltk


def find_index(text, word):
    word = word.lower()
    splitted = text.split()
    indexes = []

    for i in range(len(splitted)):
        if splitted[i].lower() == word:
            indexes.append(i+1)

    return indexes


def find_verbs(text: None):
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    result = {}
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    verbs = [tag[0] for tag in tagged if tag[1].startswith('V')]

    for verb in verbs:
        result[verb] = find_index(text, verb)

    return result


if __name__ == '__main__':
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    result = find_verbs("Ian has written over four hundred articles has written on the subject.")

    print("Done")
