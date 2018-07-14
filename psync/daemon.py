import os
import threading
import logging
from time import sleep

log_location = '/var/log' if os.path.exists('/var/log') else ''
logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                    filename=os.path.join(log_location, 'psync.log'))


class Daemon(object):

    @property
    def is_alive(self):
        return self.is_running

    def __init__(self):
        self.is_running = True
        self.interval = 5

        logger.info('creating daemon')
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        while self.is_running:
            logger.info('daemon running')
            sleep(self.interval)

    def stop(self):
        logger.info('stopping daemon')
        self.is_running = False