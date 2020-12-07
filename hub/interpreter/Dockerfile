FROM python:3.8-slim
#AS builder
WORKDIR /opencv

ARG TARGETPLATFORM
ARG BUILDPLATFORM

ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=4
ENV OPENCV_VERSION=$OPENCV_VERSION
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential apt-utils cmake wget git pkg-config gfortran zip \
    unzip libjpeg-dev libtiff5-dev libavcodec-dev libavformat-dev \
    libswscale-dev libxvidcore-dev libx264-dev libv4l-dev \
    libatlas-base-dev v4l-utils curl \
    gstreamer1.0-plugins-base  gstreamer1.0-plugins-good ; \
    pip3 install --upgrade pip && pip3 install numpy --no-cache-dir; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*;

# Download OpenCV and module source
RUN cd /tmp; \
    wget -c -nv --no-check-certificate -O opencv.zip https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip; \
    unzip opencv.zip; \
    wget -c -nv --no-check-certificate -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip; \
    unzip opencv_contrib.zip; \
    mv opencv-${OPENCV_VERSION} opencv; \
    mv opencv_contrib-${OPENCV_VERSION} opencv_contrib
    
RUN cd /tmp/opencv; \
    mkdir build; \
    cd build; \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib/modules \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D WITH_QT=OFF \
        -D WITH_GTK=OFF \
        -D WITH_OPENCL=ON \
        -D WITH_VTK=OFF \
        -D WITH_OPENGL=OFF \
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
        -D BUILD_EXAMPLES=OFF \
        -D INSTALL_C_EXAMPLES=OFF \
        -D INSTALL_PYTHON_EXAMPLES=OFF \
        -D BUILD_DOCS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D BUILD_TESTS=OFF \
        .. ;

RUN cd /tmp/opencv/build; \
    make ; \
    make install; \
    ldconfig; \
    cd /opencv ; \
    rm -rf /tmp/*

RUN apt purge --auto-remove -y apt-utils gfortran libswscale-dev libxvidcore-dev \
    libx264-dev libv4l-dev libatlas-base-dev v4l-utils gstreamer1.0-plugins-base  \
    gstreamer1.0-plugins-good pkg-config cmake wget git zip unzip curl

#FROM python:3.8-slim

#RUN apt-get update; \
#    apt-get install -y curl wget gnupg gnupg2; \
#    echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee --append /etc/apt/sources.list.d/coral-edgetpu.list; \
#    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - ; \
#    apt-get update ; \
#    apt-get install libedgetpu1-std -y --no-install-recommends; \
#    apt-get clean; \
#    rm -rf /var/lib/apt/lists/*

#RUN if [ $TARGETLATFORM = 'linux/arm64' ] ; then \
#        wget https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp38-cp38-linux_aarch64.whl; \
#        pip3 install tflite_runtime-2.5.0-cp38-cp38-linux_aarch64.whl; \
#        tflite_runtime-2.5.0-cp38-cp38-linux_aarch64.whl; \
#    elif [ $TARGETPLATFORM = 'linux/arm/v7' ] ; then \
#        wget https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp38-cp38-linux_armv7l.whl; \
#        pip3 install tflite_runtime-2.5.0-cp38-cp38-linux_armv7l.whl; \
#        rm tflite_runtime-2.5.0-cp38-cp38-linux_armv7l.whl ; \
#    else \
#        wget  	https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp38-cp38-linux_x86_64.whl; \
#        pip3 install tflite_runtime-2.5.0-cp38-cp38-linux_x86_64.whl; \
#        rm tflite_runtime-2.5.0-cp38-cp38-linux_x86_64.whl ; \
#    fi

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