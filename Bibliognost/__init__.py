import json
import logging

from flask import Flask
from flask_login import LoginManager

from config import config
from dateparser import parse_epoch, format_age

login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'auth.login'

credentials = json.load(open('config.json', mode='r', encoding='UTF-8'))

from .models import AnonymousUser, Permission
login_manager.anonymous_user = AnonymousUser

from connection import PostgresConnection
db_connection = PostgresConnection(credentials)


def get_logger(name):
	logging.basicConfig(level=logging.DEBUG)
	return logging.getLogger(name)


def create_app(config_name):
	biblio_app = Flask(__name__)
	biblio_app.config.from_object(config[config_name])
	login_manager.init_app(biblio_app)
	db_connection.init_app(biblio_app)

	@biblio_app.context_processor
	def inject_template_vars():
		return dict(Permission=Permission, parse_epoch=parse_epoch, format_age=format_age)

	from .bibliognost import biblio as biblio_blueprint
	biblio_app.register_blueprint(biblio_blueprint)

	from .auth import auth as auth_blueprint
	biblio_app.register_blueprint(auth_blueprint)

	return biblio_app
