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
        return f"Word: {self.word};  Note: {self.note}"


if __name__ == '__main__':
    pass
