from flask import Blueprint


ddi = Blueprint('ddi', __name__)

from . import view
