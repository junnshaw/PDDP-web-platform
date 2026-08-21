FROM ubuntu:18.04

RUN apt-get -qq update && apt-get -qq -y install wget bzip2 \
    && wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda2-py27_4.8.3-Linux-x86_64.sh -O /tmp/miniconda.sh \    
	&& bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh

RUN apt-get install python2.7 -y

ENV PATH /opt/conda/bin:$PATH

RUN conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
    conda config --set show_channel_urls yes && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/menpo/ && \	 
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
RUN pip install backports.weakref==1.0rc1 && \
    pip install bleach==1.5.0 && \
    pip install funcsigs==1.0.2 && \
    pip install h5py==2.9.0 && \
    pip install html5lib==0.9999999 && \
    pip install Keras==2.0.6 && \
    pip install Markdown==3.1.1 && \
    pip install mock==3.0.5 && \
    pip install numpy==1.16.4 && \
    pip install pandas==0.24.2 && \
    pip install protobuf==3.9.1 && \
    pip install python-dateutil==2.8.0 && \
    pip install pytz==2019.2 && \
    pip install PyYAML==5.1.2 && \
    pip install scikit-learn==0.18 && \
    pip install scipy==1.2.2 && \
    pip install six==1.12.0 && \
    pip install tensorflow==1.2.1 && \
    pip install Theano==1.0.4 && \
    pip install Werkzeug==0.15.5

    
RUN mkdir /run_script/
workdir /run_script/
ADD script/ /run_script/
# ADD run_scripts/* /run_scripts/
# ADD script/data/* /run_script/data/

CMD ["/usr/local/bin/python","/run_script/Wrapper.py"]


