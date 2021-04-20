from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, BooleanField
from wtforms.fields.html5 import TelField
from wtforms.validators import DataRequired


class HomeForm(FlaskForm):
    # email = EmailField('Почта', validators=[DataRequired()])
    # password = PasswordField('Пароль', validators=[DataRequired()])
    # remember_me = BooleanField('Запомнить меня')
    # submit = SubmitField('Войти')
    status = SubmitField("Заказ", validators=[DataRequired()])
    pass
