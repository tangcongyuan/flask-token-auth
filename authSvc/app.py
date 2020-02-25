from flask import Flask, jsonify
from typing import Dict
from pymodm.connection import connect


__all__ = ['app']


def register_blueprints(app):
    from blueprints import auth_bp, user_bp
    app.register_blueprint(auth_bp.auth_bp)
    app.register_blueprint(user_bp.user_bp)


def init_db(app):
    connection_string = app.config['MONGO_URI']
    connect(connection_string, alias='cytang-flask-mongo')


def create_app(config: Dict=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = 'cytang',
        MONGO_URI = 'mongodb://localhost:27017/cytang-flask-mongo'
    )
    app.config.from_object(config)

    init_db(app)

    register_blueprints(app)

    return app


app = create_app()


@app.route('/api/v1/liveness')
def liveness_check():
    return jsonify(liveness=True), 200


if __name__ == '__main__':
    print(app.url_map)
    app.run(host='0.0.0.0',
            port=8080,
            debug=True)