FROM jjhickman/opencv-python:headless
WORKDIR /security-cam
ARG TARGETPLATFORM
ENV PLATFORM=${TARGETPLATFORM}

RUN echo ${TARGETPLATFORM} > /platform.txt

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt; \
  mkdir -p /etc/security-cam; \
  touch /etc/security-cam/ca.crt

COPY . .
CMD ["python3", "security-cam.py"]
