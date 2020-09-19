from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager

login_manager = LoginManager()
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


class UsefulPhrases(db.Model):
    # MANUAL TABLE NAME CHOICE
    __tablename__ = 'useful_phrases'

    word = db.Column(db.Text, primary_key=True)
    structure = db.Column(db.Text)

    def __init__(self, phrase, example):
        self.phrase = phrase
        self.example = example

    def __repr__(self):
        return self.phrase, self.example


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)

    password_hash = db.Column(db.String(128))

    def __init__(self, username, email, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)