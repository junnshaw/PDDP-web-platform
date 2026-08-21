import os
import subprocess
import shutil
from pathlib import Path
import sys

# from numpy.core.fromnumeric import size
# import re
import json
import csv


def _decode_process_output(data):
    if not data:
        return ''

    for encoding in ('utf-8', 'gbk', 'latin-1'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', errors='replace')


def _write_task_state(base_path, tmp_folder, status, stdout='', stderr='', command=''):
    ext_dir = os.path.join(base_path, 'tmp', 'ext', tmp_folder)
    os.makedirs(ext_dir, exist_ok=True)

    with open(os.path.join(ext_dir, 'stdout.txt'), 'w', encoding='utf-8') as stdout_file:
        stdout_file.write(stdout or '')
    with open(os.path.join(ext_dir, 'stderr.txt'), 'w', encoding='utf-8') as stderr_file:
        stderr_file.write(stderr or '')
    with open(os.path.join(ext_dir, 'task_state.json'), 'w', encoding='utf-8') as state_file:
        json.dump(
            {
                'status': status,
                'stdout': stdout or '',
                'stderr': stderr or '',
                'command': command,
            },
            state_file,
        )


def start_backend_job(base_path, func_file, tmp_folder, *script_args):
    script_path = os.path.join(base_path, 'bin', func_file)
    run_mode = os.environ.get('WEBSITE_CLIENT_RUN_MODE', 'auto').lower()

    if run_mode == 'local' or (run_mode == 'auto' and os.name == 'nt'):
        cmd = 'local {}'.format(func_file)
        try:
            stdout = _write_local_result(base_path, func_file, tmp_folder)
            _write_task_state(base_path, tmp_folder, 'finished', stdout=stdout, command=cmd)
            return {'ok': True, 'result': stdout, 'error': '', 'task_id': tmp_folder}, cmd
        except Exception as exc:
            stderr = 'local test run failed: {}'.format(exc)
            _write_task_state(base_path, tmp_folder, 'failed', stderr=stderr, command=cmd)
            return {'ok': False, 'result': '', 'error': stderr, 'task_id': tmp_folder}, cmd

    if run_mode == 'slurm':
        args = ['srun', '-N', '1', '-p', 'debug', 'bash', script_path, *script_args]
    else:
        args = ['bash', script_path, *script_args]

    cmd = ' '.join(args)
    ext_dir = os.path.join(base_path, 'tmp', 'ext', tmp_folder)
    os.makedirs(ext_dir, exist_ok=True)
    _write_task_state(base_path, tmp_folder, 'execution', command=cmd)

    stdout_path = os.path.join(ext_dir, 'backend_stdout.txt')
    stderr_path = os.path.join(ext_dir, 'backend_stderr.txt')
    runner_path = os.path.join(base_path, 'my_app', 'product', 'backend_runner.py')
    process = subprocess.Popen([
        sys.executable,
        runner_path,
        base_path,
        tmp_folder,
        json.dumps(args),
        cmd,
        stdout_path,
        stderr_path,
    ])

    return {
        'ok': True,
        'result': 'submitted',
        'error': '',
        'task_id': tmp_folder,
        'pid': process.pid,
    }, cmd


def _read_first_csv_value(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        rows = list(reader)

    if not rows:
        return ''
    if len(rows) == 1:
        return rows[0][0] if rows[0] else ''
    return rows[1][0] if rows[1] else ''


def _write_local_result(base_path, func_file, tmp_folder):
    input_dir = Path(base_path) / 'tmp' / 'input' / tmp_folder
    output_dir = Path(base_path) / 'tmp' / 'output' / tmp_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    if func_file == 'dti.sh':
        smiles = _read_first_csv_value(input_dir / 'drug.csv')
        with (output_dir / 'output.csv').open('w', encoding='utf-8', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(['SMILES', 'Protein', 'Pred'])
            writer.writerow([smiles, 'LOCAL_TEST_PROTEIN', '0.8765'])
        return 'local dti result generated'

    if func_file == 'transphos.sh':
        input_text = (input_dir / 'input.csv').read_text(encoding='utf-8', errors='replace').strip()
        protein = input_text.split(',', 1)[0] if input_text else 'LOCAL_TEST_PROTEIN'
        position = input_text.split(',', 2)[1] if input_text.count(',') >= 1 else '1'
        with (output_dir / 'transphos.txt').open('w', encoding='utf-8') as output_file:
            output_file.write('{} {} {}\n'.format(protein, position, '0.9123'))
        return 'local transphos result generated'

    if func_file == 'mda.sh':
        drug_name = (input_dir / 'input.csv').read_text(encoding='utf-8', errors='replace').strip()
        microbes = [
            '{}_associated_microbe_1'.format(drug_name or 'LOCAL_TEST_DRUG'),
            '{}_associated_microbe_2'.format(drug_name or 'LOCAL_TEST_DRUG'),
        ]
        with (output_dir / 'output1.csv').open('w', encoding='utf-8') as output_file:
            output_file.write('\n'.join(microbes))
            output_file.write('\n')
        return 'local mda result generated'

    raise ValueError('No local result generator is configured for {}'.format(func_file))


def _submit_backend_job(base_path, func_file, tmp_folder, *script_args):
    script_path = os.path.join(base_path, 'bin', func_file)
    run_mode = os.environ.get('WEBSITE_CLIENT_RUN_MODE', 'auto').lower()

    if run_mode == 'slurm':
        args = ['srun', '-N', '1', '-p', 'debug', 'bash', script_path, *script_args]
    elif run_mode == 'docker' or (run_mode == 'auto' and os.name != 'nt' and shutil.which('bash') is not None):
        args = ['bash', script_path, *script_args]
    else:
        cmd = 'local {}'.format(func_file)
        try:
            stdout = _write_local_result(base_path, func_file, tmp_folder)
            _write_task_state(base_path, tmp_folder, 'finished', stdout=stdout, command=cmd)
            return {'ok': True, 'result': stdout, 'error': ''}, cmd
        except Exception as exc:
            stderr = 'local test run failed: {}'.format(exc)
            _write_task_state(base_path, tmp_folder, 'failed', stderr=stderr, command=cmd)
            return {'ok': False, 'result': '', 'error': stderr}, cmd

    cmd = ' '.join(args)
    print(cmd)

    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = _decode_process_output(process.stdout)
    stderr = _decode_process_output(process.stderr)
    status = 'finished' if process.returncode == 0 else 'failed'

    _write_task_state(base_path, tmp_folder, status, stdout=stdout, stderr=stderr, command=cmd)
    if stderr:
        print('stderr', stderr)

    return {'ok': status == 'finished', 'result': stdout, 'error': stderr}, cmd

def csvTojson(filename,filepath):
    # filename = 'data/output.csv'
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        next(f)
        # 将csv中的数据逐行存到列表lines里 lines的每一个元素对应于txt中的一行。然后将每个元素中的不同信息提取出来
        lines = f.readlines()
        # i变量，由于这个txt存储时有空行，所以增只读偶数行，主要看txt文件的格式，一般不需要
        # j用于判断读了多少条，step为画图的X轴
        # i = 0
        j = 0
        for line in lines:
        # if i % 2 == 0:
        # 分割每一行
            temp = line.split(',')
            # print(temp)
            # print(temp[0])
            # print(temp[1])
            t = temp[2].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'smiles':temp[0],
                'protein':temp[1],
                'pred':t[0]
                }
            result.append(item)
        # print(result)
        # print(type(result))

    with open('%s/output_csvTojson.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result

def csvTojsonDDI(filename,filepath):
    # filename = 'data/output.csv'
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        next(f)
        # 将csv中的数据逐行存到列表lines里 lines的每一个元素对应于txt中的一行。然后将每个元素中的不同信息提取出来
        lines = f.readlines()
        # i变量，由于这个txt存储时有空行，所以增只读偶数行，主要看txt文件的格式，一般不需要
        # j用于判断读了多少条，step为画图的X轴
        # i = 0
        j = 0
        for line in lines:
        # if i % 2 == 0:
        # 分割每一行
            temp = line.split(',')
            # print(temp)
            # print(temp[0])
            # print(temp[1])
            t = temp[2].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'drug_pair':temp[0],
                'class':temp[1],
                'score':t[0]
                }
            result.append(item)
        # print(result)
        # print(type(result))
    with open('%s/output_csvTojsonDDI.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result
    
def csvTojsonDDIdescription(filename,filepath):
    # filename = 'data/output.csv'
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        next(f)
        # 将csv中的数据逐行存到列表lines里 lines的每一个元素对应于txt中的一行。然后将每个元素中的不同信息提取出来
        lines = f.readlines()
        # i变量，由于这个txt存储时有空行，所以增只读偶数行，主要看txt文件的格式，一般不需要
        # j用于判断读了多少条，step为画图的X轴
        # i = 0
        j = 0
        for line in lines:
        # if i % 2 == 0:
        # 分割每一行
            temp = line.split(',')
            # print(temp)
            # print(temp[0])
            # print(temp[1])
            t = temp[3].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'interaction_type':temp[0],
                'description':temp[1]
                }
            result.append(item)
        # print(result)
        # print(type(result))
    with open('%s/output_csvTojsonDDIdescription.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result

##mppcsvtojson
def csvTojsonmpp(filename,filepath):
    # filename = 'data/output.csv'
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        next(f)
        # 将csv中的数据逐行存到列表lines里 lines的每一个元素对应于txt中的一行。然后将每个元素中的不同信息提取出来
        lines = f.readlines()
        # i变量，由于这个txt存储时有空行，所以增只读偶数行，主要看txt文件的格式，一般不需要
        # j用于判断读了多少条，step为画图的X轴
        # i = 0
        j = 0
        for line in lines:
        # if i % 2 == 0:
        # 分割每一行
            temp = line.split(',')
            # print(temp)
            # print(temp[0])
            # print(temp[1])
            # t = temp[2].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'smiles':temp[0],
                'SA_SCORE':temp[1],
                'MW':temp[2],
                'ALOGP':temp[3],
                'HBA':temp[4],
                'HBD':temp[5],
                'PSA':temp[6],
                'ROTB':temp[7],
                'AROM':temp[8],
                'ALERTS':temp[9],
                'VE':temp[10]
                }
            result.append(item)
        # print(result)
        # print(type(result))

    with open('%s/output_csvTojsonmpp.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result

def csvTojsonGM(filename,filepath):
    # filename = 'data/output.csv'
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        # 将csv中的数据逐行存到列表lines里 lines的每一个元素对应于txt中的一行。然后将每个元素中的不同信息提取出来
        lines = f.readlines()
        # i变量，由于这个txt存储时有空行，所以增只读偶数行，主要看txt文件的格式，一般不需要
        # j用于判断读了多少条，step为画图的X轴
        # i = 0
        j = 0
        for line in lines:
        # if i % 2 == 0:
        # 分割每一行
            temp = line.split(',')
            # print(temp)
            # print(temp[0])
            # print(temp[1])
            t = temp[1].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'count':temp[0],
                'smiles':t
                }
            result.append(item)
        # print(result)
        # print(type(result))

    with open('%s/output_csvTojsonGM.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result

def csvTojsonmolflow(filename,filepath):
    
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        lines = f.readlines()
        j = 0
        for line in lines:
            temp = line.split(',')
            print(temp[0])
            print(temp[1])
            print(temp[2])
            #t = temp[1].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'Smiles':temp[0],
                'QED':temp[1],
                'Penalized_logp':temp[2]           
                }
            result.append(item)
        # print(result)
        # print(type(result))

    with open('%s/output_csvTojsonmolflow.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result

def txtTojsontransphosdescription(filename,filepath):
    # filename = 'data/output.txt'
    result = []
    with open(filename, 'r') as f:
        for line in f:
            temp = line.split()
            item = {
                'protein':temp[0],#蛋白质名称
                'position':temp[1],#所在位点
                'score':temp[2]#预测概率
                }
            result.append(item)
    with open('%s/output_txtTojsontransphosdescription.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result

##jtvaecsvtojson
def csvTojsonjtvae(filename,filepath):
    
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        lines = f.readlines()
        j = 0
        for line in lines:
            temp = line.split(',')
            # print(temp[0])
            # print(temp[1])
            # print(temp[2])
            #t = temp[1].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'smiles':temp[0],
                'logp':temp[1],
                'sa':temp[2],
                # 'wt':temp[3]

                }
            result.append(item)
        # print(result)
        # print(type(result))

    with open('%s/output_csvTojsonjtvae.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result


##dnnxgbcsvtojson
def csvTojsondnnxgb(filename,filepath):
    
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        lines = f.readlines()
        j = 0
        for line in lines:
            temp = line.split(',')
            # print(temp[0])
            # print(temp[1])
            # print(temp[2])
            #t = temp[1].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'protein1':temp[0],
                'protein2':temp[1],
                'score':temp[2]          
                }
            result.append(item)
        print(result)
        # print(type(result))

    with open('%s/output_csvTojsondnnxgb.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result
##dnnxgb_pcsvtojson
def csvTojsondnnxgb_p(filename,filepath):
    
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        lines = f.readlines()
        j = 0
        for line in lines:
            temp = line.split(',')
            # print(temp[0])
            # print(temp[1])
            # print(temp[2])
            #t = temp[1].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'protein1':temp[0],
                'protein2':temp[1],
                'score':temp[2]          
                }
            result.append(item)
        print(result)
        # print(type(result))

    with open('%s/output_csvTojsondnnxgb_p.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result
    
##mdacsvtojson
def csvTojsonmda(filename,filepath):
    
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        lines = f.readlines()
        j = 0
        for line in lines:
            temp = line.split(',')
            item = {
                'microbes':temp[0]          
                }
            result.append(item)
        # print(result)
        # print(type(result))

    with open('%s/output_csvTojsonmda.json'%(filepath),'w') as dump_f:
        json.dump(result,dump_f)
    return result



class ConfigFile(object):
    '''
    配置文件基类，新的算法需要继承基类
    '''
    def __init__(self) -> None:
        super().__init__()
        self.basesection="[mapping]\nbase_input_path = /input\nbase_output_path = /output\nbase_ext_path = /ext\nbase_common_path = /common\n"
        # self.inputsection="[input]\ninput_dataset={}\n".format(input_path)
        # self.outputsection="[output]\noutput_path={}\n".format(output_path)
        self.extsection="[ext]\ntask_state_file = task_state.json\nlog_file = log.txt\nstderr_file = stderr.txt\nstdout_file = stdout.txt\n"
        self.resourcesection="[resource]\nresource_file = demo.txt\n"

    def parse(self):
        return self.basesection+self.inputsection+self.outputsection+self.extsection+self.resourcesection


class ConfigDeepscreen(ConfigFile):
    '''
    Deepscren 类，其他算法按照该样例来
    '''
    def __init__(self, protein_dataset, model_dataset, drug_dataset,output_result) -> None:
        super().__init__()
        self.paramsection="[param]\nbatch_size = 8\nworkers = 2\n"
        self.inputsection="[input]\nprotein_dataset={}\npredict_model={}\ninput_drug={}\n".format(protein_dataset,model_dataset,drug_dataset)
        self.outputsection="[output]\noutput_result={}\n".format(output_result)

    def parse(self):
        return self.basesection+self.inputsection+self.outputsection+self.extsection+self.paramsection+self.resourcesection

def submit_dti(base_path,func_file,tmp_folder):
    return _submit_backend_job(base_path, func_file, tmp_folder, base_path, tmp_folder)

def submit_molflow(base_path,func_file,tmp_folder):
    cmd='srun -N 1  -p debug bash {} {}'.format(os.path.join(base_path,'bin',func_file),tmp_folder)
    print(cmd)
    back=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    task_code=back[0].decode()
    return_info={'result':'{}'.format(task_code)}
    return return_info,cmd

def submit_ddi(base_path,func_file,tmp_folder):
    cmd='srun -N 1 -p debug bash {} {}'.format(os.path.join(base_path,'bin',func_file),tmp_folder)
    print(cmd)
    back=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    task_code=back[0].decode()
    return_info={'result':'{}'.format(task_code)}
    return return_info,cmd

def submit_transphos(base_path,func_file,tmp_folder):
    return _submit_backend_job(base_path, func_file, tmp_folder, base_path, tmp_folder)

def submit_dnnxgb(base_path,func_file,tmp_folder):
    cmd='srun -N 1  -p debug bash {} {}'.format(os.path.join(base_path,'bin',func_file),tmp_folder)
    print(cmd)
    back=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    task_code=back[0].decode()
    print('back',str(back))
    return_info={'result':'{}'.format(task_code)}
    return return_info,cmd
def submit_dnnxgb_p(base_path,func_file,tmp_folder):
    cmd='srun -N 1  -p debug bash {} {}'.format(os.path.join(base_path,'bin',func_file),tmp_folder)
    print(cmd)
    back=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    task_code=back[0].decode()
    print('back',str(back))
    return_info={'result':'{}'.format(task_code)}
    return return_info,cmd
def submit_jtvae(base_path,func_file,tmp_folder):
    cmd='srun -N 1  -p debug bash {} {}'.format(os.path.join(base_path,'bin',func_file),tmp_folder)
    print(cmd)
    back=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    task_code=back[0].decode()
    print('back',str(back))
    return_info={'result':'{}'.format(task_code)}
    return return_info,cmd
    
def submit_mda(base_path,func_file,tmp_folder):
    return _submit_backend_job(base_path, func_file, tmp_folder, base_path, tmp_folder)
