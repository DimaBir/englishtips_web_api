import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')  # TODO: Ask do wee need to download it every time


def find_acronyms(word: str):
    acronym_result = ''
    definition = None

    synonyms_set = wordnet.synsets(word)
    if synonyms_set:
        acronyms = synonyms_set[0].name().split('.')[0].replace('_', ' ').split()
        for acronym in acronyms:
            acronym_result += acronym.capitalize() + ' '
        acronym_result = acronym_result.rstrip()
        definition = synonyms_set[0]._definition

    return acronym_result, definition


if __name__ == '__main__':
    word = "USA"
    acronym_str, definition_str = find_acronyms(word)
    print(f"\nWord: {word}\nAcronym: {acronym_str}; \nDefinition: {definition_str}\n")

    word = "WHO"
    acronym_str, definition_str = find_acronyms(word)
    print(f"Word: {word}\nAcronyms: {acronym_str}; \nDefinition: {definition_str}\n")

    word = "IDF"
    acronym_str, definition_str = find_acronyms(word)
    print(f"Word: {word}\nAcronyms: {acronym_str}; \nDefinition: {definition_str}\n")
