from flask import Flask, make_response, jsonify, abort, request, blueprints
from data import db_session, shop_api
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
x = 0


@app.route('/')
def hello():
    return 'Hello go+ Misha'


def main():
    db_session.global_init("db/couriers.db")
    app.register_blueprint(shop_api.blueprint)
    # app.run(port=8080)
    serve(app, host='127.0.0.1', port=8080)
    # app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
