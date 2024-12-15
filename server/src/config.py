import os

debug = False
http_port = 8000
ffmpeg_pipeline = None
data_dir = '/data'
start_on_boot = False

def required_env(key):
    value = os.getenv(key)
    
    if value is None:
        raise Exception(f'{key} is not set in environment variables')
    
    return value


def initialize():
    global http_port, ffmpeg_pipeline, debug, data_dir, start_on_boot
    
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    start_on_boot = os.getenv('START_ON_BOOT', 'false').lower() == 'true'
    http_port = int(os.getenv('HTTP_PORT', http_port))
    ffmpeg_pipeline = required_env('FFMPEG_PIPELINE')
    data_dir = os.getenv('DATA_DIR', data_dir)
    

