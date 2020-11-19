import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import FileField, SubmitField


class UploadForm(FlaskForm):
    upload = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['zip', 'txt'], 'ZIP archive only!')
    ])
    submit = SubmitField('Upload')


def find_word_index(text, word, one_based=False):
    word = word.lower()
    splitted = text.split()
    indexes = []

    for i in range(len(splitted)):
        if splitted[i].lower() == word:
            i = i + 1 if one_based else i
            indexes.append(i)

    return indexes


def is_letter(text, index):
    if 'a' <= text[index] <= 'z' or 'A' <= text[index] <= 'Z':
        return True
    return False


def escape_special_characters(characters: list, text: str) -> str:
    for char in characters:
        text = text.replace(char, '\\' + char)

    return text


def find_first_char_index(text, word, one_based=False):
    word = word.lower()
    index_starts = 1 if one_based else 0
    indexes = []

    # Escapes special characters before regex
    escaped_text = escape_special_characters(["[", "]", "{", "}", "(", ")", "*", "<", ">", "?", "+"], text)
    # escaped_word = re.escape(word)

    # Find match and check if this whole word
    for m in re.finditer(word, escaped_text):
        start_index = m.start() + index_starts
        end_index = m.end() + index_starts
        # Its this is the first ord in string check end
        if start_index == 0 and end_index != len(text):  # Begin of string
            if is_letter(text, end_index):
                continue
        elif start_index != 0 and end_index == len(text):  # End of string
            if is_letter(text, start_index - 1):
                continue
        # elif start_index != 0 and end_index != len(text):  # Middle of the string
        #     if is_letter(text, start_index - 1) or is_letter(text, end_index):
        #         continue
        indexes.append(start_index)

    return indexes, len(word)
