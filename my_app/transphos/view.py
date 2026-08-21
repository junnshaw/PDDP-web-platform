from my_app.main.view import index, result
# from docker_img.MolTrans_docker.scripts.models import Output
from flask import json, render_template,url_for,request,jsonify,session
import time
import os
import pandas as pd
from datetime import datetime
from my_app.product.models import start_backend_job
from my_app.config.my_settings import BaseConfig
import shutil
# from my_app import app
from . import transphos

basepath = BaseConfig.BASE_PATH
@transphos.route('/submittransphos',methods=['GET', 'POST'])
def submitMolecule():
    return render_template('submittransphos.html')

@transphos.route('/transphos_introduction',methods=['GET', 'POST'])
def transphos_introduction():
    return render_template('transphos_introduction.html')

@transphos.route('/smiles_submit_transphos',methods=['GET','POST'])
def submitsmiles():
    txt=request.form.get('txt')
    sites=request.form.get('sites')
    print("site",request.form)
    try:
        ip=str(request.remote_addr)
        session['ip']=ip
        TIMESTRING = datetime.now().strftime("%Y%m%d-%H.%M.%S.%f")
        print(TIMESTRING)
        session['time'] = TIMESTRING
        smiles_dir='tmp/input/%s/'%(TIMESTRING)
        ext_dir='tmp/ext/%s/'%(TIMESTRING)
        output_dir='tmp/output/%s/'%(TIMESTRING)
        conf_dir='tmp/conf/%s/'%(TIMESTRING)
        os.makedirs(os.path.join(basepath,smiles_dir),exist_ok=True)
        # os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,ext_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,output_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        shutil.copyfile(os.path.join(basepath, 'docker_img/transphos/conf/app.conf'),os.path.join(basepath,conf_dir,'app.conf'))
        with open(os.path.join(basepath,smiles_dir,'input.csv'),'w') as file:
            for line in txt:
                file.write(line)  
        with open(os.path.join(basepath,conf_dir,'app.conf'),'a') as file:
            file.write("\n")
            file.write(f"site={sites}")
        result,cmd=start_backend_job(basepath,'transphos.sh','%s'%(TIMESTRING),basepath,'%s'%(TIMESTRING))
        print(cmd)
    except Exception as e:
        result={'ok': False, 'result':str(e), 'error': str(e)}

    return jsonify(result)
