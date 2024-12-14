import os
import logging

# camera input parameters
input_pipe = 0 # input pipeline to give to opencv
width = 640 # frame width
height = 480 # frame height
fps = 30 # frames per second

# motion detection parameters
guassian_blur = 17 # blur kernel to use for guassian blur
window_perc = 0.1 # 10% of image creates 10x10 = 100 pixel window
noise_threshold = 64 # used to remove noise from the scene
total_motion_threshold = 0.04 # 5% of window must have changed from previous frame to detect motion
motion_detected_windows = 3 # number of windows to detect motion

# object tracking and detection parameters
tracker_frames = 5 # number of frames to track the object
detect_conf_threshold = 0.7 # confidence threshold for detection of dog
redetect_interval = 30 # number of frames to re-detect the object
model_path = "hapa.onnx" # path to the model to load

# kafka parameters
kafka_brokers = None
kafka_max_block_ms = 1000
kafka_retries = 5
http_port = 5000
kafka_topic = 'core.events'


def required_env(key):
    """
    Gets the provided key from os and if the value
    is None, raises an Exception
    """
    value = os.getenv(key)
    if value is None:
        raise Exception(f'{key} is a required env variable')
    return value



def initialize():
    global kafka_brokers, kafka_max_block_ms, kafka_retries, http_port, kafka_topic
    global input_pipe, width, height, fps, detect_conf_threshold, guassian_blur
    global window_perc, noise_threshold, tracker_frames
    global total_motion_threshold, redetect_interval, model_path
    global motion_detected_windows

    # setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    kafka_brokers = required_env('KAFKA_BROKERS')
    kafka_brokers = [k.strip() for k in kafka_brokers.split(',')]
    
    kafka_max_block_ms = int(os.getenv('KAFKA_MAX_BLOCK_MS', kafka_max_block_ms))
    kafka_retries = int(os.getenv('KAFKA_RETRIES', kafka_retries))
    http_port = int(os.getenv('HTTP_PORT', http_port))
    kafka_topic = os.getenv('KAFKA_TOPIC', kafka_topic)
    
    input_pipe = os.getenv('INPUT_PIPE', input_pipe)
    width = int(os.getenv('WIDTH', width))
    height = int(os.getenv('HEIGHT', height))
    fps = int(os.getenv('FPS', fps))
    detect_conf_threshold = float(os.getenv('DETECT_CONF_THRESHOLD', detect_conf_threshold))
    guassian_blur = int(os.getenv('GUASSIAN_BLUR', guassian_blur))
    window_perc = float(os.getenv('WINDOW_PERC', window_perc))
    noise_threshold = int(os.getenv('NOISE_THRESHOLD', noise_threshold))
    tracker_frames = int(os.getenv('TRACKER_FRAMES', tracker_frames))
    total_motion_threshold = float(os.getenv('TOTAL_MOTION_THRESHOLD', total_motion_threshold))
    redetect_interval = int(os.getenv('REDETECT_INTERVAL', redetect_interval))
    motion_detected_windows = int(os.getenv('MOTION_DETECTED_WINDOWS', motion_detected_windows))
    model_path = os.getenv('MODEL_PATH', model_path)