import os
import sys
import subprocess
import configparser
import time
import json
default_config_dir = "/conf"
default_script_dir = "/GraphDTA_docker"

scripts_path="eval.py"

# model_path="datasets_5folds.pickle"
config_file = "app.conf"
config_file_full_path = os.path.join(default_config_dir, config_file)
# #config_file_full_path = os.path.join(default_script_dir, default_config_dir)  # 不对
# #config_file_full_path = os.path.join(default_script_dir, conf_file)   # 不对
conf = configparser.ConfigParser()
conf.read(config_file_full_path)
# #conf.read(config_file_full_path+"/app.conf")  # 成绝对路径不对
# thread_num = conf.get("param", "product_no")

full_path_dict = {}
#full_path_dict = {}
full_path_dict["input"] = {k:os.path.join(conf.get("mapping",
"base_input_path"), v) for k,v in conf.items("input")}

full_path_dict["output"] = {k:os.path.join(conf.get("mapping",
"base_output_path"), v) for k,v in conf.items("output")}
full_path_dict["ext"] = {k:os.path.join(conf.get("mapping", "base_ext_path"), v)
for k,v in conf.items("ext")}

#fc1 = conf.get("param","fc1")
#fc2 = conf.get("param","fc2")
#lr = conf.get("param","lr")
#bs = conf.get("param","bs")
#dropout = conf.get("param","dropout")
#epoch = conf.get("param","epoch")
# product_no = conf.get("param","product_no")


script_full_path = os.path.join(default_script_dir, scripts_path)
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
print(full_path_dict)
process_argvs = ["python",script_full_path ,"--drug_input_file",full_path_dict["input"]["input_dataset"],"--protein_input_file",full_path_dict["input"]["input_dataset1"],"--output_file",full_path_dict["output"]["output_path"],"--input_model",full_path_dict["input"]["input_model"]]

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
     
