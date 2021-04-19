from flask import Flask, make_response, jsonify, request, render_template, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from data import db_session, shop_api
from forms.registration import RegisterForm
from data import db_session
from data.couriers import Courier
from data.orders import Order
from data.regions import Region
from data.workinghours import WH
from data.deliveryhours import DH
from data.users import User
from forms.login import LoginForm

# комент
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
x = 0
login_manager = LoginManager()
login_manager.init_app(app)

def hehe():
    print('hehe')

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@login_required
def start():
    return 'Start ' + current_user.name


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            user_type=form.user_type.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/couriers.db")
    app.register_blueprint(shop_api.blueprint)
    app.run()
    # app.run(port=8080)
    # serve(app, host='127.0.0.1', port=8080)
    # app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
