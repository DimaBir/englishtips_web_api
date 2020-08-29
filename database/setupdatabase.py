import os

from application import db, SERVER_PATH
from database.models import ConfusedWord


def fill_database():
    file = open('confused words.txt', 'r')

    for line in file.readlines():
        lines_words = line.split()
        word = lines_words[0]
        note = lines_words[1:]

        # Lets return the list of words to aline wit a spaces wetween
        string = ''
        for item in note:
            string = string + item + ' '

        note = string.rstrip()

        # Add to db
        entry = ConfusedWord(word=word, note=note)

        db.session.add(entry)
        db.session.commit()

        print("Entry: Word: {}; Note: {} has been added to db".format(word, note))


def setup_db():
    if not os.path.isfile(SERVER_PATH):
        db.create_all()
        fill_database()


if __name__ == '__main__':
    setup_db()

