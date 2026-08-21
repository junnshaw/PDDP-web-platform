FROM ubuntu:18.04

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
    conda install -y python=3 && \
    conda update conda



RUN mkdir ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> ~/.pip/pip.conf && \
    echo "[install]"  >> ~/.pip/pip.conf && \
    echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf
	
    
 
# RUN apt-get update && \
    # apt-get install python-rdkit librdkit1 rdkit-data -y
# apt-get update
# apt-get install python-rdkit librdkit1 rdkit-data
RUN conda install -c conda-forge rdkit
RUN conda install orderedset && \
    conda install tabulate && \
    conda install networkx && \
    conda install scipy && \
    conda install seaborn && \
    pip install tqdm
RUN conda install cairosvg==2.4.2
RUN conda install pytorch==1.7.1 torchvision==0.8.2 torchaudio==0.7.2 cudatoolkit=11.0 -c pytorch -y
    


    
RUN mkdir /run_script/
workdir /run_script/
ADD script/ /run_script/
# ADD run_scripts/* /run_scripts/
# ADD script/data/* /run_script/data/

CMD ["/usr/local/bin/python","/run_script/Wrapper.py"]


