import os
import logging
from time import sleep

import configparser

from psync.syncer import Sync

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
        logger.info('creating daemon')
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.interval = config.getint('default', 'sync_interval')
        self.is_running = False
        self.sync = Sync(is_pretend=False)

    def run(self):
        self.is_running = True
        while self.is_alive:
            self.sync.run()
            sleep(self.interval * 60)

    def stop(self):
        logger.info('stopping daemon')
        self.is_running = False
