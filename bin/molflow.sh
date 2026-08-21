# #!/bin/bash


cd /nfs_storage/Website_Client/docker_img/molflow_docker

docker build -t mf .

docker run --rm -v /usr/bin/nvidia-smi:/usr/bin/nvidia-smi:ro \
-v /usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:ro \
-v /nfs_storage/Website_Client/tmp/input/$1/:/input/ \
-v /nfs_storage/Website_Client/tmp/ext/$1/:/ext/ \
-v /nfs_storage/Website_Client/docker_img/molflow_docker/conf/:/conf/ \
-v /nfs_storage/Website_Client/tmp/output/$1/:/output/  \
mf
jsonpath="/nfs_storage/Website_Client/tmp/ext/$1/task_state.json"

appcode=''

while read line
do 
    [[ $line =~ "status" ]] && {
        appcode=${line:11:7}   
    }   
done < $jsonpath

echo $appcode


