FROM jjhickman/opencv-python:headless

WORKDIR /interpreter

RUN mkdir /interpreter/models; \
    mkdir /interpreter/output; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl gnupg2 ca-certificates; \
    update-ca-certificates; \
    echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - ; \
    apt-get update ; \
    apt-get install libedgetpu1-std python3-pycoral -y --no-install-recommends; \
    cd /interpreter/models; \
    curl -OL "https://github.com/google-coral/edgetpu/raw/master/test_data/ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite"; \
    curl -OL "https://github.com/google-coral/edgetpu/raw/master/test_data/ssd_mobilenet_v2_face_quant_postprocess.tflite"; \
    curl -OL "https://github.com/google-coral/edgetpu/raw/master/test_data/coco_labels.txt"; \
    apt purge -y curl gnupg2; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python3", "interpreter.py"]
