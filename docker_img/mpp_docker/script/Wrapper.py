# -*- coding: utf-8 -*-

#!/usr/bin/env python
# coding: utf-8



import os
import sys
import subprocess
import configparser
import time
import json

default_config_dir = "/conf"

default_script_dir = "/run_script"

script_path = "test.py"
script_full_path=os.path.join(default_script_dir,script_path)

config_file = "app.conf"
config_file_full_path = os.path.join(default_config_dir, config_file)
conf = configparser.ConfigParser()
conf.read(config_file_full_path)


full_path_dict = {}


full_path_dict["input"] = {k:os.path.join(conf.get("mapping","base_input_path"), v) for k,v in conf.items("input")}

full_path_dict["output"] = {k:os.path.join(conf.get("mapping","base_output_path"), v) for k,v in conf.items("output")}

full_path_dict["ext"] = {k:os.path.join(conf.get("mapping", "base_ext_path"), v)for k,v in conf.items("ext")}

param = {k:v for k,v in conf.items("param")}


# model_full_path = os.path.join(default_script_dir, model_path)
def write_tsf(status, speed, desc, start_time, end_time):
    with open(full_path_dict["ext"]["task_state_file"], "w") as tsf:
        ts_message = {"status": status,
                        "speed": speed,
                        "desc": desc,
                        "startTime": start_time,
                        "endTime": end_time}
        json.dump(ts_message, tsf, indent=4)

start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
write_tsf("execution", "0", "running...", start_time, "")



process_argvs = ["python", script_full_path,
            
            # '--output_dir', full_path_dict["input"]["input_model"],
            '--input_file', full_path_dict["input"]["input_file"],
            # '--output_tanimoto',full_path_dict["output"]["output_tanimoto"],
            # '--output_ddi',full_path_dict["output"]["output_ddi"],
            # '--output_ddi_f',full_path_dict["output"]["output_ddi_f"],
            # '--output_annotated',full_path_dict["output"]["output_annotated"],
            # '--output_similarity',full_path_dict["output"]["output_similarity"],
            # '--output_pca',full_path_dict["output"]["output_pca"],
            # '--output_result',full_path_dict["output"]["output_result"],

            '--output_csv',full_path_dict["output"]["output_csv"]

            ]
            
            
            
with open(full_path_dict["ext"]["stderr_file"], "w") as stderr_f,\
     open(full_path_dict["ext"]["stdout_file"], "w") as stdout_f:
    print(process_argvs)
    p = subprocess.Popen(process_argvs, stdout=stdout_f, stderr=stderr_f)
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
    
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    write_tsf(status, speed, desc, start_time, end_time)
