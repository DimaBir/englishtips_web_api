from nltk.corpus import wordnet


def find_synonyms(word: str):
    synonyms = []
    antonyms = []

    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())

    return list(set(synonyms)), list(set(antonyms))


if __name__ == '__main__':
    synonyms, antonyms = find_synonyms("antonym")
    print("Synonyms: {0}\nAntonyms: {1}".format(synonyms, antonyms))

