from flask import Blueprint

biblio = Blueprint('biblio', __name__)

from . import views, errors
