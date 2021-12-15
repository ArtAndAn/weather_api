class FlaskConfig:
    """App configuration"""
    DEBUG = True
    CSRF_ENABLED = True
    SECRET_KEY = 'H@hh#^7xh6hF9KX8k6*p6j8@7&XU+N(K6R)2MF6)r789n5@A2LB!(+PM!vkjmd&m'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///weather.db?uri=true'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
