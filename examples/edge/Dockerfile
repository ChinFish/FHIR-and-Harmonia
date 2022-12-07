FROM tensorflow/tensorflow

RUN pip install --upgrade pip && \
    pip install --upgrade protobuf==3.20.* \
    pip install grpcio grpcio-tools \
    pip install pandas \
    pip install scikit-learn \
    pip install openpyxl

ADD . /app
ADD ./train /train
ENTRYPOINT [ "python", "/app/main.py" ]
