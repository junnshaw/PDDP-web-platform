from flask import Flask
from my_app.config.my_settings import BaseConfig

app=Flask(__name__)
app.config.from_object(BaseConfig)
from my_app.main import main as main_blueprint
from my_app.transphos import transphos as transphos_blueprint
from my_app.dti import dti as dti_blueprint
from my_app.ddi import ddi as ddi_blueprint
from my_app.molflow import molflow as molflow_blueprint
from my_app.dnnxgb import dnnxgb as dnnxgb_blueprint
from my_app.dnnxgb_p import dnnxgb_p as dnnxgb_p_blueprint
from my_app.mda import mda as mda_blueprint
from my_app.jtvae import jtvae as jtvae_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(transphos_blueprint)
app.register_blueprint(dti_blueprint)
app.register_blueprint(ddi_blueprint)
app.register_blueprint(molflow_blueprint)
app.register_blueprint(dnnxgb_blueprint)
app.register_blueprint(dnnxgb_p_blueprint)
app.register_blueprint(mda_blueprint)
app.register_blueprint(jtvae_blueprint)