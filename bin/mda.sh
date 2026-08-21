#!/bin/bash
set -e

BASE_PATH="${1:-/nfs_storage/Website_Client}"
TMP_FOLDER="${2:-}"

cd "$BASE_PATH/docker_img/gmda_docker/"

##
if ! docker image inspect graph2mda >/dev/null 2>&1 || [ "${FORCE_DOCKER_BUILD:-0}" = "1" ]; then
    docker build -t graph2mda .
fi

docker_args=(
    --rm
    -v "$BASE_PATH/tmp/input/$TMP_FOLDER/:/input/"
    -v "$BASE_PATH/tmp/ext/$TMP_FOLDER/:/ext/"
    -v "$BASE_PATH/docker_img/gmda_docker/conf/:/conf/"
    -v "$BASE_PATH/tmp/output/$TMP_FOLDER/:/output/"
)

if [ -e /dev/nvidia0 ] && [ -e /dev/nvidiactl ]; then
    docker_args+=(
        --device /dev/nvidia0:/dev/nvidia0:rwm
        --device /dev/nvidiactl:/dev/nvidiactl:rwm
        -v /usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:ro
    )

    if [ -e /dev/nvidia-uvm ]; then
        docker_args+=(--device /dev/nvidia-uvm:/dev/nvidia-uvm:rwm)
    fi
    if [ -e /dev/nvidia-uvm-tools ]; then
        docker_args+=(--device /dev/nvidia-uvm-tools:/dev/nvidia-uvm-tools:rwm)
    fi
    if [ -x /usr/bin/nvidia-smi ]; then
        docker_args+=(-v /usr/bin/nvidia-smi:/usr/bin/nvidia-smi:ro)
    fi
else
    echo "NVIDIA devices were not found; running graph2mda on CPU."
fi

docker run "${docker_args[@]}" graph2mda
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







