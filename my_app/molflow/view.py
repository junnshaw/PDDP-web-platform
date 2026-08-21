from my_app.main.view import index, result
# from docker_img.MolTrans_docker.scripts.models import Output
from flask import json, render_template,url_for,request,jsonify,session
import time
import os
import pandas as pd
from my_app.product.models import submit_molflow
import shutil
# from my_app import app
from . import molflow

basepath='/nfs_storage/Website_Client'
@molflow.route('/submitmolflow',methods=['GET', 'POST'])
def submitMolecule():
    return render_template('submitmolflow.html')

@molflow.route('/smiles_submit_molflow',methods=['GET','POST'])
def submitsmiles():
    #txt=request.form.get('txt')
    #sites=request.form.get('sites')
    #id=request.form.get('id')
    #print(id)
    #print(1)
    #print(txt)
    #print("site",request.form)
    # smiles_df=pd.DataFrame({'id':[1],'SMILES':smiles})
    # smiles_df=pd.DataFrame(smiles_df['SMILES'])
    try:
        ip=str(request.remote_addr)
        session['ip']=ip
        TIMESTRING  = time.strftime("%Y%m%d-%H.%M.%S", time.localtime()) 
        print(TIMESTRING)
        session['time'] = TIMESTRING
        str1 = 'molflowtmp'
        session['molflow'] = str1
        #smiles_dir='tmp/input/%s/'%(TIMESTRING)
        ext_dir='tmp/ext/%s/'%(str1)
        output_dir='tmp/output/%s/'%(str1)
        conf_dir='tmp/conf/%s/'%(str1)
        

        #os.makedirs(os.path.join(basepath,smiles_dir),exist_ok=True)
        # os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,ext_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,output_dir),exist_ok=True)
        os.makedirs(os.path.join(basepath,conf_dir),exist_ok=True)
        #shutil.copyfile('/home/nfs_storage/Website_Client/docker_img/molflow_docker/conf/app.conf',os.path.join(basepath,conf_dir,'app.conf'))
        #获得前端输入
        #with open(os.path.join(basepath,smiles_dir,'input.csv'),'w') as file:
            #for line in txt:
                #file.write(line)  
        #配置conf
        #with open(os.path.join(basepath,conf_dir,'app.conf'),'a') as file:
            #file.write("\n")
            #file.write(f"site={sites}")
        # smiles_df.to_csv(os.path.join(basepath,smiles_dir,'drug.csv'),index=False)
        result,cmd=submit_molflow(basepath,'molflow.sh','%s'%(str1))
        #print(result)
        print(cmd)
    except Exception as e:
        result={'result':str(e)}
        
    # print(result)
    # print(1)
    return jsonify(result)

