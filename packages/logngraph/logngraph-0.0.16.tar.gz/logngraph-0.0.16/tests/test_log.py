from logngraph.log import get_logger
from logngraph.log.levels import *
from time import sleep
from test_log2 import *
import threading as t

logger = get_logger(__name__, 'test.log', TRACE, True)

def main_too():
    while True:
        logger.trace("Hello, World!")
        sleep(0.2)
        logger.debug("Hello, World!")
        sleep(0.2)
        logger.info("Hello, World!")
        sleep(0.2)
        logger.warn("Hello, World!")
        sleep(0.2)
        logger.error("Hello, World!")
        sleep(0.2)
        logger.fatal("Hello, World!")
        logger.set_level(INFO)
        sleep(0.2)
        logger.trace("Hello, World!")
        sleep(0.2)


if __name__ == '__main__':
    t.Thread(target=main_too).start()
    t.Thread(target=main).start()

