FROM nvidia/cuda:11.2.2-cudnn8-devel-ubuntu18.04

RUN apt-get -qq update && apt-get -qq -y install wget bzip2 && \
        wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -bfp /usr/local && \
    rm -rf /tmp/miniconda.sh

RUN conda install -y python=3 && \
    conda update conda

RUN mkdir ~/.pip /run_script && \
    pip config set global.index-url http://mirrors.aliyun.com/pypi/simple && \
    pip config set install.trusted-host mirrors.aliyun.com && \
    pip install -U pip && \
    yes|pip install configparser tqdm
    
RUN pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html

RUN conda install -y -c rdkit rdkit

# RUN yes|pip install torch-geometric
    
# RUN yes|pip install torch-geometric=1.6.1 torch-scatter=2.0.8 torch-sparse=0.6.12 scikit-learn=0.24.1
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN yes|pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric==1.6.1 -f https://data.pyg.org/whl/torch-1.8.0+cu111.html

RUN apt-get -y install libxrender1 libxext6
ADD script/* /run_script/

CMD ["/usr/local/bin/python","/run_script/wrapper.py"]

