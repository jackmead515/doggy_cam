import util
import config

if __name__ == "__main__":
    
    util.compile()
    
    config.initialize()
    
    import core
    
    core.run()