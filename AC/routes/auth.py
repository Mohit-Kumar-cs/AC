from urllib import request
from flask import Blueprint
from flask import request, jsonify, make_response, url_for, redirect, abort
from AC.database.models import Attachments, Tacticals, User, WeaponAttachment, Weapons
from .. import db
import json
auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(name=data['name'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    token = user.encode_token()
    response = {
        'message': 'User registered successfully',
        'token': token.decode('UTF-8')
    }
    return jsonify(response), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token = user.encode_token()
        response = {
            'message': 'User logged in successfully',
            'token': token.decode('UTF-8')
        }
        return jsonify(response), 200
    else:
        response = {'message': 'Invalid email or password'}
        return jsonify(response), 401

@auth.route('/auth/facebook', methods=['POST'])
def facebook_login():
    data = request.get_json()
    facebook_data = data.facebook
    user = User.query.filter_by(facebook_id=facebook_data['id']).first()
    if user:
        token = user.encode_token()
        response = {
            'message': 'User logged in successfully with Facebook',
            'token': token.decode('UTF-8')
        }
        return jsonify(response), 200
    else:
        user = User.query.filter_by(email=facebook_data['email']).first()
        if user:
            user.facebook_id = facebook_data['id']
            db.session.commit()
            token = user.encode_token()
            response = {
                'message': 'User registered and linked with Facebook',
                'token': token.decode('UTF-8')
            }
            return jsonify(response), 201
        else:
            user = User(name=facebook_data['name'], email=facebook_data['email'], facebook_id=facebook_data['id'])
            db.session.add(user)
            db.session.commit()
            token = user.encode_token()
            response = {
                'message': 'User registered and logged in successfully with Facebook',
                'token': token.decode('UTF-8')
            }
            return jsonify(response), 201