class Config:
    DEBUG = False
    SECRET_KEY = 'superSECUREcipherTHATyouCANnotDECIPHER!'


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False


config = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)
