#!/usr/bin/env python3

# server/app.py

from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Superheroes Code Challenge</h1>'

class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict() for hero in heroes], 200

class HeroByID(Resource):
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if hero:
            return hero.to_dict(rules=('hero_powers', 'hero_powers.power')), 200
        return {'error': 'Hero not found'}, 404

class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict() for power in powers], 200

class PowerByID(Resource):
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if power:
            return power.to_dict(), 200
        return {'error': 'Power not found'}, 404

    def patch(self, id):
        power = Power.query.filter_by(id=id).first()
        if not power:
            return {'error': 'Power not found'}, 404
        try:
            data = request.get_json()
            if 'description' in data:
                power.description = data['description']
            db.session.commit()
            return power.to_dict(), 200
        except ValueError as e:
            return {'errors': [str(e)]}, 400

class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(new_hero_power)
            db.session.commit()
            hero = Hero.query.filter_by(id=data['hero_id']).first()
            return hero.to_dict(rules=('hero_powers', 'hero_powers.power')), 201
        except ValueError as e:
            return {'errors': [str(e)]}, 400

api.add_resource(Heroes, '/heroes')
api.add_resource(HeroByID, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerByID, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
