FROM tensorflow/tensorflow

RUN pip install -U pip && \
    pip install grpcio grpcio-tools \
    pip install numpy
ADD . /app
ENTRYPOINT [ "python", "/app/main.py" ]
