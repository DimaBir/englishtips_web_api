from database.models import ConfusedWord, SentenceStructure


def get_confused_word_item(word: str) -> ConfusedWord:
    """
    Gets Confused Word from DB by ID
    :param word: String of word to search for notes
    :return: returns ConfusedWord object
    """

    # SELECT BY ID #
    entry = ConfusedWord.query.get(word)
    return entry


def get_sentence_structure_item(word: str) -> SentenceStructure:
    """
    Gets Confused Word from DB by ID
    :param word: String of word to search for notes
    :return: returns SentenceStructure object
    """

    # SELECT BY ID #
    entry = SentenceStructure.query.get(word)
    return entry