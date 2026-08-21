# from docker_img.MolTrans_docker.scripts.models import Output
from flask import json, render_template,url_for,jsonify,session,request
import pandas as pd
import os
import time
import json as std_json
from pathlib import Path
from my_app.config.my_settings import BaseConfig
from my_app.product import models
# from my_app import app
from . import main

basepath = BaseConfig.BASE_PATH


def _current_task_id():
    task_id = request.args.get('task_id')
    if task_id:
        return task_id

    for key, value in request.args.items():
        if key.strip(' +') == 'task_id' and value:
            return value

    raw_query = request.query_string.decode('utf-8', errors='ignore')
    for marker in ('task_id=', '+task_id='):
        if marker in raw_query:
            return raw_query.split(marker, 1)[1].split('&', 1)[0]

    return session.get('time')


def _result_file_path(filename):
    time_key = _current_task_id()
    if not time_key:
        return None

    candidate = Path(basepath) / 'tmp' / 'output' / time_key / filename
    if candidate.exists() and candidate.stat().st_size > 0:
        return candidate

    return None


def _task_state_notice():
    time_key = _current_task_id()
    if not time_key:
        return None

    ext_dir = Path(basepath) / 'tmp' / 'ext' / time_key
    state_file = ext_dir / 'task_state.json'
    stderr_file = ext_dir / 'stderr.txt'
    backend_stderr_file = ext_dir / 'backend_stderr.txt'

    status = ''
    stderr = ''
    if state_file.exists():
        try:
            with state_file.open('r', encoding='utf-8') as state_handle:
                state = std_json.load(state_handle)
            status = str(state.get('status', ''))
            stderr = str(state.get('stderr', ''))
        except Exception as exc:
            return 'Task state file could not be parsed: {}'.format(exc)

    if stderr_file.exists() and not stderr:
        stderr = stderr_file.read_text(encoding='utf-8', errors='replace')
    if backend_stderr_file.exists():
        backend_stderr = backend_stderr_file.read_text(encoding='utf-8', errors='replace')
        if backend_stderr.strip():
            stderr = (stderr + '\n' + backend_stderr).strip()

    status_lower = status.lower()
    if status_lower in ('failed', 'failure', 'error') or (not status_lower and stderr.strip()):
        detail = stderr.strip() or 'The backend task failed before writing the result file.'
        return 'Task failed: {}'.format(detail)

    if status_lower in ('finished', 'success'):
        return 'Task finished, but the expected result file was not created. Please check the backend script output path.'

    if status_lower in ('execution', 'running'):
        return None

    return None


def _result_not_ready(template):
    task_notice = _task_state_notice()
    if task_notice:
        return render_template(
            template,
            data_show=[],
            notice=task_notice,
            refresh=False,
        )

    return render_template(
        template,
        data_show=[],
        notice='Result file is not ready yet. Please refresh in a moment.',
        refresh=True,
    )


def _result_parse_error(template, error):
    return render_template(
        template,
        data_show=[],
        notice='Result file could not be parsed. Please check the submitted input or server task log.',
        error=str(error),
        refresh=False,
    )


def _result_empty(template):
    return render_template(
        template,
        data_show=[],
        notice='Result file was created, but no valid result rows were found. Please check the backend stderr/stdout logs for this task.',
        refresh=False,
    )

@main.route('/',methods=['GET', 'POST'])
@main.route('/home',methods=['GET', 'POST'])
def index():
    return render_template('home.html')

@main.route('/selectFunction',methods=['GET', 'POST'])
def selectFunction():
    return render_template('selectFunction.html')


@main.route('/about',methods=['GET', 'POST'])
@main.route('/about.html',methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@main.route('/blog',methods=['GET', 'POST'])
@main.route('/blog.html',methods=['GET', 'POST'])
def blog():
    return render_template('blog.html')





@main.route('/contact',methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')



## jt-vae 路由注册
@main.route('/jthome',methods=['GET', 'POST'])
def jthome():
    return render_template('/jtplates/index.html')

@main.route('/jtmodel',methods=['GET', 'POST'])
def jtmodel():
    return render_template('/jtplates/model.html')

@main.route('/jtfunc',methods=['GET', 'POST'])
def jtfunc():
    return render_template('/jtplates/function.html')

@main.route('/jtabout',methods=['GET', 'POST'])
def jtabout():
    return render_template('/jtplates/about.html')

@main.route('/jtcontact',methods=['GET', 'POST'])
def jtcontact():
    return render_template('/jtplates/contact.html')


# @main.route('/submitMolecule',methods=['GET', 'POST'])
# def submitMolecule():
#     return render_template('submitMolecule.html')

#DeepConv-DTI
# @main.route('/result',methods=['GET', 'POST'])
# def result():
#     time=session.get('time')

#     output_json=models.csvTojson(os.path.join(basepath,'docker_img/DeepConv-DTI/output/output.csv'),os.path.join(basepath,'docker_img/DeepConv-DTI/output/'))
#     # print(output_json)
# MolTrans_docker

@main.route('/result',methods=['GET', 'POST'])
def result():
    time=session.get('time')
    print('****')
    print(time)
    print('****')


    #output_json = models.csvTojson(os.path.join(basepath, 'tmp/output/%s'%(time), 'output.csv'),os.path.join(basepath, 'tmp/output/%s' % (time)))
    #output_json = models.csvTojson(os.path.join(basepath,'tmp/output/%s'%(time), 'output.csv'),os.path.join(basepath,'docker_img/MolTrans_docker/output/'))

    output_csv = _result_file_path('output.csv')
    if output_csv is None:
        return _result_not_ready('result.html')

    try:
        output_json = models.csvTojson(str(output_csv), str(output_csv.parent))
    except Exception as exc:
        return _result_parse_error('result.html', exc)
    if not output_json:
        return _result_empty('result.html')

    #print(output_json)
    # ip=session.get('ip')

    # df=pd.read_csv(os.path.join(basepath,'tmp/output/%s'%(time),'output.csv'))
    # df=df.sort_values(by='Pred',ascending=False).iloc[:,:20]
    
    return render_template('result.html',data_show=output_json)

@main.route('/result_ddi',methods=['GET', 'POST'])
def result_DDI():
    time=session.get('time')

    output_json=models.csvTojsonDDI(os.path.join(basepath,'tmp/output/dditmp','result.csv'),os.path.join(basepath,'docker_img/ddi_docker/'))
    #print(output_json)
    # ip=session.get('ip')
    type_json=models.csvTojsonDDIdescription(os.path.join(basepath,'docker_img/DeepDDI/DDI-Interaction_information.csv'),os.path.join(basepath,'docker_img/DeepDDI/'))
    # df=pd.read_csv(os.path.join(basepath,'tmp/output/%s'%(time),'output.csv'))
    # df=df.sort_values(by='Pred',ascending=False).iloc[:,:20]
    
    return render_template('result_DDI.html',data_show=output_json,type_show=type_json)
   
#tranphos结果
@main.route('/result_transphos',methods=['GET', 'POST'])
def result_transphos():
    output_file = _result_file_path('transphos.txt')
    if output_file is None:
        return _result_not_ready('result_transphos.html')

    try:
        output_json=models.txtTojsontransphosdescription(str(output_file), str(output_file.parent))
    except Exception as exc:
        return _result_parse_error('result_transphos.html', exc)
    if not output_json:
        return _result_not_ready('result_transphos.html')
    return render_template('result_transphos.html',data_show=output_json)

@main.route('/result_molflow',methods=['GET', 'POST'])
def result_molflow():
    time=session.get('time')

    str1 = session.get('molflow')
    print('***')
    print(str1)
    output_json=models.csvTojsonmolflow(os.path.join(basepath,'tmp/output/molflowtmp','resultsort.csv'),os.path.join(basepath,'docker_img/molflow_docker/'))
    return render_template('result_molflow.html',data_show=output_json)

#test dnnxgb结果
@main.route('/result_dnnxgb',methods=['GET', 'POST'])
def result_dnnxgb():
    #randstring = session.get('randstr')
    time=session.get('time')
    #randstring = session.get('rand')
    print('****')
    print(time)
    print('****')

    output_json=models.csvTojsondnnxgb(os.path.join(basepath,'tmp/output/%s'%(time),'output.csv'),os.path.join(basepath,'docker_img/dnnxgb_docker/'))
    #print(output_json)
    # ip=session.get('ip')

    # df=pd.read_csv(os.path.join(basepath,'tmp/output/%s'%(time),'output.csv'))
    # df=df.sort_values(by='Pred',ascending=False).iloc[:,:20]
    
    return render_template('result_dnnxgb.html',data_show=output_json)
####
# @main.route('/result_dnnxgb',methods=['GET', 'POST'])
# def result_dnnxgb():
#     time=session.get('time')
#     print('****')
#     print(time)
#     print('****')
#     output_json=models.csvTojsondnnxgb(os.path.join(basepath,'tmp/output/%s'%(time),'output.csv'),os.path.join(basepath,'docker_img/dnnxgb_docker/'))
#     return render_template('result_dnnxgb.html',data_show=output_json)
####
###dnnxgb_p结果
@main.route('/result_dnnxgb_p',methods=['GET', 'POST'])
def result_dnnxgb_p():
    #randstring = session.get('randstr')
    time=session.get('time')
    #randstring = session.get('rand')
    print('****')
    print(time)
    print('****')

    # 临时链接，显示之前的预测结果
    output_json=models.csvTojsondnnxgb_p(os.path.join(basepath,'docker_img/dnnxgb_p_docker/output/output_p.csv'),os.path.join(basepath,'docker_img/dnnxgb_p_docker/'))
    # output_json=models.csvTojsondnnxgb_p(os.path.join(basepath,'tmp/output/%s'%(time),'output_p.csv'),os.path.join(basepath,'docker_img/dnnxgb_p_docker/'))
    #print(output_json)
    # ip=session.get('ip')

    # df=pd.read_csv(os.path.join(basepath,'tmp/output/%s'%(time),'output.csv'))
    # df=df.sort_values(by='Pred',ascending=False).iloc[:,:20]
    
    return render_template('result_dnnxgb_p.html',data_show=output_json)

####jtvae结果
@main.route('/result_jtvae',methods=['GET', 'POST'])
def result_jtvae():
    time=session.get('time')
    print('#####session time')
    print(time)
    # 临时链接，显示之前的预测结果
    output_json=models.csvTojsonjtvae(os.path.join(basepath,'docker_img/jtvae_docker/output/result.csv'),os.path.join(basepath,'docker_img/jtvae_docker/'))
    # output_json=models.csvTojsonjtvae(os.path.join(basepath,'tmp/output/%s'%(time),'result.csv'),os.path.join(basepath,'docker_img/jtvae_docker/'))
    #output_json=models.csvTojsonjtvae(os.path.join(basepath,'tmp/output/jtvae','result.csv'),os.path.join(basepath,'docker_img/jtvae_docker/'))
    return render_template('result_jtvae.html',data_show=output_json)
####

####mda结果
@main.route('/result_mda',methods=['GET', 'POST'])
def result_mda():
    output_file = _result_file_path('output1.csv')
    if output_file is None:
        return _result_not_ready('result_mda.html')

    try:
        output_json=models.csvTojsonmda(str(output_file), str(output_file.parent))
    except Exception as exc:
        return _result_parse_error('result_mda.html', exc)
    if not output_json:
        return _result_not_ready('result_mda.html')
    return render_template('result_mda.html',data_show=output_json)
####

##MPP结果
@main.route('/result_MPP',methods=['GET', 'POST'])
def result_MPP():
    # 临时链接，显示之前的预测结果
    output_json=models.csvTojsonmpp(os.path.join(basepath,'docker_img/mpp_docker/output/result.csv'),os.path.join(basepath,'docker_img/mpp_docker/'))
    return render_template('result_MPP.html',data_show=output_json)
####

#————————————————————————————————————————————
#临时添加selectfunction中的4个界面，暂无封装
@main.route('/submitMolecule_DDI',methods=['GET', 'POST'])
def submitMolecule_DDI():
    return render_template('submitMolecule_DDI.html')

@main.route('/submitMolecule_PRFP',methods=['GET', 'POST'])
def submitMolecule_PRFP():
    return render_template('submitMolecule_PRFP.html')

@main.route('/submitMolecule_MPP',methods=['GET', 'POST'])
def submitMolecule_MPP():
    return render_template('submitMolecule_MPP.html')

@main.route('/submitMolecule_GM',methods=['GET', 'POST'])
def submitMolecule_GM():
    return render_template('submitMolecule_GM.html')
 
@main.route('/submitmolflow',methods=['GET', 'POST'])
def submitmolflow():
    return render_template('submitmolflow.html')
 
@main.route('/submittransphos',methods=['GET', 'POST'])
def submittransphos():
    return render_template('submittransphos.html')
    
#####
@main.route('/submitdnnxgb',methods=['GET', 'POST'])
def submitdnnxgb():
    return render_template('submitdnnxgb.html')
#####

#####
@main.route('/submitdnnxgb_p',methods=['GET', 'POST'])
def submitdnnxgb_p():
    return render_template('submitdnnxgb_p.html')
#####

#####
@main.route('/submitjtvae',methods=['GET', 'POST'])
def submitjtvae():
    return render_template('submitjtvae.html')
#####

#####
@main.route('/submitmda',methods=['GET', 'POST'])
def submitmda():
    return render_template('submitmda.html')
#####

#————————————————————————————————————————
# DDI结果
# @main.route('/result_DDI',methods=['GET', 'POST'])
# def result_DDI():
    # output_json=models.csvTojsonDDI(os.path.join(basepath,'docker_img/DeepDDI/deepDDI.csv'),os.path.join(basepath,'docker_img/DeepDDI/'))
    # type_json=models.csvTojsonDDIdescription(os.path.join(basepath,'docker_img/DeepDDI/DDI-Interaction_information.csv'),os.path.join(basepath,'docker_img/DeepDDI/'))
    # return render_template('result_DDI.html',data_show=output_json,type_show=type_json)

#PRFP结果
@main.route('/result_PRFP',methods=['GET', 'POST'])
def result_PRFP():
    return render_template('result_PRFP.html')



#GM结果
# @main.route('/result_GM',methods=['GET', 'POST'])
# def result_GM():
#     output_json=models.csvTojsonGM(os.path.join(basepath,'docker_img/BIMODAL_docker/novel_valid_unique_molecules_fold_1_epochs_9_T_0.7_N_100.csv'),os.path.join(basepath,'docker_img/BIMODAL_docker/'))
#     # print(output_json)
#     return render_template('result_GM.html',data_show=output_json)
