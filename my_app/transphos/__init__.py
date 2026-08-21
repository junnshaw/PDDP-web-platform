from flask import Blueprint


transphos = Blueprint('transphos', __name__)

from . import view
