from flask import Flask
from flask_restful import Api

from config import FlaskConfig
from database import db
from views.weather_data_view import GetWeatherData, Cities, Mean, MovingMean, Records


def create_app():
    """Application initialisation and configuration adding"""
    app = Flask(__name__)
    app.config.from_object(FlaskConfig)

    api = Api(app)
    api.add_resource(GetWeatherData, '/get_data')
    api.add_resource(Cities, '/cities')
    api.add_resource(Mean, '/mean')
    api.add_resource(MovingMean, '/moving_mean')
    api.add_resource(Records, '/records')

    db.init_app(app)
    db.create_all(app=app)

    return app, api


app, api = create_app()
