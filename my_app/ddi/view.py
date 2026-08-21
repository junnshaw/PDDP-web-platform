from my_app.main.view import index, result
# from docker_img.MolTrans_docker.scripts.models import Output
from flask import json, render_template,url_for,request,jsonify,session
import time
import os
import pandas as pd
from my_app.product.models import submit_ddi
# from my_app import app
from . import ddi

basepath='/nfs_storage/Website_Client'
@ddi.route('/submitMolecule_ddi',methods=['GET', 'POST'])
def submitMolecule():
    return render_template('submitMolecule_DDI.html')

@ddi.route('/smiles_submit_ddi',methods=['GET','POST'])
def submitsmiles():
    smiles=request.form.get('smiles')
    id=request.form.get('id')
    print(id)
    print(1)
    print(smiles)
    # smiles_df=pd.DataFrame({'id':[1],'SMILES':smiles})
    # smiles_df=pd.DataFrame(smiles_df['SMILES'])
    try:
        ip=str(request.remote_addr)
        session['ip']=ip
        
        TIMESTRING  = time.strftime("%Y%m%d-%H.%M.%S", time.localtime())
        
        print(TIMESTRING)
        session['time'] = TIMESTRING
        str1 = 'dditmp'
        session['ddi'] = str1
        smiles_dir='tmp/input/%s/'%(str1)
        ext_dir='tmp/ext/%s/'%(str1)
        # output_dir='ddi_docker/output/'
        output_dir='tmp/output/%s/'%(str1)

        os.makedirs(os.path.join(basepath,smiles_dir),exist_ok=True)
        # os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,ext_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,output_dir),exist_ok=True)

        # save
        with open(os.path.join(basepath,smiles_dir,'input_structures.txt'),'w') as file:
            file.write('%s %s'%(id,smiles))
        # smiles_df.to_csv(os.path.join(basepath,smiles_dir,'drug.csv'),index=False)
        result,cmd=submit_ddi(basepath,'ddi.sh','%s'%(str1))
        print(result)
        print(cmd)
    except Exception as e:
        result={'result':str(e)}
        
    print(result)
    print(1)
    return jsonify(result)
