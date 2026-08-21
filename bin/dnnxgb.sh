#!/bin/bash

##
cd /nfs_storage/Website_Client/docker_img/dnnxgb_docker/

##
docker build -t dnnxgb . 

docker run --rm --device /dev/nvidia-uvm:/dev/nvidia-uvm:rwm \
--device /dev/nvidia-uvm-tools:/dev/nvidia-uvm-tools:rwm \
--device /dev/nvidia0:/dev/nvidia0:rwm \
--device /dev/nvidiactl:/dev/nvidiactl:rwm \
-v /usr/bin/nvidia-smi:/usr/bin/nvidia-smi:ro \
-v /usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:ro \
-v /usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:ro \
-v /nfs_storage/Website_Client/tmp/input/$1/:/input/ \
-v /nfs_storage/Website_Client/tmp/ext/$1/:/ext/ \
-v /nfs_storage/Website_Client/docker_img/dnnxgb_docker/conf/:/conf/ \
-v /nfs_storage/Website_Client/tmp/output/$1/:/output/  \
dnnxgb
jsonpath="/nfs_storage/Website_Client/tmp/ext/$1/task_state.json"

appcode=''

while read line
do 
    [[ $line =~ "status" ]] && {
        appcode=${line:11:7}   
    }   
done < $jsonpath

echo $appcode











