from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class NewCourierForm(FlaskForm):
    couriers = SelectMultipleField(label='Хотят быть курьерами', coerce=int)
    submit = SubmitField('Принять на работу')
