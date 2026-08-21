from flask import Blueprint


jtvae = Blueprint('jtvae', __name__)

from . import view
