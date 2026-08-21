from flask import Blueprint


dnnxgb_p = Blueprint('dnnxgb_p', __name__)

from . import view
