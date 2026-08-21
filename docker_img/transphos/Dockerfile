# FROM中删除了nvidia/cuda的参数，因为服务器没有gpu，如果有这里可以加
# FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04
FROM ubuntu:18.04

RUN apt-get -qq update && apt-get -qq -y install wget bzip2 \
    && wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh -O /tmp/miniconda.sh \    
	&& bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh


ENV PATH /opt/conda/bin:$PATH


RUN conda config --add channels  https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main && \
    conda config --add channels  https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free && \
    conda config --add channels  https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r && \
    conda config --add channels  https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro && \
    conda config --add channels  https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2 && \
    conda update conda


RUN mkdir ~/.pip /run_script && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple/" >> ~/.pip/pip.conf && \
    echo "[install]"  >> ~/.pip/pip.conf && \
    echo "trusted-host=pypi.tuna.tsinghua.edu.cn" >> ~/.pip/pip.conf
    

RUN conda install numpy && \  
    conda install pandas && \
    conda install tensorflow && \
    conda install matplotlib && \
    conda install keras


ADD script/* /run_script/

CMD ["/usr/local/bin/python","/run_script/wrapper.py"]
