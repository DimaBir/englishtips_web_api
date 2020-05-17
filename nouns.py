import re
import nltk

from utils import find_word_index, find_first_char_index

nltk.download('punkt')  # TODO: Ask do wee need to download it every time
nltk.download('averaged_perceptron_tagger')


def find_nouns(text: None):
    result = {}
    tokens = nltk.word_tokenize(text)
    nouns = [word for (word, pos) in nltk.pos_tag(tokens) if (pos[:2] == 'NN')]

    for noun in nouns:
        splitted_nouns = re.split(r'\s+|[,;.-]\s*', noun)
        for spl_noun in splitted_nouns:
            if spl_noun in result.keys():
                indexes = find_word_index(text, spl_noun, one_based=False)
                result[spl_noun] = list(set(indexes) | set(result[spl_noun]))
                continue
            result[spl_noun] = find_word_index(text, spl_noun, one_based=True)

    return result


def find_compound_indexes(nouns_dict: dict):
    """

    :param nouns_dict: key = noun; value = list of indexes it appeeares in
    :return:
    """
    # Concatenate Indexes
    all_indexes = []
    for noun in nouns_dict:
        for index in nouns_dict[noun][0]:
            all_indexes.append((index, nouns_dict[noun][1]))

    return all_indexes


def find_noun_compound(text: None):
    result = {}
    noun_compound_indexes = []

    original_text = text
    text = text.replace(".", " . ").replace(",", " , ").lower()

    tokens = nltk.word_tokenize(text)
    nouns = list(set([word for (word, pos) in nltk.pos_tag(tokens) if (pos[:2] == 'NN')]))

    # Finds all occurrences of nouns in text
    for noun in nouns:
        indexes, length = find_first_char_index(original_text.lower(), noun, one_based=False)
        result[noun] = (indexes, length)

    # Sorts all indexes
    sorted_indexes = sorted(find_compound_indexes(result), key=lambda x: x[0])

    # Finds continuous indexes - noun-compounds
    # TODO: To function
    counter = 0
    prev_index = 0
    grouped_indexes = []

    for i in range(len(sorted_indexes)):
        current_index = sorted_indexes[i][0]  # the beginning of the word
        end_index = sorted_indexes[i][0] + sorted_indexes[i][1]  # the end of the word = current_index + length

        # If there are subwords of words, skip. Like: six-pack and pack => (48, 8) (52, 4)
        if current_index < prev_index:
            continue
        # If next word starts where the previous ends this is continuous nouns, that we are looking
        if counter < 1 or prev_index == current_index - 1:
            prev_index = end_index
            grouped_indexes.append((sorted_indexes[i][0], sorted_indexes[i][1]))
            counter = counter + 1
        # If there word that doesnt starts where previuos ends, check if we get noun_compound and reset variables
        else:
            # If we get two or more continious nouns, remeber them
            if counter >= 2:

                first = grouped_indexes[0][0]
                last = grouped_indexes[-1][0] + grouped_indexes[-1][1]

                noun_compound_indexes.append([first, last])

            # Reset all variables and keep looking
            counter = 0
            prev_index = end_index
            grouped_indexes.clear()
            continue

    return noun_compound_indexes

