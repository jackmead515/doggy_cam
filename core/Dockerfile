FROM debian:stable-slim

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

COPY --link --from=ghcr.io/astral-sh/uv:0.5.2 /uv /usr/local/bin/uv

WORKDIR /app

RUN uv python install 3.10

COPY .python-version pyproject.toml .

RUN uv sync -v

COPY src ./src

COPY hapa.onnx .

CMD ["uv", "run", "src/main.py"]



# FROM ubuntu:20.04

# RUN apt-get update && apt-get upgrade -y

# RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
#     tzdata \
#     libgstreamer1.0-0 \
# 	gstreamer1.0-plugins-base \
# 	gstreamer1.0-plugins-good \
# 	gstreamer1.0-plugins-bad \
# 	gstreamer1.0-plugins-ugly \
# 	gstreamer1.0-libav \
# 	gstreamer1.0-doc \
# 	gstreamer1.0-tools \
# 	libgstreamer1.0-dev \
# 	libgstreamer-plugins-base1.0-dev \
#     libgstreamer-plugins-bad1.0-dev \
#     gstreamer1.0-x \
#     gstreamer1.0-gl \
#     git \
#     gcc \
#     build-essential \
#     libssl-dev \
#     cmake \
#     curl \
#     ca-certificates \
#     && apt clean \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# RUN apt-get update && apt-get install -y python3-pip software-properties-common

# RUN add-apt-repository ppa:deadsnakes/ppa -y

# RUN apt install python3.10 python3.10-dev python3.10-distutils -y

# #RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# RUN python3 -m pip install --upgrade pip

# # symlink python3.10 to python3
# RUN ln -sf /usr/bin/python3.10 /usr/bin/python3

# #ENV OPENCV_VER "master"
# # Build and install OpenCV from source.
# # RUN git clone https://github.com/opencv/opencv-python.git \
# #     && cd opencv-python \
# #     && git checkout $OPENCV_VER \
# #     && export ENABLE_CONTRIB=1 \
# #     && export ENABLE_HEADLESS=1 \
# #     && export CMAKE_ARGS="-DWITH_GSTREAMER=ON" \
# #     && python3 -m pip wheel . --verbose \
# #     && python3 -m pip install opencv_python*.whl \
# #     && rm -rf opencv-python

# RUN git clone https://github.com/opencv/opencv.git

# RUN cd opencv \
#     && git checkout 4.10.0 \
#     && git submodule update --recursive --init \
#     && mkdir build \
#     && cd build \
#     && cmake \
#     -D CMAKE_BUILD_TYPE=RELEASE \
#     -D INSTALL_PYTHON_EXAMPLES=ON \
#     -D BUILD_opencv_python3=ON \
#     -D PYTHON_EXECUTABLE=$(which python3) \
#     -D PYTHON3_EXECUTABLE=$(which python3) \
#     -D CMAKE_INSTALL_PREFIX=$(python3 -c "import sys; print(sys.prefix)") \
#     -D WITH_GSTREAMER=ON \
#     -D BUILD_EXAMPLES=OFF \
#     -D BUILD_TESTS=OFF \
#     -D BUILD_PERF_TESTS=OFF \
#     -D INSTALL_C_EXAMPLES=OFF \
#     -D BUILD_opencv_python2=OFF \
#     -D WITH_FFMPEG=OFF ../ \
#     && make -j$(nproc) \
#     && make install \
#     && ldconfig

#     #-D CMAKE_INSTALL_PREFIX=$(.venv/bin/python3 -c "import sys; print(sys.prefix)") \
#     #-D PYTHON3_INCLUDE_DIR=$(.venv/bin/python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
#     #-D PYTHON3_PACKAGES_PATH=$(.venv/bin/python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \

# COPY requirements.txt .

# RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# RUN python3 -m pip install -r requirements.txt

# COPY src ./src

# CMD ["python3", "src/main.py"]