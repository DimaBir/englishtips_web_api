from application import db, SERVER_PATH
from database.models import ConfusedWord


def get_item(word: str) -> ConfusedWord:
    """
    Gets Confused Word from DB by ID
    :param id: String of word to search for notes
    :return: returns ConfusedWord object
    """

    # SELECT BY ID #
    entry = ConfusedWord.query.get(word)
    print(f"Word: {entry.word}\nNote: {entry.note}")

    return entry
