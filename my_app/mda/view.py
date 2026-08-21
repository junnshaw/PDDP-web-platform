from my_app.main.view import index, result
from flask import json, render_template,url_for,request,jsonify,session
import time
import os
import pandas as pd
from datetime import datetime
from my_app.product.models import start_backend_job
from my_app.config.my_settings import BaseConfig
# from my_app import app
from . import mda


basepath = BaseConfig.BASE_PATH
@mda.route('/submitmda',methods=['GET', 'POST'])
def submitMolecule():
    return render_template('submitmda.html')

@mda.route('/smiles_submit_mda',methods=['GET','POST'])
def submitsmiles():
    input1=request.form.get('input_mda1')
    #input2=request.form.get('input_mda')
    print(1)

    print(input1)
    #print(input2)
    #smiles_df=pd.DataFrame({'id':[1],'SMILES':smiles})
    #smiles_df=pd.DataFrame(smiles_df['SMILES'])
    #smiles_df=pd.DataFrame(smiles)
    try:
        ip=str(request.remote_addr)
        session['ip']=ip
        
        TIMESTRING = datetime.now().strftime("%Y%m%d-%H.%M.%S.%f")
        
        print(TIMESTRING)
        session['time'] = TIMESTRING
        ####add
        smiles_dir='tmp/input/%s/'%(TIMESTRING)
        ext_dir='tmp/ext/%s/'%(TIMESTRING)
        output_dir='tmp/output/%s/'%(TIMESTRING)

        os.makedirs(os.path.join(basepath,smiles_dir),exist_ok=True)
        # os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,ext_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,output_dir),exist_ok=True)

        # save
        #smiles_df.to_csv(os.path.join(basepath,smiles_dir,'druglist.csv'),index=False)
        with open(os.path.join(basepath,smiles_dir,'input.csv'),'w') as file:
            #file.write('%s %s'%(input1,input2)) 
            file.write('%s'%(input1)) 
        result,cmd=start_backend_job(basepath,'mda.sh','%s'%(TIMESTRING),basepath,'%s'%(TIMESTRING))
        print(result)
        print(cmd)
    except Exception as e:
        result={'ok': False, 'result':str(e), 'error': str(e)}
        
    print(result)
    print(1)
    return jsonify(result)

        





    
    
