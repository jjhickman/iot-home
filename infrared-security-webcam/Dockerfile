FROM balenalib/raspberry-pi-python:latest

WORKDIR /iot-home

ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=4
ARG REPOSITORY=https://github.com/jjhickman/iot-home.git
ENV OPENCV_VERSION=$OPENCV_VERSION
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN set -e; \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential apt-utils cmake wget git gfortran zip unzip libjpeg-dev libtiff-dev libgif-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libcanberra-gtk* \
    libxvidcore-dev libx264-dev libgtk-3-dev \
    libtbb2 libtbb-dev libdc1394-22-dev libv4l-dev \
    libopenblas-dev libatlas-base-dev libblas-dev \
    libjasper-dev liblapack-dev libhdf5-dev \
    gcc-arm* protobuf-compiler vim

# Installing build tools and dependencies.
RUN rm -rf /var/lib/apt/lists/* \
	&& apt-get -y autoremove


# Install Node.js build for ARMv6l
RUN set -e; \
    cd /tmp; \
    wget https://nodejs.org/dist/v11.15.0/node-v11.15.0-linux-armv6l.tar.gz; \
    tar -xzf node-v11.15.0-linux-armv6l.tar.gz; \
    cp -R node-v11.15.0-linux-armv6l/* /usr/local/

# install PM2 to run daemon app
RUN npm install -g pm2

# Install NumPy dependency for OpenCV
RUN pip install numpy

# Download OpenCV and module source
RUN set -e; \
    cd /tmp; \
    wget -c -nv -O opencv.zip https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip; \
    unzip opencv.zip; \
    wget -c -nv -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip; \
    unzip opencv_contrib.zip; \
    mv opencv-${OPENCV_VERSION} opencv; \
    mv opencv_contrib-${OPENCV_VERSION} opencv_contrib

# Configure OpenCV
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
        -D WITH_OPENCL=ON \
        -D WITH_CUDA=OFF \
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
        .. 

# Build OpenCV
RUN set -e; \
    cd /tmp/opencv/build; \
    make -j$CPU_CORES 

# Install OpenCV
RUN set -e; \
    cd /tmp/opencv/build; \ 
    make install; \
    ldconfig; \
    make clean

# Clean up installation
RUN set -e; \
    rm -rf /tmp/*

# Get application and dependencies
RUN git clone $REPOSITORY .
RUN cd /infrared-security-webcam; \
    pip install -r requirements.txt

CMD ["/bin/bash"]
# CMD ["pm2", "start", "infrared-security-webcam/app.py", "--interpreter", "python3.8", "--name", "infrared-security-webcam", "--restart-delay", "5000"]
