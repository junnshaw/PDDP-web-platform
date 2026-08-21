from flask import Blueprint


dnnxgb = Blueprint('dnnxgb', __name__)

from . import view
