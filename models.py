from database import db


class CityModel(db.Model):
    """Basic city model"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)


class DayWeatherModel(db.Model):
    """Single day weather model"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.Integer, db.ForeignKey(CityModel.id))
    date = db.Column(db.Date)
    temp = db.Column(db.Float, nullable=True)
    pcp = db.Column(db.Float, nullable=True)
    clouds = db.Column(db.Float, nullable=True)
    pressure = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    wind_speed = db.Column(db.Float, nullable=True)

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
