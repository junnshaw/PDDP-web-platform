from my_app.main.view import index, result
# from docker_img.MolTrans_docker.scripts.models import Output
from flask import json, render_template,url_for,request,jsonify,session
import time
import os
import pandas as pd
import random
from my_app.product.models import submit_dnnxgb
# from my_app import app
from . import dnnxgb

basepath='/nfs_storage/Website_Client'
@dnnxgb.route('/submitdnnxgb',methods=['GET', 'POST'])
def submitMolecule():
    return render_template('submitdnnxgb.html')

@dnnxgb.route('/dnnxgb_introduction',methods=['GET', 'POST'])
def dnnxgb_introduction():
    return render_template('dnnxgb_introduction.html')

@dnnxgb.route('/smiles_submit_dnnxgb',methods=['GET','POST'])
def submitsmiles():
    input_dnnxgb1=request.form.get('input_dnnxgb1')
    input_dnnxgb2=request.form.get('input_dnnxgb2')
    print(input_dnnxgb1)
    print(input_dnnxgb2)
    try:
        ip=str(request.remote_addr)
        session['ip']=ip
        
        TIMESTRING  = time.strftime("%Y%m%d-%H.%M.%S", time.localtime())
        randstring = 'final'
        session['rand'] = randstring
        session['time'] = TIMESTRING
        # smiles_dir='tmp/input/%s/'%(randstring)
        # ext_dir='tmp/ext/%s/'%(randstring)
        # output_dir='tmp/output/%s/'%(randstring)

        smiles_dir='tmp/input/%s/'%(TIMESTRING)
        ext_dir='tmp/ext/%s/'%(TIMESTRING)
        output_dir='tmp/output/%s/'%(TIMESTRING)

        os.makedirs(os.path.join(basepath,smiles_dir),exist_ok=True)
        # os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,ext_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,output_dir),exist_ok=True)

        # save
        with open(os.path.join(basepath,smiles_dir,'dnnxgb.csv'),'w') as file:
            file.write('%s,%s'%(input_dnnxgb1,input_dnnxgb2))
        # smiles_df.to_csv(os.path.join(basepath,smiles_dir,'drug.csv'),index=False)
        result,cmd=submit_dnnxgb(basepath,'dnnxgb.sh','%s'%(TIMESTRING))
        print(result)
        print(cmd)
    except Exception as e:
        result={'result':str(e)}
        
    print(result)
    print(1)
    return jsonify(result)