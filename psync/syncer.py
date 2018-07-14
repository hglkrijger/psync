import os
import logging
from uuid import UUID

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


def refresh_session(secret_or_client, is_pretend):
    client_id = None
    if os.path.exists(secret_or_client):
        config = configparser.ConfigParser()
        config.read(secret_or_client)
        client_id = config['default']['client_id']
    else:
        try:
            UUID(secret_or_client, version=4)
            client_id = secret_or_client
        except ValueError:
            pass

    if client_id is None:
        logger.error('client_id could not be determined')
        return

    logger.info('loading session for app %s %s', client_id, '[dry-run]' if is_pretend else '')

    scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readonly']
    client = onedrivesdk.get_default_client(client_id=client_id, scopes=scopes)

    if is_pretend:
        logger.info('refreshing token')
        return

    client.auth_provider.load_session()
    client.auth_provider.refresh_token()

    logger.info('token refreshed')
