from database.utils import get_item
from database.models import ConfusedWord


def get_confused_word(word: str) -> ConfusedWord:
    """

    :param word:
    :return:
    """
    result = get_item(word)
    return result


if __name__ == '__main__':
    get_confused_word("dog")
