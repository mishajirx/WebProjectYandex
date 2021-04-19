from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, BooleanField, StringField, IntegerField, FloatField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class MakeOrderForm(FlaskForm):
    weight = FloatField('Вес заказа', validators=[DataRequired()])
    region = IntegerField('Регион заказа', validators=[DataRequired()])
    dh = StringField('Часы доставки заказа', validators=[DataRequired()])
    submit = SubmitField('Сделать заказ')
