from flask import Blueprint


mda = Blueprint('mda', __name__)

from . import view
