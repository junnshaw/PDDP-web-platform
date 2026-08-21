# #!/bin/bash


cd /nfs_storage/Website_Client/docker_img/ddi_docker

docker build -t deepddi:v1 .

docker run --rm -v /nfs_storage/Website_Client/tmp/input/$1/:/input/ \
-v /nfs_storage/Website_Client/tmp/output/$1/:/output/ \
-v /nfs_storage/Website_Client/tmp/ext/$1/:/ext/ \
-v /nfs_storage/Website_Client/ddi_input/:/resource/ \
-v /nfs_storage/Website_Client/conf/ddi/:/conf/ \
deepddi:v1

jsonpath="/nfs_storage/Website_Client/tmp/ext/$1/task_state.json"

appcode=''

while read line
do 
    [[ $line =~ "status" ]] && {
        appcode=${line:11:7}   
    }   
done < $jsonpath

echo $appcode

