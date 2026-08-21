from flask import Blueprint


molflow = Blueprint('molflow', __name__)

from . import view
