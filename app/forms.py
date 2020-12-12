from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class PredictForm(FlaskForm):

    sentence = StringField("Please, type sentence to check for wordiness.")
    submit = SubmitField("Check")
