import nltk

from utils import find_word_index


def find_nouns(text: None):
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    result = {}
    tokens = nltk.word_tokenize(text)
    nouns = [word for (word, pos) in nltk.pos_tag(tokens) if(pos[:2] == 'NN')]

    for noun in nouns:
        result[noun] = find_word_index(text, noun, one_based=True)

    return result
