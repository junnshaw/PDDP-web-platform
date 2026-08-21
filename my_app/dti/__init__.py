from flask import Blueprint


dti = Blueprint('dti', __name__)

from . import view
