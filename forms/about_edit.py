from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class EditInfoForm(FlaskForm):
    courier_type = TextAreaField("Мой тип")
    regions = TextAreaField("Мои регионы")
    working_hours = TextAreaField("Мои рабочие часы")
    submit = SubmitField('Изменить')
