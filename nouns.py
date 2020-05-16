import re
import nltk

from itertools import groupby
from operator import itemgetter
from timeit import default_timer as timer
from utils import find_word_index, find_first_char_index

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


def find_nouns(text: None):
    result = {}
    tokens = nltk.word_tokenize(text)
    nouns = [word for (word, pos) in nltk.pos_tag(tokens) if (pos[:2] == 'NN')]

    for noun in nouns:
        splitted_nouns = re.split(r'\s+|[,;.-]\s*', noun)
        for spl_noun in splitted_nouns:
            if spl_noun in result.keys():
                indexes = find_word_index(text, spl_noun, one_based=True)
                result[spl_noun] = list(set(indexes) | set(result[spl_noun]))
                continue
            result[spl_noun] = find_word_index(text, spl_noun, one_based=True)

    return result


def find_compund_indexes(nouns_dict: dict):
    """

    :param nouns_dict: key = noun; value = list of indexes it appeeares in
    :return:
    """
    # Concatenate Indexes
    all_indexes = []
    for noun in nouns_dict:
        all_indexes = all_indexes + nouns_dict[noun]

    return all_indexes


def find_noun_compound(text: None):
    start = timer()
    result = {}
    tokens = nltk.word_tokenize(text)
    nouns = [word for (word, pos) in nltk.pos_tag(tokens) if (pos[:2] == 'NN')]

    for noun in nouns:
        splitted_nouns = re.split(r'\s+|[,;.-]\s*', noun)
        for spl_noun in splitted_nouns:
            if spl_noun in result.keys():
                indexes = find_word_index(text, spl_noun, one_based=True)
                result[spl_noun] = list(set(indexes) | set(result[spl_noun]))
                continue
            result[spl_noun] = find_word_index(text, spl_noun, one_based=True)

    indexes = find_compund_indexes(result)
    for _, g in groupby(enumerate(indexes), lambda ix: ix[0] - ix[1]):
        compound = list(map(itemgetter(1), g))
        if len(compound) == 1:
            continue
        result.append(compound)

    server_execution_time = timer() - start
    return result, server_execution_time


if __name__ == '__main__':
    dict = {
        "has": [1, 3, 7, 10, 12, 15, 17, 18, 20, 30, 40, 50, 60, 70, 80, 85, 90, 95],
        "eatten": [4, 5, 11, 16, 17, 18, 23, 31, 45, 55, 61, 62, 81, 86, 91, 96]
    }

    result = sorted(find_compund_indexes(dict))
    for k, g in groupby(enumerate(result), lambda ix: ix[0] - ix[1]):
        compound = list(map(itemgetter(1), g))
        if len(compound) == 1:
            continue
        print(compound)

    print('Elapsed time {:.6f}'.format())
