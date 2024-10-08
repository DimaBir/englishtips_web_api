from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class PredictForm(FlaskForm):

    sentence = StringField("Please, type sentence to check for wordiness.")
    recaptcha = RecaptchaField()
    submit = SubmitField("Check")


class DatasetForm(FlaskForm):

    sentence = StringField("Please, enter the sentence, with dot at the end.",)
    label = SelectField(
        'Class:',
        [DataRequired()],
        choices=[
            ('1', 'Wordy'),
            ('0', 'Clear')
        ]
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("Add")
