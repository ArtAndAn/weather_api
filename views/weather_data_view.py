import datetime

import requests
from flask import request
from flask_restful import Resource, abort
from numpy import average, convolve, ones
from werkzeug.exceptions import BadRequestKeyError

from database import db
from models import DayWeatherModel, CityModel


class GetWeatherData(Resource):
    """
    View for adding Weather data from OpenWeatherMap API to database (only GET method)
    """
    WEATHER_DATA_URL = 'https://api.openweathermap.org/data/2.5/onecall'
    CITIES_LOC = {
        'Kiev': (50.45, 30.52),
        'Lviv': (49.83, 24.02),
        'Odessa': (46.47, 30.73),
        'Kharkiv': (49.98, 36.25),
        'Dnepr': (48.45, 34.98)
    }

    def get(self):
        for city, location in self.CITIES_LOC.items():
            city_from_db = self.check_city_in_db(city)
            json_data = self.get_weather_json(location)

            for date_weather_data in json_data['daily'][1:]:
                self.add_weather_day_to_db(city_from_db, date_weather_data)
        db.session.commit()
        return {'result': 'created'}, 201

    def check_city_in_db(self, city: str):
        """
        Function for adding a new city to DB if its not there and
        returns CityModel for further use
        """
        if not CityModel.query.filter_by(name=city).first():
            new_city = CityModel(name=city)
            db.session.add(new_city)
            db.session.commit()
        city_from_db = CityModel.query.filter_by(name=city).first()
        return city_from_db

    def get_weather_json(self, location: tuple):
        """
        Function that makes request to OpenWeatherMap API for specified city location and
        returns json data from response
        """
        data = requests.get(
            url=self.WEATHER_DATA_URL,
            params={'lat': location[0],
                    'lon': location[1],
                    'units': 'metric',
                    'exclude': 'current,minutely,hourly,alerts',
                    'appid': '9f1c8469b3aaaddcdaa2f741558124f4'
                    }
        )
        json_data = data.json()
        return json_data

    def add_weather_day_to_db(self, city_from_db: CityModel, date_weather_data: dict):
        """
        Function for adding a single day weather data to DB
        """
        temp_list = date_weather_data['temp']
        new_weather_data = DayWeatherModel(
            city=city_from_db.id,
            date=datetime.date.fromtimestamp(date_weather_data['dt']),
            temp=round(average(list(temp_list.values())), 1),
            pcp=date_weather_data.get('rain', 0),
            clouds=date_weather_data['clouds'],
            pressure=date_weather_data['pressure'],
            humidity=date_weather_data['humidity'],
            wind_speed=date_weather_data['wind_speed']
        )
        db.session.add(new_weather_data)


class Cities(Resource):
    """
    View for showing all cities in DB (only GET method)
    """

    def get(self):
        return {'result': [city.name for city in CityModel.query.all()]}


class Mean(Resource):
    """
    View for showing mean value for specified in query params value type and city (only GET method)
    """

    def get(self):
        try:
            db_query, city_from_req, value_type_form_req = process_mean_data()
            mean_value = round(average([getattr(day, value_type_form_req) for day in db_query]), 1)
            return {'result': f'Mean for {value_type_form_req}={mean_value} for {city_from_req} city'}
        except BadRequestKeyError:
            abort(400, result='City or value type was not specified')
        except AttributeError:
            abort(400, message='City or value type is not valid')


class MovingMean(Resource):
    """
    View for showing moving mean value for specified in query params value type and city (only GET method)
    """

    def get(self):
        try:
            db_query, city_from_req, value_type_form_req = process_mean_data()
            data = [getattr(day, value_type_form_req) for day in db_query]
            moving_mean_average = round(average(convolve(data, ones((3,)) / 3, mode='valid')), 1)
            return {'result': f'Moving mean for {value_type_form_req}={moving_mean_average} for {city_from_req} city'}
        except BadRequestKeyError:
            abort(400, result='City or value type was not specified')
        except AttributeError:
            abort(400, result='City or value type is not valid')


class Records(Resource):
    """
    View for showing all records for dates range specified in query params (only GET method)
    """

    def get(self):
        try:
            city = request.args['city']
            start_dt = datetime.datetime.strptime(request.args['start_dt'], '%d-%m-%Y')
            end_dt = datetime.datetime.strptime(request.args['end_dt'], '%d-%m-%Y')
            if end_dt < start_dt or end_dt - start_dt > datetime.timedelta(days=7):
                raise ValueError
            db_query = DayWeatherModel.query.join(CityModel).filter(CityModel.name == city).filter(
                DayWeatherModel.date.between(start_dt - datetime.timedelta(days=1), end_dt)).all()
            return {'result': {datetime.date.strftime(day.date, '%d-%m-%Y'): day.as_dict() for day in db_query}}
        except BadRequestKeyError:
            abort(400, result='One of the query parameters is not specified')
        except ValueError:
            abort(400, result='Start or End date is not valid')


def process_mean_data():
    """
    Function for processing mean request query parameters
    Raises AttributeError if value type is not valid or database query is empty
    """
    value_types = ('temp', 'pcp', 'clouds', 'pressure', 'humidity', 'wind_speed')

    city_from_req = request.args['city']
    value_type_form_req = request.args['value_type']
    db_query = DayWeatherModel.query.join(CityModel).filter(CityModel.name == city_from_req).all()
    if value_type_form_req not in value_types or not db_query:
        raise AttributeError
    return db_query, city_from_req, value_type_form_req
