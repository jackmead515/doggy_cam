import logging
import threading
import subprocess
import time
import shlex
import signal
from subprocess import TimeoutExpired

import config

_stream = None
_streams_lock = threading.Lock()


def kill_stream():
    global _stream, _streams_lock

    with _streams_lock:
        if _stream is not None:
            logging.info('Killing pipeline')
            
            _stream.send_signal(signal.SIGINT)
            try:
                exit_code = _stream.wait(timeout=5)
            except TimeoutExpired:
                _stream.kill()

        _stream = None

        # final any ffmpeg processes that may have been left running
        subprocess.run(['pkill', 'ffmpeg'])


def launch_stream():
    global _stream, _streams_lock
    
    kill_stream()

    with _streams_lock:
        pipeline = shlex.split(config.ffmpeg_pipeline)
        logging.info(f'Running pipeline: {pipeline}')

        if config.debug:
            _stream = subprocess.Popen(pipeline, cwd=config.data_dir)
        else:
            _stream = subprocess.Popen(pipeline, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=config.data_dir)