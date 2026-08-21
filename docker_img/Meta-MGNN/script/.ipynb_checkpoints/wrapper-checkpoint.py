# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import configparser
import time
import json

# 配置文件的默认目录，必须从此目录读取配置文件
default_config_dir = "/conf"

# 内部程序存放位置，由封装者自行制定，与系统无关
default_script_dir = "/run_script"

# 被封装的程序
script_path = "main.py"


config_file = "app.conf"
config_file_full_path = os.path.join(default_config_dir, config_file)
conf = configparser.ConfigParser()
conf.read(config_file_full_path)

# 对配置文件中的输入输出路径和参数进行处理
print(config_file_full_path)
full_path_dict = {}
full_path_dict["input"] = {k: os.path.join(conf.get("mapping",
                                                    "base_input_path"), v) for k, v in conf.items("input")}

full_path_dict["output"] = {k: os.path.join(conf.get("mapping",
                                                     "base_output_path"), v) for k, v in conf.items("output")}

full_path_dict["ext"] = {k: os.path.join(conf.get("mapping", "base_ext_path"), v)
                         for k, v in conf.items("ext")}

script_full_path = os.path.join(default_script_dir, script_path)

dataset = conf.get("param","dataset")
graph_model = conf.get("param","graph_model")
taskaware_attention = conf.get("param","taskaware_attention")
edge_pred = conf.get("param","edge_pred")
atom_pred = conf.get("param","atom_pred")
weight = conf.get("param","weight")
support = conf.get("param","support")


def write_tsf(status, speed, desc, start_time, end_time):
    with open(full_path_dict["ext"]["task_state_file"], "w") as tsf:
        ts_message = {"status": status,
            "speed": speed,
            "desc": desc,
            "startTime": start_time,
            "endTime": end_time}
        json.dump(ts_message, tsf, indent=4)

#记录算子运行状态
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
write_tsf("execution", "0", "running...", start_time, "")

#调用运行被封装的程序
process_argvs = "python "+script_full_path+" --input_model_file "+full_path_dict["input"]["pretrained_model"]+" --dataset "+ dataset+" --gnn_type "+ graph_model+" --add_similarity "+taskaware_attention+" --add_selfsupervise "+edge_pred+" --add_masking "+atom_pred+" --add_weight "+weight+" --m_support "+support+" --filename "+full_path_dict["output"]["output"]


#将stderr和stdout写入输出目录
with open(full_path_dict["ext"]["stderr_file"], "w") as stderr_f,\
    open(full_path_dict["ext"]["stdout_file"], "w") as stdout_f:
    print(process_argvs)
    p = subprocess.Popen(process_argvs, stdout=stdout_f, stderr=stderr_f, shell=True)
    p.wait()
    returncode = p.returncode
  
    if returncode == 0:
        status = "success"
        speed = "1"
        desc = "success desc"
    else:
        status = "failure"
        speed = "1"
        desc = "failure desc"
  #记录算子运行状态
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    write_tsf(status, speed, desc, start_time, end_time)
