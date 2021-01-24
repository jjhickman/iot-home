FROM jjhickman/tpu-interpreter

WORKDIR /interpreter
COPY requirements.txt .
RUN apt-get update; \
    apt-get install -y --no-install-recommends python3-pip; \
    pip3 install -r requirements.txt; \
    mkdir /interpreter/models; \
    mkdir /interpreter/output;

COPY . .

CMD ["python3", "interpreter.py", "--help"]
