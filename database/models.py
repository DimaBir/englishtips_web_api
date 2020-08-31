from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ConfusedWord(db.Model):
    # MANUAL TABLE NAME CHOICE
    __tablename__ = 'confused_words'

    word = db.Column(db.Text, primary_key=True)
    note = db.Column(db.Text)

    def __init__(self, word, note):
        self.word = word
        self.note = note

    def __repr__(self):
        return self.word, self.note


class SentenceStructure(db.Model):
    # MANUAL TABLE NAME CHOICE
    __tablename__ = 'sentence_structure'

    word = db.Column(db.Text, primary_key=True)
    structure = db.Column(db.Text)

    def __init__(self, word, structure):
        self.word = word
        self.structure = structure

    def __repr__(self):
        return self.word, self.structure


if __name__ == '__main__':
    pass
