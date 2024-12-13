import logging
import threading
from flask import Flask

import config

logger = logging.getLogger()

app = Flask(__name__)

class HttpServer(threading.Thread):
    """
    Creates a new flask HTTP server.
    """

    def __init__(self):
        super().__init__(daemon=True, name="http_server")


    def run(self):
        """"
        Runs the flask server. This is a blocking call.
        """

        logger.info("Starting flask server")

        # if debug is set to True, you can't access
        # flask across a network
        app.debug = False

        try:
            app.run(host="0.0.0.0", port=config.http_port, debug=False)
        except KeyboardInterrupt:
            logger.info("Flask got interrupt. Quitting.")
