import re
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from utils import find_word_index, find_first_char_index


def find_nouns(text: None):
    result = {}
    tokens = nltk.word_tokenize(text)
    nouns = [word for (word, pos) in nltk.pos_tag(tokens) if(pos[:2] == 'NN')]

    for noun in nouns:
        splitted_nouns = re.split(r'\s+|[,;.-]\s*', noun)
        for spl_noun in splitted_nouns:
            if spl_noun in result.keys():
                indexes = find_word_index(text, spl_noun, one_based=True)
                result[spl_noun] = list(set(indexes) | set(result[spl_noun]))
                continue
            result[spl_noun] = find_word_index(text, spl_noun, one_based=True)

    return result
