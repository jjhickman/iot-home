FROM arm32v6/python:3.7-alpine:3.11

ARG PYTHON_VERSION_SHORT=3.7
ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=1
ARG REPOSITORY=https://github.com/jjhickman/iot-home.git
ENV OPENCV_VERSION=$OPENCV_VERSION
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /iot-home

# Installing build tools and dependencies.
RUN set -e; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential; \
    apt-get install -y --no-install-recommends \
        # Downloading utils
        unzip \
        wget \
        # Build utils
        cmake \
        gcc \
        # Required dependencies
        python-numpy \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libgstreamer-plugins-base1.0-dev \
        # Optional dependencies
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libopenexr-dev \
        libtiff-dev \
        libwebp-dev \
        # Video device drivers
        libv4l-dev \
        libdc1394-22-dev \
        # app-specific dependencies
        python3-pip \
        python3-dev \
        python3-rpi.gpio; \
    # Clear apt cache
    rm -rf /var/lib/apt/lists/*

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
