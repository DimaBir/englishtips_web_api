import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')  # TODO: Ask do wee need to download it every time


def find_hypernyms(word: str):
    hypernyms = []
    synonyms_set = wordnet.synsets(word)

    if len(synonyms_set) > 0:
        cur_word = synonyms_set[0]
        for h in cur_word.hypernyms():
            for l in h.lemmas():
                if l.name() not in hypernyms:
                    hypernyms.append(l.name())

    return hypernyms


if __name__ == '__main__':
    hypernyms = find_hypernyms("green")
    print("Hypernyms: {0}".format(hypernyms))

