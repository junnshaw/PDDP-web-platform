#!/bin/bash
set -e

BASE_PATH="${1:-/nfs_storage/Website_Client}"
TMP_FOLDER="${2:-}"

cd "$BASE_PATH/docker_img/transphos/"

docker build -t zhiyuan:transphos .

docker_args=(
    --rm
    -v /usr/bin/nvidia-smi:/usr/bin/nvidia-smi:ro
    -v /usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:ro
    -v "$BASE_PATH/tmp/input/$TMP_FOLDER/:/input/"
    -v "$BASE_PATH/tmp/ext/$TMP_FOLDER/:/ext/"
    -v "$BASE_PATH/tmp/conf/$TMP_FOLDER/:/conf/"
    -v "$BASE_PATH/tmp/output/$TMP_FOLDER/:/output/"
)

docker run "${docker_args[@]}" zhiyuan:transphos

jsonpath="$BASE_PATH/tmp/ext/$TMP_FOLDER/task_state.json"

if [ ! -f "$jsonpath" ]; then
    echo "task_state.json was not created: $jsonpath" >&2
    exit 1
fi

appcode=''

while read line
do 
    [[ $line =~ "status" ]] && {
        appcode=${line:11:7}   
    }   
done < "$jsonpath"

echo "$appcode"
