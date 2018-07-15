import datetime
import os
import logging

import configparser
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from uuid import UUID

logger = logging.getLogger(__name__)
session_file = 'session.pickle'
scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']


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
    client = onedrivesdk.get_default_client(client_id=client_id, scopes=scopes)

    if is_pretend:
        logger.info('refreshing token')
        return

    client.auth_provider.load_session()
    client.auth_provider.refresh_token()

    logger.info('token refreshed')

    return client


class Sync(object):

    def __init__(self, is_pretend):
        config = configparser.ConfigParser()
        config.read('config.ini')
        secrets_path = config['default']['secrets_path']
        self.sync_src = config['default']['sync_src']
        self.sync_dst = config['default']['sync_dst']
        self.client = refresh_session(secrets_path, is_pretend=False)
        self.is_pretend = is_pretend

    def run(self):
        logger.debug('sync running')
        src_id = self.find_id(self.sync_src)
        src_items = self.list_all(src_id)
        logger.debug('sync {0} items to {1}'.format(len(src_items), self.sync_dst))
        if not os.path.exists(self.sync_dst):
            logger.error('{0} does not exist'.format(self.sync_dst))
            return
        dst_items = self.list_files(self.sync_dst)
        logger.debug('{0} items exist in {1}'.format(len(dst_items), self.sync_dst))

        for src_item in src_items:
            year = src_item.created_date_time.strftime("%Y")
            month = src_item.created_date_time.strftime("%m")
            day = src_item.created_date_time.strftime("%d")
            full_path = os.path.join(self.sync_dst, year, month, day)
            self.download(src_item.id, src_item.name, full_path)

            if datetime.datetime.utcnow() - src_item.created_date_time > datetime.timedelta(days=365):
                logger.info('{0} is over a year old, removing..'.format(src_item.name))
                self.delete(src_item.id)

        logger.debug('sync completed')

    @staticmethod
    def list_files(path):
        items = []
        for root, sub_dirs, files in os.walk(path):
            for filename in files:
                file_path = os.path.join(root, filename)
                items.append(file_path)
                logger.debug(file_path)
        return items

    def find_id(self, path, item_id='root'):
        logger.debug('find path={0}, item_id={1}'.format(path, item_id))
        folders = path.split('/')
        folder = folders[0]
        remaining_path = '/'.join(folders[1:])
        items = self.list_all(item_id)
        for item in items:
            if item.name == folder:
                logger.debug('found {0}, id {1}'.format(item.name, item.id))
                if remaining_path is '':
                    return item.id
                return self.find_id(remaining_path, item.id)
        logger.error('{0} not found'.format(path))
        return None

    def next(self, items):
        ret_items = None
        try:
            ret_items = onedrivesdk.ChildrenCollectionRequest.get_next_page_request(items, self.client).get()
        except Exception:
            pass
        return ret_items

    def first(self, item_id):
        return self.client.item(id=item_id).children.request(top=100).get()

    def list_all(self, item_id):
        all_items = []
        items = self.first(item_id)
        for i in items:
            all_items.append(i)
        while items is not None:
            items = self.next(items)
            if items is not None:
                for i in items:
                    all_items.append(i)
        logger.debug('{0} items found in {1}'.format(len(all_items), item_id))
        return all_items

    def print_list(self, item_id):
        items = self.list_all(item_id)
        for i in items:
            logger.info('[{:23}] {}{}'.format(i.id, i.name, '' if i.folder is None else '/'))

    def download(self, item_id, item_name, folder):
        if not os.path.exists(folder) and not self.is_pretend:
            logger.info('creating {0}'.format(folder))
            os.makedirs(folder)
        if os.path.exists(os.path.join(folder, item_name)):
            logger.debug('{0} already exists, skipping'.format(item_name))
            return
        logger.info('download {0} to {1}'.format(item_name, folder))
        if not self.is_pretend:
            self.client.item(id=item_id).download(os.path.join(folder, item_name))

    def delete(self, item_id):
        if not self.is_pretend:
            self.client.item(id=item_id).delete()
