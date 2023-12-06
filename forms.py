from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, validators


class ContactForm(FlaskForm):
    name = StringField(
        'Name',
        [validators.DataRequired(), validators.length(max=15)],
        render_kw={"placeholder": "Enter your name"},
    )
    email = StringField(
        'Email',
        [validators.DataRequired(), validators.Email()],
        render_kw={"placeholder": "Enter your email"},
    )
    question = TextAreaField(
        'Question',
        [validators.DataRequired()],
        render_kw={
            "placeholder": "Please, provide file number you are interested in"
        },
    )
    recaptcha = RecaptchaField()
