from database.utils import get_sentence_structure_item
from database.models import SentenceStructure


def get_sentence_structure(word: str) -> SentenceStructure:
    """

    :param word:
    :return:
    """
    result = get_sentence_structure_item(word)
    return result


if __name__ == '__main__':
    get_sentence_structure("dog")