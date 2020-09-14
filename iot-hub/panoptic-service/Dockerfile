#FROM raspbian/stretch:latest
FROM arm64v8/ubuntu:focal
WORKDIR /iot-home

ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=4
ARG REPOSITORY=https://github.com/jjhickman/iot-home.git
ENV OPENCV_VERSION=$OPENCV_VERSION
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN set -e; \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential apt-utils cmake wget git pkg-config gfortran zip \
    unzip libjpeg-dev libtiff5-dev libavcodec-dev libavformat-dev \
    libswscale-dev libgtk2.0-dev libxvidcore-dev libx264-dev libv4l-dev \
    libatlas-base-dev vim python3-dev python2.7-dev v4l-utils curl \
    gstreamer1.0-plugins-base  gstreamer1.0-plugins-good qtbase5-dev \
    qtdeclarative5-dev nodejs npm  gnupg2 gnupg ; \
    python3-pip -y --no-install-recommends; \
    pip3 install --upgrade pip && pip3 install numpy picamera \
    python-socketio async-timeout asyncio pika Pillow; \
    npm install -g pm2

# Setup for Coral Edge TPU
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee --append /etc/apt/sources.list.d/coral-edgetpu.list; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - ; \
    apt-get update ; \
    apt-get install libedgetpu1-std -y --no-install-recommends; \
    wget https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp38-cp38-linux_aarch64.whl; \
    pip3 install tflite_runtime-2.1.0.post1-cp38-cp38-linux_aarch64.whl; \
    rm tflite_runtime-2.1.0.post1-cp38-cp38-linux_aarch64.whl

# Download OpenCV and module source
RUN set -e; \
    cd /tmp; \
    wget -c -nv -O opencv.zip https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip; \
    unzip opencv.zip; \
    wget -c -nv -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip; \
    unzip opencv_contrib.zip; \
    mv opencv-${OPENCV_VERSION} opencv; \
    mv opencv_contrib-${OPENCV_VERSION} opencv_contrib; \
    cd /tmp/opencv; \
    mkdir build; \
    cd build; \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib/modules \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        # Build with GUI support
        -D WITH_QT=ON \
        -D WITH_GTK=ON \
        # Build without GPU support
        -D WITH_OPENCL=ON \
        -D WITH_CUDA=OFF \
	    -D OPENCV_GENERATE_PKGCONFIG=ON \
	    -D BUILD_NEW_PYTHON_SUPPORT=ON \
	    -D BUILD_opencv_python3=TRUE \
	    -D WITH_OPENMP=ON \
	    -D BUILD_TIFF=ON \
	    -D WITH_FFMPEG=ON \
	    -D WITH_GSTREAMER=ON \
	    -D WITH_TBB=ON \
	    -D BUILD_TBB=ON \
	    -D OPENCV_EXTRA_EXE_LINKER_FLAGS=-latomic \
	    -D WITH_EIGEN=OFF \
        # Build with python
        # Ignore all unnecessary stages
        -D BUILD_EXAMPLES=OFF \
        -D INSTALL_C_EXAMPLES=OFF \
        -D INSTALL_PYTHON_EXAMPLES=OFF \
        -D BUILD_DOCS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D BUILD_TESTS=OFF \
        .. ; \
    make -j$CPU_CORES; \
    make install; \
    ldconfig; 

# Clean up installation and set environment variable
RUN set -e; \
    rm -rf /tmp/*; \
    rm -rf /var/lib/apt/lists/*; \
    dpkg -P -r --force-depends git curl wget; \
	apt-get -y autoremove; \
    touch /root/.bashrc; \
    echo "export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1" > /root/.bashrc

CMD ["/bin/bash"]
# CMD ["pm2", "start", "iot-hub/panoptic-service.py", "--interpreter", "python3.8", "--name", "panoptic-service", "--restart-delay", "5000"]
