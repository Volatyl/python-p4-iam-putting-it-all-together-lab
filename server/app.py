#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):

        data = request.get_json()

        if 'username' not in data or 'password' not in data:
            return {'error_message': 'Please provide a username and password.'}, 422

        user = User(username=data['username'],
                    password_hash=data['password'], bio=data['bio'], image_url=data['image_url'])

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return user.to_dict(), 201


class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            return user.to_dict(), 200
        return {}, 401


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 201

        return {'error': "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id', None)
            return {}, 204
        return jsonify({'error': 'Unauthorized'}), 401


class RecipeIndex(Resource):
    def get(self):
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.filter_by(id=user_id).first()

            recipes = [recipe.to_dict() for recipe in user.recipes]

            return recipes, 200

        return {"failed": "unauthorised"}, 401

    def post(self):
        if not session['user_id']:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()
        obj = {
            "title": data['title'],
            "instructions": data['instructions'],
            "minutes_to_complete": data['minutes_to_complete'],
            "user_id": session['user_id']
        }

        new = Recipe(**obj)

        db.session.add(new)
        db.session.commit()

        return new.to_dict(), 201


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
