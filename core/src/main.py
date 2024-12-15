import time
import logging

import util
import config


if __name__ == "__main__":
    
    util.compile()
    
    config.initialize()
    
    logging.basicConfig(level=logging.DEBUG)
    
    import core
    import server 
    import eventer

    server = server.HttpServer()
    events = eventer.Eventer()
    
    server.start()
    events.start()
    
    while True:
        try:
            core.run()
        except Exception as e:
            logging.exception(e)
            time.sleep(0.5)
            continue
        except KeyboardInterrupt:
            break

    server.join()
    events.stop()