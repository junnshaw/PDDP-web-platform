from my_app.main.view import index, result
from flask import json, render_template,url_for,request,jsonify,session
import time
import os
import pandas as pd
from my_app.product.models import submit_jtvae
# from my_app import app
from . import jtvae


basepath='/nfs_storage/Website_Client'
@jtvae.route('/submitjtvae',methods=['GET', 'POST'])
def submitMolecule():
    return render_template('submitjtvae.html')

@jtvae.route('/smiles_submit_jtvae',methods=['GET','POST'])
def submitsmiles():
    input1=request.form.get('input_jtvae1')
    input2=request.form.get('input_jtvae2')
    input3=request.form.get('input_jtvae3')
    print(1)

    print(input1)
    #print(input2)
    #smiles_df=pd.DataFrame({'id':[1],'SMILES':smiles})
    #smiles_df=pd.DataFrame(smiles_df['SMILES'])
    #smiles_df=pd.DataFrame(smiles)
    try:
        ip=str(request.remote_addr)
        session['ip']=ip
        
        TIMESTRING  = time.strftime("%Y%m%d-%H.%M.%S", time.localtime())
        
        print(TIMESTRING)
        session['time'] = TIMESTRING
        ####add
        smiles_dir='tmp/input/%s/'%(TIMESTRING)
        ext_dir='tmp/ext/%s/'%(TIMESTRING)
        output_dir='tmp/output/%s/'%(TIMESTRING)

        #smiles_dir='tmp/input/jtvae/'
        #ext_dir='tmp/ext/jtvae/'
        #output_dir='tmp/output/jtvae/'

        os.makedirs(os.path.join(basepath,smiles_dir),exist_ok=True)
        # os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,ext_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,output_dir),exist_ok=True)

        # save
        #smiles_df.to_csv(os.path.join(basepath,smiles_dir,'druglist.csv'),index=False)
        with open(os.path.join(basepath,smiles_dir,'jtvae_input.csv'),'w') as file:
            file.write('%s,%s,%s'%(input1,input2,input3))

        result,cmd=submit_jtvae(basepath,'jtvae.sh','%s'%(TIMESTRING))
        print(result)
        print(cmd)
    except Exception as e:
        result={'result':str(e)}
        
    print(result)
    print(1)
    return jsonify(result)

        





    
    

