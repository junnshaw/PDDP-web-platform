FROM ubuntu:18.04

RUN apt-get -qq update && apt-get -qq -y install wget bzip2 \
    && wget https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh -O /tmp/miniconda.sh \
    #    Miniconda3-4.5.1-Linux-x86_64.sh          Miniconda3-py37_4.9.2-Linux-x86_64.sh
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
	&& apt-get install -qq -y libbsd-dev

ENV PATH /usr/local/bin:$PATH
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

RUN conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
    conda config --set show_channel_urls yes && \
    conda install -y python=3.7 pip && \
    conda clean -afy
RUN mkdir ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> ~/.pip/pip.conf && \
    echo "[install]"  >> ~/.pip/pip.conf && \
    echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf
RUN pip install --no-cache-dir --default-timeout=300 --retries 10 \
        numpy==1.19.5 \
        scipy==1.7.3 \
        pandas==1.1.5 \
        matplotlib==3.3.4 \
        scikit-learn==0.24.2 \
        xlrd==1.2.0 \
        tqdm==4.62.0 \
        keras==2.2.4 \
        -i http://mirrors.aliyun.com/pypi/simple \
        --trusted-host mirrors.aliyun.com
RUN pip install --no-cache-dir --default-timeout=600 --retries 20 \
        tensorflow==1.15 \
        protobuf==3.20.3 \
        -i http://mirrors.aliyun.com/pypi/simple \
        --trusted-host mirrors.aliyun.com
RUN mkdir /run_script/
workdir /run_script/
ADD script/ /run_script/


CMD ["/usr/local/bin/python","/run_script/Wrapper.py"]
