FROM python:3.10

RUN apt update
RUN apt-get install nodejs -y
RUN apt-get install npm -y

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
RUN pip install TA-Lib
RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

WORKDIR /analysis
COPY . /analysis
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN jupyter labextension install jupyterlab-plotly

CMD ["jupyter-lab","--ip","0.0.0.0","--allow-root","-b","localhost"]
