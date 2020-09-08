FROM arm32v6/python:3.7-alpine3.11

ARG PYTHON_VERSION_SHORT=3.7
ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=1
ARG REPOSITORY=https://github.com/jjhickman/iot-home.git
ENV OPENCV_VERSION=$OPENCV_VERSION
ARG DEBIAN_FRONTEND=noninteractive


WORKDIR /iot-home
RUN apk update
RUN apk add build-base \
    clang \
    clang-dev ninja \
    cmake \
    freetype-dev \
    g++ \
    jpeg-dev \
    lcms2-dev \
    libffi-dev \
    libgcc \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    make \
    musl \
    musl-dev \
    openjpeg-dev \
    openssl-dev \
    python3-dev \
    zlib-dev \
    && apk add \
    curl \
    freetype \
    gcc \
    jpeg \
    libjpeg \
    openjpeg \
    python3 \
    tesseract-ocr \
    zlib

# Installing build tools and dependencies.
RUN apk del build-dependencies && \
    rm -rf /var/cache/apk/*

RUN pip install numpy

# Download latest source and contrib
RUN set -e; \
    cd /tmp; \
    wget -c -nv -O opencv.zip https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip; \
    unzip opencv.zip; \
    wget -c -nv -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip; \
    unzip opencv_contrib.zip; \
    mv opencv-${OPENCV_VERSION} opencv; \
    mv opencv_contrib-${OPENCV_VERSION} opencv_contrib

# Build opencv
RUN set -e; \
    cd /tmp/opencv; \
    mkdir build; \
    cd build; \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib/modules \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        # Build without GUI support
        -D WITH_QT=OFF \
        -D WITH_GTK=OFF \
        # Build without GPU support
        -D WITH_OPENCL=OFF \
        -D WITH_CUDA=OFF \
        -D BUILD_opencv_gpu=OFF \
        -D BUILD_opencv_gpuarithm=OFF \
        -D BUILD_opencv_gpubgsegm=OFF \
        -D BUILD_opencv_gpucodec=OFF \
        -D BUILD_opencv_gpufeatures2d=OFF \
        -D BUILD_opencv_gpufilters=OFF \
        -D BUILD_opencv_gpuimgproc=OFF \
        -D BUILD_opencv_gpulegacy=OFF \
        -D BUILD_opencv_gpuoptflow=OFF \
        -D BUILD_opencv_gpustereo=OFF \
        -D BUILD_opencv_gpuwarping=OFF \
        # Build with python
        -D BUILD_opencv_python3=ON \
        -D BUILD_opencv_python2=OFF \
        # Ignore all unnecessary stages
        -D BUILD_opencv_apps=OFF \
        -D BUILD_EXAMPLES=OFF \
        -D INSTALL_C_EXAMPLES=OFF \
        -D INSTALL_PYTHON_EXAMPLES=OFF \
        -D BUILD_DOCS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D BUILD_TESTS=OFF \
        ..; \
    make -j$CPU_CORES; \
    make install; \
    ldconfig; \
    # Clean up
    make clean; \
    cd /tmp; \
    rm -rf /tmp/*

# get application
RUN git clone $REPOSITORY .
RUN cd ./infrared-security-webcam; \
    pip3 install -r requirements.txt


CMD ["/bin/bash"]
