import os
import logging

import configparser


class Configuration(object):

    config_file = '/etc/psync.conf' if os.path.exists('/etc/psync.conf') else 'psync.conf'

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.logger.info('loading configuration from {0}'.format(Configuration.config_file))
        self.config.read(Configuration.config_file)

    @property
    def sync_interval(self):
        return self.config.getint('default', 'sync_interval')

    @property
    def secrets_path(self):
        return self.config['default']['secrets_path']

    @property
    def sync_src(self):
        return self.config['default']['sync_src']

    @property
    def sync_dst(self):
        return self.config['default']['sync_dst']

    @property
    def redirect_uri(self):
        return self.config['secrets']['redirect_uri']

    @property
    def client_secret(self):
        return self.config['secrets']['client_secret']

    @property
    def client_id(self):
        return self.config['secrets']['client_id']
