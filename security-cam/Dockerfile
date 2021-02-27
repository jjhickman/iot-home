FROM jjhickman/opencv-python:headless AS builder
ARG TARGETPLATFORM
ENV PLATFORM=${TARGETPLATFORM}

RUN echo ${TARGETPLATFORM} > /platform.txt

FROM ubuntu
WORKDIR /security-cam

COPY --from=builder /platform.txt /platform.txt
COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/include /usr/local/include
COPY --from=builder /usr/lib /usr/lib
COPY --from=builder /usr/include /usr/include
COPY --from=builder /lib /lib
RUN ldconfig /usr/local/lib; \
    ldconfig /usr/lib; \
    ldconfig /lib; \
    apt-get update; \
    apt-get install -y --no-install-recommends build-essential python3-minimal python3-pip; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "security-cam.py"]
