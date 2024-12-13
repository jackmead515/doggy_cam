from flask import Blueprint

import services.streams as stream_service
import config

mod = Blueprint('stream', __name__)

@mod.route('/api/stream', methods=['POST'])
def create_stream():

    stream_service.launch_stream(config.ffmpeg_pipeline)
    
    return 'OK', 200


@mod.route('/api/stream', methods=['DELETE'])
def delete_stream():
    stream_service.kill_stream()
    
    return 'OK', 200