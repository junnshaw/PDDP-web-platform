from my_app.main.view import index, result
# from docker_img.MolTrans_docker.scripts.models import Output
from flask import json, render_template,url_for,request,jsonify,session
import time
import os
import pandas as pd
from datetime import datetime
from my_app.config.my_settings import BaseConfig
from my_app.product.models import start_backend_job
# from my_app import app
from . import dti

basepath = BaseConfig.BASE_PATH
@dti.route('/submitMolecule',methods=['GET', 'POST'])
def submitMolecule():
    return render_template('submitMolecule.html')

@dti.route('/smiles_submit',methods=['GET','POST'])
def submitsmiles():
    smiles=request.form.get('smiles')
    print(1)
    print(smiles)
    smiles_df=pd.DataFrame({'id':[1],'SMILES':smiles})
    smiles_df=pd.DataFrame(smiles_df['SMILES'])
    try:
        ip=str(request.remote_addr)
        session['ip']=ip
        
        TIMESTRING = datetime.now().strftime("%Y%m%d-%H.%M.%S.%f")
        
        print(TIMESTRING)
        session['time'] = TIMESTRING
        smiles_dir='tmp/input/%s/'%(TIMESTRING)
        ext_dir='tmp/ext/%s/'%(TIMESTRING)
        output_dir='tmp/output/%s/'%(TIMESTRING)

        os.makedirs(os.path.join(basepath,smiles_dir),exist_ok=True)
        # os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,ext_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,output_dir),exist_ok=True)

        # save
        smiles_df.to_csv(os.path.join(basepath,smiles_dir,'drug.csv'),index=False)
        result,cmd=start_backend_job(basepath,'dti.sh','%s'%(TIMESTRING),basepath,'%s'%(TIMESTRING))
        print(result)
        print(cmd)
    except Exception as e:
        result={'ok': False, 'result':str(e), 'error': str(e)}
        
    print(result)
    print(1)
    return jsonify(result)

        





    
    
