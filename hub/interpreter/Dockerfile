FROM jjhickman/tpu-interpreter

WORKDIR /interpreter
COPY requirements.txt .
RUN apt-get update; \
    apt-get install -y --no-install-recommends python3-pip; \
    pip3 install -r requirements.txt
COPY . .

CMD ["python3", "interpreter.py", "--help"]
