FROM jjhickman/opencv-python AS builder
ARG TARGETPLATFORM
ENV PLATFORM=${TARGETPLATFORM}

RUN echo ${TARGETPLATFORM} > /platform.txt

FROM ubuntu

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
    apt-get install -y --no-install-recommends curl gnupg2 ca-certificates; \
    update-ca-certificates; \
    echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - ; \
    apt-get update ; \
    apt-get install libedgetpu1-std python3-pycoral -y --no-install-recommends; \
    apt purge -y curl gnupg2 ca-certificates; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

#WORKDIR /interpreter
#COPY . .
#RUN pip install -r requirements.txt
 #   chown -R interpreter /home/interpreter

#COPY --from=builder /usr/local /usr/local
#RUN ldconfig /usr/local; \
    #useradd -ms /bin/bash interpreter; \
    #mkdir -p /interpreter/log; \
 #   apt-get purge -y --auto-remove curl wget gnupg gnupg2

#USER interpreter
#CMD ["python", "interpreter.py"]