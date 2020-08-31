import os

from database.models import ConfusedWord, db, SentenceStructure


def fill_database():
    file = open(os.path.join(os.path.dirname(__file__) + '/confused words.txt'), 'r')

    for line in file.readlines():
        lines_words = line.split()
        word = lines_words[0]
        note = lines_words[1:]

        # Lets return the list of words to aline wit a spaces between
        string = ''
        for item in note:
            string = string + item + ' '

        note = string.rstrip()

        # Add to db
        entry = ConfusedWord(word=word, note=note)

        db.session.add(entry)
        db.session.commit()

        print("Entry: Word: {}; Note: {} has been added to db".format(word, note))

    file = open(os.path.join(os.path.dirname(__file__) + '/sentence structure.txt'), 'r')

    for line in file.readlines():
        lines_words = line.split()
        word = lines_words[0]
        structure = lines_words[1:]

        # Lets return the list of words to aline wit a spaces between
        string = ''
        for item in structure:
            string = string + item + ' '

        structure = string.rstrip()

        # Add to db
        entry = SentenceStructure(word=word, structure=structure)

        db.session.add(entry)
        db.session.commit()

        print("Entry: Word: {}; Note: {} has been added to db".format(word, note))


if __name__ == '__main__':
    fill_database()
