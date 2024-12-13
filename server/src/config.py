import os

http_port = 8000
ffmpeg_pipeline = None

def required_env(key):
    value = os.getenv(key)
    
    if value is None:
        raise Exception(f'{key} is not set in environment variables')
    
    return value


def initialize():
    global http_port, ffmpeg_pipeline
    
    http_port = int(os.getenv('HTTP_PORT', http_port))
    ffmpeg_pipeline = required_env('FFMPEG_PIPELINE')

