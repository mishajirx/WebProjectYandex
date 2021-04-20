from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class EditAboutForm(FlaskForm):
    about = TextAreaField("О себе")
    submit = SubmitField('Изменить')
