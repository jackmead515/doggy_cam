import util
import config

if __name__ == "__main__":
    
    util.compile()
    
    config.initialize()
    
    import core
    import server 
    import eventer

    server = server.HttpServer()
    events = eventer.Eventer()
    
    server.start()
    events.start()
    
    core.run()
    
    server.join()
    events.stop()