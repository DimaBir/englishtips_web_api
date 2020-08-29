import os

from application import db, SERVER_PATH
from database import setupdatabase as db_utils


class ConfusedWord(db.Model):
    # MANUAL TABLE NAME CHOICE
    __tablename__ = 'confused_words'

    word = db.Column(db.Text, primary_key=True)
    note = db.Column(db.Text)

    def __init__(self, word, note):
        self.word = word
        self.note = note

    def __repr__(self):
        return f"Word: {self.word};  Note: {self.note}"


if __name__ == '__main__':
    if not os.path.isfile(SERVER_PATH):
        db_utils.setup_db()
