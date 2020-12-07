FROM raspbian/stretch:latest AS builder

WORKDIR /builder

ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=4
ENV OPENCV_VERSION=$OPENCV_VERSION
ARG DEBIAN_FRONTEND=noninteractive
ENV PATH="$PATH:/opt/vc/bin"

RUN echo "/opt/vc/lib" | tee --append /etc/ld.so.conf.d/00-vcms.conf; \
    ldconfig

# Install build dependencies
RUN set -e; \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential apt-utils cmake wget git pkg-config gfortran unzip libjpeg-dev libtiff5-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libxvidcore-dev libx264-dev \
    libv4l-dev libatlas-base-dev libjasper-dev \
    python3-dev python2.7-dev; \
    apt-get install -y --no-install-recommends python3-pip; \
    pip3 install --upgrade pip; \
    pip3 install numpy --no-cache-dir; \
    apt-get clean; \
    apt-get -y autoremove; \
    rm -rf /var/lib/apt/lists/*;

# Install OpenCV source and build/install
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
        -D WITH_QT=OFF \
        -D WITH_GTK=OFF \
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
        -D BUILD_EXAMPLES=OFF \
        -D INSTALL_C_EXAMPLES=OFF \
        -D INSTALL_PYTHON_EXAMPLES=OFF \
        -D BUILD_DOCS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D BUILD_TESTS=OFF \
        .. ; \
    	make -j$CPU_CORES; \
    	make install; \
        rm -rf /tmp/*

RUN apt-get purge -y build-essential apt-utils cmake wget git pkg-config gfortran unzip libjpeg-dev libtiff5-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libxvidcore-dev libx264-dev \
    libv4l-dev libatlas-base-dev libjasper-dev \
    python3-dev python2.7-dev; 

FROM raspbian/stretch:latest
WORKDIR /security-cam
COPY --from=builder /usr/local/ /usr/local/
RUN ldconfig /usr/local
COPY . .

CMD ["python", "security-cam.py"]
