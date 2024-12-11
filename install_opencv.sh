sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

git clone https://github.com/opencv/opencv.git

cmake \
-D BUILD_JAVA=OFF \
-D BUILD_PYTHON=ON \
-D BUILD_opencv_java=OFF \
-D BUILD_opencv_java_bindings_generator=OFF \
-D BUILD_opencv_js=OFF \
-D BUILD_opencv_js_bindings_generator=OFF \
-D BUILD_opencv_python3=ON \
-D BUILD_opencv_python_bindings_generator=ON \
-D BUILD_opencv_python_tests=OFF \
-D BUILD_EXAMPLES=OFF \
-D BUILD_TESTS=OFF \
-D BUILD_PERF_TESTS=OFF \
-D BUILD_opencv_apps=OFF \
-D WITH_FFMEG=OFF \
-D WITH_ONNX=ON \
-D WITH_GSTREAMER=ON \
-D WITH_V4L=ON \
../opencv

cmake --build .

sudo make install