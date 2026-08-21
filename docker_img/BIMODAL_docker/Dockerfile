FROM nvidia/cuda:11.2.2-cudnn8-devel-ubuntu18.04


RUN apt-get -qq update && apt-get -qq -y install wget bzip2 \
    && wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
	&& apt-get install -qq -y libbsd-dev

ENV PATH /opt/conda/bin:$PATH

run conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
    conda config --set show_channel_urls yes && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/menpo/ && \
    conda install -y python=3.7 && \
    conda update conda

RUN mkdir ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = https://mirrors.aliyun.com/pypi/simple/" >> ~/.pip/pip.conf && \
    echo "[install]"  >> ~/.pip/pip.conf && \
    echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf && \
    
 
# RUN apt-get update && \
    # apt-get install python-rdkit librdkit1 rdkit-data -y
# apt-get update
# apt-get install python-rdkit librdkit1 rdkit-data
RUN conda install -c rdkit rdkit=2018.09.2.0
# RUN pip install backports.weakref==1.0rc1 && \
#     pip install bleach==1.5.0 && \
RUN pip install pytorch=1.0.0

RUN pip install matplotlib=3.0.3 && \
    pip install nbformat=4.4.0 && \
    pip install numpy=1.16.2 && \
    pip install numpy-base=1.16.2 && \
    pip install openbabel=2.4.1 && \
    pip install pandas=0.24.2 && \
    pip install pillow=5.4.1 && \
    # pip install python=3.7.4 && \
    pip install pytorch=1.0.0 && \
    # pip install cuda100 && \
    pip install torchvision=0.2.1 && \
    # pip install rdkit=2018.09.2.0 && \
    pip install scikit-learn=0.20.2 && \
    pip install scipy=1.2.1 && \
    pip install seaborn=0.9.0 && \
    pip install jupyter && \
    pip install torchsummary==1.5.1



    
RUN mkdir /run_script/
workdir /run_script/
ADD script/ /run_script/
# ADD run_scripts/* /run_scripts/
# ADD script/data/* /run_script/data/

CMD ["/usr/local/bin/python","/run_scripts/Wrapper.py"]


