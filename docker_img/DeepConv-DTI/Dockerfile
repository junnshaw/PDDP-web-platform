FROM ubuntu:18.04
# FROM nvidia/cuda:11.2.2-cudnn8-devel-ubuntu18.04
# ����Conda����Դ
# ��������Դ

RUN apt-get -qq update && apt-get -qq -y install wget bzip2 \
    && wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
	&& apt-get install -qq -y libbsd-dev

ENV PATH /opt/conda/bin:$PATH

# ��Դ
run conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
    conda config --set show_channel_urls yes && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/menpo/ && \
    conda install -y python=3 && \
    conda update conda

RUN mkdir ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> ~/.pip/pip.conf && \
    echo "[install]"  >> ~/.pip/pip.conf && \
    echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf 
    # pip install pandas==1.0.4 && \
    # pip install opencv-python==4.2.0.34 &&\
    # pip install torch==1.8.1+cu111 torchvision==0.9.1+cu111 torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html &&\
	# pip install scipy==1.5.0rc2 &&\
	# pip install scikit-learn==0.23.1 &&\
    # pip install	cairosvg==2.4.2

    ##
RUN pip install h5py==2.10 && \
    pip install pandas && \
    pip install tensorflow==1.15.0 && \
    pip install keras==2.3.1 && \
    pip install numpy && \
    pip install pandas && \
    pip install scikit-learn && \
    conda install -c conda-forge rdkit
    # pip install h5py

# run mkdir /DEEPScreen_docker 
# workdir /DEEPScreen_docker
add run_scripts/* /run_scripts/

cmd ["/usr/local/bin/python","/run_scripts/Wrapper.py"]


