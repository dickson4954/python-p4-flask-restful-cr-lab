#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = True

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get(self):
        response_dict_list = [n.to_dict() for n in Plant.query.all()]
        return make_response(jsonify(response_dict_list), 200)

    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({'error': 'No input data provided'}), 400)

        try:
            new_record = Plant(
                name=data['name'],
                image=data['image'],
                price=data['price'],
            )
            db.session.add(new_record)
            db.session.commit()
            response_dict = new_record.to_dict()
            return make_response(jsonify(response_dict), 201)
        except KeyError as e:
            return make_response(jsonify({'error': f'Missing field: {e}'}), 400)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

api.add_resource(Plants, '/plants')

class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if plant is None:
            return make_response(jsonify({'error': 'Plant not found'}), 404)

        response_dict = plant.to_dict()
        return make_response(jsonify(response_dict), 200)

api.add_resource(PlantByID, '/plants/<int:id>')
        

if __name__ == '__main__':
    app.run(port=5555, debug=True)
