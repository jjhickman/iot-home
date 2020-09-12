FROM raspbian/stretch:latest

WORKDIR /iot-home

ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=4
ARG REPOSITORY=https://github.com/jjhickman/iot-home.git
ENV OPENCV_VERSION=$OPENCV_VERSION
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN set -e; \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential apt-utils cmake wget git pkg-config gfortran zip unzip libjpeg-dev libtiff5-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libxvidcore-dev libx264-dev \
    libv4l-dev libatlas-base-dev libjasper-dev \
    vim python3-dev python2.7-dev

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

RUN apt-get update && apt-get install python3-pip python3-dev -y --no-install-recommends

# Install NumPy dependency for OpenCV
RUN pip3 install --upgrade pip && pip3 install numpy

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
	-D WITH_VTK=OFF \
	-D WITH_QT=OFF \
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

# Clean up installation
RUN set -e; \
    rm -rf /tmp/*

# Get application and dependencies
#RUN git clone $REPOSITORY .
#RUN cd /infrared-security-webcam; \
#    pip install -r requirements.txt

CMD ["/bin/bash"]
# CMD ["pm2", "start", "infrared-security-webcam/app.py", "--interpreter", "python3.8", "--name", "infrared-security-webcam", "--restart-delay", "5000"]
