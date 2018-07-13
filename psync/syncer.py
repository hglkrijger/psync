import os
import logging
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
import configparser

logger = logging.getLogger(__name__)
session_file = 'session.pickle'


def new_session(secrets_config, is_pretend):
    if not os.path.exists(secrets_config):
        logger.error('%s does not exist', secrets_config)
        return

    logger.info('new session, loading %s %s', secrets_config, '[dry-run]' if is_pretend else '')

    config = configparser.ConfigParser()
    config.read(secrets_config)

    redirect_uri = config['default']['redirect_uri']
    client_secret = config['default']['client_secret']
    client_id = config['default']['client_id']
    scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readonly']

    logger.info('loaded secrets successfully')

    if is_pretend:
        logger.info('authenticate app %s at %s', client_id, redirect_uri)
        return

    client = onedrivesdk.get_default_client(client_id=client_id, scopes=scopes)
    auth_url = client.auth_provider.get_auth_url(redirect_uri)
    logger.info('authenticating via the browser...')
    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
    client.auth_provider.authenticate(code, redirect_uri, client_secret)
    client.auth_provider.save_session()

    if os.path.exists(session_file):
        logger.info('session saved to %s', session_file)
    else:
        logger.warn('expected session file not found [%s]', session_file)
