from flask import Flask, make_response, jsonify, request, render_template, redirect
import datetime
import re
from pprint import pprint

import pydantic
from flask import jsonify, abort, request, Blueprint, render_template, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from typing import List, Optional
import json
from forms.new_order import MakeOrderForm
from pydantic import validator
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
courier_fields = {'courier_id', 'courier_type', 'regions', 'working_hours'}
order_fields = {'order_id', 'weight', 'region', 'delivery_hours'}
c_type = {'foot': 10, 'bike': 15, 'car': 50}
rev_c_type = {10: 'foot', 15: 'bike', 50: 'car'}
kd = {10: 2, 15: 5, 50: 9}
CODE = 'zhern0206eskiy'
PATTERN = r = re.compile('.{2}:.{2}-.{2}:.{2}')


class CourierModel(pydantic.BaseModel):
    base: List[int]
    courier_id: int
    courier_type: str
    regions: List[int]
    working_hours: List[str]

    @validator('courier_type')
    def courier_type_should_be(cls, courier_type: str):
        if courier_type not in c_type:
            raise ValueError('courier_type should be "foot", "car" or "bike"')
        return courier_type

    @validator('working_hours')
    def wh_should_be(cls, working_hours: list):
        for wh in working_hours:
            if not PATTERN.match(wh):
                raise ValueError('invalid working hours format')
            if wh[2] != ':' or wh[5] != '-' or wh[8] != ':':
                raise ValueError('invalid separators')
            if not all(map(lambda x: x.isnumeric,
                           [wh[0], wh[1], wh[3], wh[4], wh[6], wh[7], wh[9], wh[10]])):
                raise ValueError('Hours/minutes should be integer')
            else:
                f1 = not 0 <= int(wh[0:2]) <= 23
                f2 = not 0 <= int(wh[3:5]) <= 59
                f3 = not 0 <= int(wh[6:8]) <= 23
                f4 = not 0 <= int(wh[9:11]) <= 59
                if f1 or f3:
                    raise ValueError('Hours should be between 0 and 23')
                if f2 or f4:
                    raise ValueError('Minutes should be between 0 and 59')
        return working_hours

    class Config:
        extra = 'forbid'


class EditCourierModel(pydantic.BaseModel):
    courier_id: Optional[int]
    courier_type: Optional[str]
    regions: Optional[List[int]]
    working_hours: Optional[List[str]]

    @validator('courier_type')
    def courier_type_should_be(cls, courier_type: str):
        if courier_type not in c_type:
            raise ValueError('courier_type should be "foot", "car" or "bike"')
        return courier_type

    @validator('working_hours')
    def wh_should_be(cls, working_hours: list):
        for wh in working_hours:
            if not PATTERN.match(wh):
                raise ValueError('invalid working hours format')
            if wh[2] != ':' or wh[5] != '-' or wh[8] != ':':
                raise ValueError('invalid separators')
            if not all(map(lambda x: x.isnumeric,
                           [wh[0], wh[1], wh[3], wh[4], wh[6], wh[7], wh[9], wh[10]])):
                raise ValueError('Hours/minutes should be integer')
            else:
                f1 = not 0 <= int(wh[0:2]) <= 23
                f2 = not 0 <= int(wh[3:5]) <= 59
                f3 = not 0 <= int(wh[6:8]) <= 23
                f4 = not 0 <= int(wh[9:11]) <= 59
                if f1 or f3:
                    raise ValueError('Hours should be between 0 and 23')
                if f2 or f4:
                    raise ValueError('Minutes should be between 0 and 59')
        return working_hours

    class Config:
        extra = 'forbid'


class OrderModel(pydantic.BaseModel):
    base: List[int]
    order_id: int
    weight: float
    region: int
    delivery_hours: List[str]

    class Config:
        extra = 'forbid'

    @validator('weight')
    def weight_should_be(cls, w: float):
        if not 0.01 <= w <= 50:
            raise ValueError('weight should be between 0.01 and 50')
        return w

    @validator('delivery_hours')
    def dh_should_be(cls, delivery_hours: list):
        for dh in delivery_hours:
            if not PATTERN.match(dh):
                raise ValueError('invalid working hours format')
            try:
                map(int, [dh[0], dh[1], dh[3], dh[4], dh[6], dh[7], dh[9], dh[10]])
            except ValueError:
                raise ValueError('Hours/minutes should be integer')
            if dh[2] != ':' or dh[5] != '-' or dh[8] != ':':
                raise ValueError('invalid separators')
            f1 = not 0 <= int(dh[0:2]) <= 23
            f2 = not 0 <= int(dh[3:5]) <= 59
            f3 = not 0 <= int(dh[6:8]) <= 23
            f4 = not 0 <= int(dh[9:11]) <= 59
            if f1 or f3:
                raise ValueError('Hours should be between 0 and 23')
            if f2 or f4:
                raise ValueError('Minutes should be between 0 and 59')
        return delivery_hours


def is_t_ok(l1, l2) -> bool:
    # format HH:MM - HH:MM
    time = [0] * 1440
    # print(list(l1) + list(l2))
    for h in list(l1) + list(l2):
        t = h.hours
        b1, b2 = t.split('-')
        a = b1.split(':')
        a = int(a[0]) * 60 + int(a[1])
        b = b2.split(':')
        b = int(b[0]) * 60 + int(b[1])
        time[a] += 1
        time[b + 1] -= 1
        # print(t, b1, b2, a, b, time[a], time[b + 1])
    # print('---------------------------')
    balance = 0
    for i in time:
        balance += i
        if balance >= 2:
            return True
    return False


def choose_orders(ords: list, maxw: int) -> list:
    try:
        n, w = len(ords), maxw * 100
        a = list(map(lambda x: int(x * 100), ords))
        c = list(map(lambda x: int(x * 100), ords))
        dp = [[(0, [])] + [(-1, [])] * w for i in range(n)]
        dp[0][0] = (0, [])
        dp[0][a[0]] = (c[0], [1])
        for i in range(1, n):
            for j in range(1, w + 1):
                dp[i][j] = dp[i - 1][j]
                if j - a[i] >= 0 and dp[i - 1][j - a[i]][0] != - 1:
                    if dp[i][j][0] < dp[i - 1][j - a[i]][0] + c[i]:
                        dp[i][j] = (dp[i - 1][j - a[i]][0] + c[i], dp[i - 1][j - a[i]][1] + [i + 1])
        ans = max(dp[-1])[1]
        return list(map(lambda x: x - 1, ans))
    except IndexError:
        return []


def parsing_about(text):
    try:
        t, rs, whs = text.split(';')
        return t, rs, whs
    except Exception:
        return False


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


@app.route('/couriers', methods=["POST"])
@login_required
def add_couriers():
    if current_user.user_type != 3:
        redirect('/')
        # TODO форма
    req_json = request.json['data']
    db_sess = db_session.create_session()
    already_in_base = [i.id for i in db_sess.query(Courier).all()]
    res = []
    bad_id = []
    is_ok = True
    # for i in range(len())
    # t, rs, ws = parsing_about(current_user.about)

    # req_json = [
    #     {'courier_id': max(already_in_base) + 1, 'courier_type': t, 'regions': rs,
    #      'working_hours': ws}
    # ]
    for courier_info in req_json:
        flag = False
        error_ans = []
        try:
            CourierModel(**courier_info, base=already_in_base)
        except pydantic.ValidationError as e:
            error_ans += json.loads(e.json())
            flag = True
        if courier_info['courier_id'] in already_in_base:
            error_ans += [
                {"loc": ["id"], "msg": "Invalid id: There is a courier with the same id",
                 "type": "value_error"}
            ]
        if flag or courier_info['courier_id'] in already_in_base:
            is_ok = False
            bad_id.append({"id": int(courier_info['courier_id']), 'errors': error_ans})
        if not is_ok:
            continue
        courier = Courier()
        courier.id = courier_info['courier_id']
        courier.maxw = c_type[courier_info['courier_type']]
        for i in list((courier_info['regions'])):
            reg = Region()
            reg.courier_id = courier.id
            reg.region = i
            db_sess.add(reg)
        for i in list(courier_info['working_hours']):
            wh = WH()
            wh.courier_id = courier.id
            wh.hours = i
            db_sess.add(wh)
        db_sess.add(courier)
        res.append({"id": courier_info['courier_id']})

    if is_ok:
        db_sess.commit()
        return jsonify({"couriers": res}), 201
    pprint({"validation_error": bad_id})
    print('-------------------------------------------------------------------------')
    return jsonify({"validation_error": bad_id}), 400


@app.route('/orders', methods=["POST", 'GET'])
@login_required
def add_orders():
    if current_user.user_type != 0:
        return redirect('/')
    form = MakeOrderForm()
    if form.validate_on_submit():
        req_json = []
        db_sess = db_session.create_session()
        res = []
        bad_id = []
        is_ok = True
        already_in_base = [i.id for i in db_sess.query(Order).all()]
        req_json.append({'order_id': max(already_in_base) + 1, 'weight': form.weight.data,
                         'region': form.region.data, 'delivery_hours': form.dh.data.split(';')})
        print(req_json[0]['delivery_hours'])
        for order_info in req_json:
            flag = False
            error_ans = []
            try:
                OrderModel(**order_info, base=already_in_base)
            except pydantic.ValidationError as e:
                error_ans += json.loads(e.json())
                flag = True
            if order_info['order_id'] in already_in_base:
                error_ans += [
                    {"loc": ["id"], "msg": "Invalid id: There is a order with the same id",
                     "type": "value_error"}
                ]
            if flag or order_info['order_id'] in already_in_base:
                is_ok = False
                bad_id.append({"id": int(order_info['order_id']), 'errors': error_ans})
            if not is_ok:
                continue
            order = Order()
            order.id = order_info['order_id']
            order.weight = order_info['weight']
            order.region = order_info['region']
            order.orders_courier = 0
            for i in list(order_info['delivery_hours']):
                dh = DH()
                dh.order_id = order.id
                dh.hours = i
                db_sess.add(dh)
            db_sess.add(order)
            res.append({"id": int(order_info['order_id'])})

        if is_ok:
            db_sess.commit()
            return render_template('result.html', u=str({"orders": res}))
            # return jsonify({"orders": res}), 201
        pprint({"validation_error": bad_id})
        print('-------------------------------------------------------------------------')
        return render_template('result.html', u=str({"validation_error": bad_id}))
        # return jsonify({"validation_error": bad_id}), 400
    return render_template('new_order.html', title='Новый заказ', form=form)


@app.route('/couriers/edit', methods=["PATCH"])
@login_required
def edit_courier():
    if current_user.user_type != 2:
        return redirect('/')
    courier_id = current_user.c_id
    db_sess = db_session.create_session()
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        return jsonify({'message': 'no courier with this id'}), 404
    req_json = request.json
    try:
        EditCourierModel(**req_json)
    except pydantic.ValidationError as e:
        print({'errors': json.loads(e.json())})
        return jsonify({'errors': json.loads(e.json())}), 400
    for k, v in dict(req_json).items():
        if k == 'courier_type':
            courier.maxw = c_type[v]
        elif k == 'regions':
            db_sess.query(Region).filter(Region.courier_id == courier.id).delete()
            for i in v:
                reg = Region()
                reg.courier_id = courier.id
                reg.region = i
                db_sess.add(reg)
        elif k == 'working_hours':
            db_sess.query(WH).filter(WH.courier_id == courier.id).delete()
            for i in v:
                wh = WH()
                wh.courier_id = courier.id
                wh.hours = i
                db_sess.add(wh)
    db_sess.commit()
    res = {'courier_id': courier_id, 'courier_type': rev_c_type[courier.maxw]}
    a = db_sess.query(WH).filter(WH.courier_id == courier.id).all()
    res['working_hours'] = [i.hours for i in a]
    b = [i.region for i in db_sess.query(Region).filter(Region.courier_id == courier.id).all()]
    res['regions'] = b
    for i in db_sess.query(Order).filter(Order.orders_courier == courier_id).all():
        dh = db_sess.query(DH).filter(DH.order_id == i.id).all()
        if i.complete_time:
            continue
        if i.region not in res['regions'] or not is_t_ok(dh, a):
            i.orders_courier = 0
    db_sess.commit()
    ords = list(db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                            Order.complete_time == '').all())
    for i in ords:
        i.orders_courier = 0
    db_sess.commit()
    courier.currentw = 0
    inds = choose_orders(list(map(lambda u: u.weight, ords)), courier.maxw)
    for i in inds:
        order = ords[i]
        courier.currentw += order.weight
        order.orders_courier = courier_id
    db_sess.commit()
    return jsonify(res), 200


@app.route('/couriers/get', methods=["GET"])
@login_required
def get_courier():
    if current_user.user_type != 2:
        return redirect('/')
    courier_id = current_user.c_id
    db_sess = db_session.create_session()
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    if request.method == 'GET':
        res = {'courier_id': courier_id, 'courier_type': rev_c_type[courier.maxw]}
        a = [i.hours for i in db_sess.query(WH).filter(WH.courier_id == courier.id).all()]
        res['working_hours'] = a
        b = [i.region for i in db_sess.query(Region).filter(Region.courier_id == courier.id).all()]
        res['regions'] = b
        if not db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                           Order.complete_time == '').all():
            courier.earnings += courier.last_pack_cost
            courier.last_pack_cost = 0
        res['earnings'] = courier.earnings
        if not courier.earnings:
            # return jsonify(res), 200
            return render_template('courier_info.html',
                                   t=res['courier_type'],
                                   wh=str(res['working_hours']),
                                   rs=str(res['regions']),
                                   earnings='-',
                                   rating='-'
                                   )
        try:
            t = min([i.summa / i.q
                     for i in db_sess.query(Region).filter(Region.courier_id == courier.id).all() if
                     i.q != 0])
        except ValueError:
            t = 60 * 60
        res['rating'] = round((60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5, 2)
        # return jsonify(res), 200
        return render_template('courier_info.html',
                               t=res['courier_type'],
                               wh=str(res['working_hours']),
                               rs=str(res['regions']),
                               earnings=str(res['earnings']),
                               rating=str(res['rating'])
                               )


@app.route('/orders/assign', methods=["POST", 'GET'])
@login_required
def assign_orders():
    if current_user.user_type != 2:
        return redirect('/')
    courier_id = current_user.c_id
    # courier_id = request.json['courier_id']
    db_sess = db_session.create_session()
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        return jsonify({'message': 'no courier with this id'}), 400
    ords = db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                       Order.complete_time == '').all()
    if ords:
        # print('didnt all task')
        res = [{'id': i.id} for i in ords]
        # return jsonify({'orders': res, 'assign_time': courier.last_assign_time}), 201
        return render_template('result.html',
                               u=str({'orders': res, 'assign_time': courier.last_assign_time}))
    courier_regions = [i.region for i in
                       db_sess.query(Region).filter(Region.courier_id == courier_id).all()]
    courier_wh = db_sess.query(WH).filter(WH.courier_id == courier_id).all()
    ords = db_sess.query(Order).filter((Order.orders_courier == 0),
                                       Order.region.in_(courier_regions)).all()
    ords = list(
        filter(lambda u: is_t_ok(db_sess.query(DH).filter(DH.order_id == u.id).all(), courier_wh),
               ords))
    inds = choose_orders(list(map(lambda u: u.weight, ords)), courier.maxw)
    for i in inds:
        order = ords[i]
        courier.currentw += order.weight
        order.orders_courier = courier_id

    db_sess.commit()

    res = [{'id': order.id} for order in
           db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                       '' == Order.complete_time)]
    if not res:
        return render_template('result.html', u=str({"orders": []}))
        # return jsonify({"orders": []}), 200
    courier.last_pack_cost = kd[courier.maxw] * 500
    # t = str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    t = str(datetime.datetime.utcnow().isoformat()) + 'Z'
    courier.last_assign_time = t
    assign_time = t
    if '' == courier.last_delivery_t:
        courier.last_delivery_t = assign_time
    db_sess.commit()
    return render_template('result.html', u=str({"orders": res, 'assign_time': str(assign_time)}))
    # return jsonify({"orders": res, 'assign_time': str(assign_time)}), 200


@app.route('/orders/complete/<order_id>', methods=["POST", 'GET'])
@login_required
def complete_orders(order_id):
    if current_user.user_type != 2:
        return redirect('/')
    # req_json = request.json
    db_sess = db_session.create_session()
    courier_id = current_user.c_id
    # courier_id = req_json['courier_id']
    # order_id = req_json['order_id']
    complete_t = str(datetime.datetime.utcnow().isoformat()) + 'Z'
    # complete_t = req_json['complete_time']
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    order = db_sess.query(Order).filter(Order.id == order_id).first()
    if not courier:
        # return jsonify({'message': 'no courier with this id'}), 400
        return render_template('result.html', u=str({'message': 'no courier with this id'}))
    if not order:
        # return jsonify({'message': 'no order with this id'}), 400
        return render_template('result.html', u=str({'message': 'no order with this id'}))
    if order.orders_courier != courier.id:
        # return jsonify({'message': 'courier and order don\'t match'}), 400
        return render_template('result.html', u=str({'message': 'courier and order don\'t match'}))
    db_sess.commit()
    reg = db_sess.query(Region).filter(
        Region.region == order.region, Region.courier_id == courier_id
    ).first()
    reg.q += 1
    u = datetime.datetime.fromisoformat(complete_t.split('.')[0])
    v = datetime.datetime.fromisoformat(courier.last_delivery_t.split('.')[0])
    courier.last_delivery_t = complete_t
    reg.summa += (u - v).total_seconds()
    if order.complete_time == '':
        courier.currentw -= order.weight
    order.complete_time = complete_t
    if not db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                       Order.complete_time == '').all():
        courier.earnings += courier.last_pack_cost
        courier.last_pack_cost = 0
    db_sess.commit()
    # return jsonify({'order_id': order.id}), 200
    return render_template('result.html', u=str({'order_id': order.id}))


@app.route('/test', methods=['GET'])
@login_required
def test():
    return render_template('go_home.html', u=current_user.name)
    # return jsonify({"test": 'connection is here'}), 201


def main():
    db_session.global_init("db/couriers.db")
    app.register_blueprint(shop_api.blueprint)
    app.run()
    # app.run(port=8080)
    # serve(app, host='127.0.0.1', port=8080)
    # app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
