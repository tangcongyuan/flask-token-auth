from flask import (
    Blueprint,
    jsonify,
    request,
)
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User


user_bp = Blueprint('user', __name__, url_prefix='/api/v1')


@user_bp.route('/users', methods=['GET'])
def get_users():
    userset = User.objects.all() # jsonify cannot sericalize queryset objects
    users = [user.to_son().to_dict() for user in userset]
    return jsonify(users=users), 200


@user_bp.route('/users/<string:user_uuid>', methods=['GET'])
def get_user(user_uuid):
    userset = User.objects.raw({'_id': {'$eq': user_uuid}})
    if userset.count():
        return jsonify(user=user.to_son().to_dict())
    return jsonify(message='No user found.'), 404


@user_bp.route('/users/new', methods=['POST'])
def new_user():
    ''' Create User with json data passed in. '''
    data = request.get_json()
    userset = User.objects.raw({'email': {'$eq': data['email']}})
    if userset.count():
        return jsonify(message='Email already taken.',
                       user=userset.first().uuid), 409
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    user.save()
    return jsonify(user=str(user.uuid)), 201


@user_bp.route('/users/<string:user_uuid>', methods=['PATCH'])
def modify_user(user_uuid):
    userset = User.objects.raw({'_id': {'$eq': user_uuid}})
    if not userset.count():
        return jsonify(message=f'User with uuid: {user_uuid} not found.'), 404
    data = request.get_json()
    user = userset.first()
    user.patch(**data)
    return jsonify(user=user.to_son().to_dict()), 200


@user_bp.route('/users/<string:user_uuid>', methods=['DELETE'])
def delete_user(user_uuid):
    userset = User.objects.raw({'_id': {'$eq': user_uuid}})
    if not userset.count():
        return jsonify(message=f'User with uuid: {user_uuid} not found.'), 404
    user = userset[0]
    user.delete()
    return jsonify(user=str(user.uuid)), 200