FROM tensorflow/tensorflow

RUN pip install -U pip && \
    pip install grpcio grpcio-tools \
    pip install numpy \
    pip install scikit-learn
ADD . /app
ENTRYPOINT [ "python", "/app/main.py" ]
