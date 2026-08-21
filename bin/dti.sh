#!/bin/bash
set -e

BASE_PATH="${1:-/nfs_storage/Website_Client}"
TMP_FOLDER="${2:-}"

# cd /nfs_storage/Website_Client/docker_img/DeepConv-DTI/
#cd /nfs_storage/Website_Client/docker_img/MolTrans_docker/
cd "$BASE_PATH/docker_img/MolTrans_docker/"


docker build -t dti:v1 .
docker build --no-cache -f Dockerfile1 -t dti:v1 .

docker_args=(
    --rm
    -v "$BASE_PATH/tmp/input/$TMP_FOLDER/:/input/"
    -v "$BASE_PATH/dti_input/:/resource/"
    -v "$BASE_PATH/tmp/ext/$TMP_FOLDER/:/ext/"
    -v "$BASE_PATH/conf/dti/:/conf/"
    -v "$BASE_PATH/tmp/output/$TMP_FOLDER/:/output/"
)

docker run "${docker_args[@]}" dti:v1
# > /nfs_storage/Website_Client/tmp/ext/$1/docker_run.txt

jsonpath="$BASE_PATH/tmp/ext/$TMP_FOLDER/task_state.json"
output_csv="$BASE_PATH/tmp/output/$TMP_FOLDER/output.csv"
stderr_file="$BASE_PATH/tmp/ext/$TMP_FOLDER/stderr.txt"

if [ ! -f "$jsonpath" ]; then
    echo "task_state.json was not created: $jsonpath" >&2
    exit 1
fi

if [ ! -s "$output_csv" ]; then
    echo "output.csv was not created: $output_csv" >&2
    if [ -f "$stderr_file" ]; then
        echo "Container stderr:" >&2
        cat "$stderr_file" >&2
    fi
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
