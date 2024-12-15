import logging
import time
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

import config

config.initialize()

logging.basicConfig(level=logging.INFO)

from routes import stream as stream_routes
from routes import healthz as healthz_routes

app.register_blueprint(stream_routes.mod)
app.register_blueprint(healthz_routes.mod)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/jsmpeg.min.js')
def jsmpeg():
    return app.send_static_file('jsmpeg.min.js')


if __name__ == '__main__':
    """    
    curl -X POST http://localhost:8000/api/stream
    """
    
    if config.start_on_boot:
        import services.streams as stream_service
        
        time.sleep(3)
        stream_service.launch_stream()
    
    app.run(
        host='0.0.0.0',
        port=config.http_port,
        threaded=True,
        debug=False
    )