import logging
import sys

import colorlog



def set_header_trailer_formatter(handler):
    # handy function to print without time/level (for header / trailer)
    
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    

def set_usual_formatter(handler):
    # to print the main pipeline logging:
    
    formatter = colorlog.ColoredFormatter(
        "%(asctime)s %(log_color)s%(levelname)s%(reset)s: %(message)s", datefmt="%H:%M:%S",
        log_colors={'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'bold_red'})
    handler.setFormatter(formatter)


    
def get_logger(logger_id, verbose):

    
    # create a clean logger without handlers
    logger = logging.getLogger(logger_id)    
    if logger.hasHandlers(): 
        logger.handlers.clear()
        
    # stop bubbling up to root logger
    logger.propagate = False  
    
    
    # show everything on the stderr:
    handler = logging.StreamHandler(stream=sys.stderr)
    logger.addHandler(handler)
    
    # set the level 
    if verbose: logger.setLevel(logging.DEBUG) # debug (lvl 10) and up
    else:       logger.setLevel(logging.INFO) # debug (lvl 20) and up
    
    # attach the default formatter
    set_usual_formatter(handler)
    
    
    return logger