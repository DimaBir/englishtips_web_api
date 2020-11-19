import nltk

from app.utils import find_word_index, find_first_char_index

nltk.download('punkt')  # TODO: Ask do wee need to download it every time
nltk.download('averaged_perceptron_tagger')


def find_verbs(text: None):
    result = {}
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    verbs = [tag[0] for tag in tagged if tag[1].startswith('V')]

    for verb in verbs:
        result[verb] = find_word_index(text, verb, one_based=True)

    return result


def find_verbs_per_char(text: None):
    result = []
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    verbs = [tag[0] for tag in tagged if tag[1].startswith('V') and len(tag[0]) > 1]

    for verb in verbs:
        indexes, length = find_first_char_index(text, verb, one_based=False)
        dic = {
            "Verb": verb,
            "VerbLength": length,
            "Indexes": indexes
        }
        if dic in result:
            continue
        result.append(dic)

    return result


if __name__ == '__main__':
    result = find_verbs("Ian has written over four hundred articles has written on the subject.")

    print("Done")
