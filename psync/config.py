import ast
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
        return self.config.getint('service', 'sync_interval')

    @property
    def owner(self):
        return self.config['service']['owner']

    @property
    def accounts(self):
        return ast.literal_eval(self.config['service']['accounts'])

    @property
    def redirect_uri(self):
        return self.config['secrets']['redirect_uri']

    @property
    def client_secret(self):
        return self.config['secrets']['client_secret']

    @property
    def client_id(self):
        return self.config['secrets']['client_id']

    def session_file(self, account):
        if not self.config.has_section(account):
            raise Exception('Account %s not defined', account)

        return self.config[account]['session_file']

    def sync_src(self, account):
        if not self.config.has_section(account):
            raise Exception('Account %s not defined', account)

        return self.config[account]['sync_src']

    def sync_dst(self, account):
        if not self.config.has_section(account):
            raise Exception('Account %s not defined', account)

        return self.config[account]['sync_dst']

