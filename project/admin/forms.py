from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class AddForm(FlaskForm):
    word = StringField('Confused Word:')
    definition = StringField('Definition:')
    submit = SubmitField('Add word')


class DelForm(FlaskForm):
     word = StringField('Confused Word to delete:')
     submit = SubmitField('Remove Word')
