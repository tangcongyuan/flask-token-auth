from flask import (
    Blueprint,
    jsonify,
    make_response,
    request,
)
from werkzeug.security import check_password_hash
from models.user import User

import datetime
import jwt

JWT_SECRET = 'cytangssecret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_MINUTES = 30


auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1')


@auth_bp.route('/login', methods=['GET'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    
    userset = User.objects.raw({'username': {'$eq': auth.username}})
    if not userset.count():
        return jsonify(message='No user found.'), 404

    user = userset[0]
    if check_password_hash(user.password, auth.password):
        payload = {'user_uuid' : str(user.uuid),
                   'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXP_DELTA_MINUTES)}
        token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
        return jsonify(token=token.decode('UTF-8'))
    
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


@auth_bp.route('/check_token', methods=['GET'])
def check_token():
    if not 'Bearer' in request.headers['Authorization']:
        return jsonify(message='No Bearer token found in request headers.'), 401
    token = request.headers['Authorization'][len('Bearer '):]

    try:
        decoded = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        current_user = User.objects.raw({'_id': {'$eq': decoded['user_uuid']}}).first()
    except:
        return jsonify(message='Token not valid or expired.')
    
    return jsonify(user=current_user.to_son().to_dict())