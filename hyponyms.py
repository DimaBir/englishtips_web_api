import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')  # TODO: Ask do wee need to download it every time


def find_hyponyms(word: str):
    hyponyms = []
    synonyms_set = wordnet.synsets(word)

    if len(synonyms_set) > 0:
        cur_word = synonyms_set[0]
        for h in cur_word.hyponyms():
            for l in h.lemmas():
                if l.name() not in hyponyms:
                    hyponyms.append(l.name())

    return hyponyms


if __name__ == '__main__':
    hyponyms = find_hyponyms("green")
    print("Hypernyms: {0}".format(hyponyms))

