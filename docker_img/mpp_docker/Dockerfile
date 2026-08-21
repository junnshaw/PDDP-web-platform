FROM ubuntu:18.04

# RUN apt-get -qq update && apt-get -qq -y install wget bzip2 \
#     && wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda2-py27_4.8.3-Linux-x86_64.sh -O /tmp/miniconda.sh \    
# 	&& bash /tmp/miniconda.sh -bfp /usr/local \
#     && rm -rf /tmp/miniconda.sh
RUN apt-get -qq update && apt-get -qq -y install wget bzip2 \
    && wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh
# RUN apt-get install python2.7 -y

ENV PATH /opt/conda/bin:$PATH

# RUN conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
#     conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
#     conda config --set show_channel_urls yes && \
#     conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/ && \
#     conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/ && \
#     conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/ && \
#     conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/menpo/ && \	 
#     conda update conda
RUN conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
    conda config --set show_channel_urls yes && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/menpo/ && \
    conda install -y python=3 



RUN mkdir ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> ~/.pip/pip.conf && \
    echo "[install]"  >> ~/.pip/pip.conf && \
    echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf
	
RUN conda install -c conda-forge rdkit
RUN conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
RUN pip install flask && \
    # pip install GPy && \
    pip install hyperopt && \
    pip install jupyter && \
    pip install matplotlib && \
    pip install numpy && \
    pip install plotly && \
    pip install seaborn && \
    pip install scikit-learn && \
    pip install scipy && \
    pip install tensorboardX && \
    pip install tensorflow && \
    pip install torchvision && \
    pip install tqdm

    
RUN mkdir /run_script/
workdir /run_script/
ADD script/ /run_script/
# ADD run_scripts/* /run_scripts/
# ADD script/data/* /run_script/data/

CMD ["/usr/local/bin/python","/run_scripts/Wrapper.py"]


