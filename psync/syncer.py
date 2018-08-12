import shutil

import datetime
import os
import logging
import onedrivesdk

from onedrivesdk.helpers import GetAuthCodeServer
from psync.config import Configuration


logger = logging.getLogger(__name__)
scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']


class Sync(object):

    def __init__(self, is_pretend):
        self.config = Configuration()
        self.is_pretend = is_pretend
        self.accounts = self.config.accounts
        self.client = None

        try:
            from pwd import getpwnam
            pw = getpwnam(self.config.owner)
            self.uid = pw.pw_uid
            self.gid = pw.pw_gid
        except Exception:
            self.uid = 0
            self.gid = 0

    def run(self):
        for account in self.accounts:
            logger.debug('[{0}] sync running'.format(account))

            self.client = self.refresh_session(account)
            src = self.config.sync_src(account)
            dst = self.config.sync_dst(account)

            src_id = self.find_id(src)
            src_items = self.list_all(src_id)
            logger.debug('sync {0} items to {1}'.format(len(src_items), dst))
            if not os.path.exists(dst):
                logger.error('{0} does not exist'.format(dst))
                return
            dst_items = self.list_files(dst)
            logger.debug('{0} items exist in {1}'.format(len(dst_items), dst))

            for src_item in src_items:
                year = src_item.created_date_time.strftime("%Y")
                month = src_item.created_date_time.strftime("%m")
                day = src_item.created_date_time.strftime("%d")
                full_path = os.path.join(dst, year, month, day)
                self.download(src_item.id, src_item.name, full_path)

                if datetime.datetime.utcnow() - src_item.created_date_time > datetime.timedelta(days=365):
                    logger.info('{0} is over a year old, removing..'.format(src_item.name))
                    self.delete(src_item.id)

            logger.debug('[{0}] sync completed'.format(account))

    def new_session(self, account):
        redirect_uri = self.config.redirect_uri
        client_secret = self.config.client_secret
        client_id = self.config.client_id
        session_file = self.config.session_file(account)

        logger.info('loaded secrets successfully')

        if self.is_pretend:
            logger.info('authenticate account "%s" for app %s at %s', account, client_id, redirect_uri)
            return

        client = onedrivesdk.get_default_client(client_id=client_id, scopes=scopes)
        auth_url = client.auth_provider.get_auth_url(redirect_uri)
        logger.info('authenticating account "%s" via the browser...', account)
        code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
        client.auth_provider.authenticate(code, redirect_uri, client_secret)
        client.auth_provider.save_session(path=session_file)

        if os.path.exists(session_file):
            logger.info('session saved to %s for account %s', session_file, account)
        else:
            logger.warn('expected session file not found [%s]', session_file)

    def refresh_session(self, account):
        client_id = self.config.client_id
        session_file = self.config.session_file(account)

        logger.info('loading session for account %s, app %s %s',
                    account,
                    client_id,
                    '[dry-run]' if self.is_pretend else '')
        client = onedrivesdk.get_default_client(client_id=client_id, scopes=scopes)

        client.auth_provider.load_session(path=session_file)
        client.auth_provider.refresh_token()

        logger.info('token refreshed for %s', account)

        return client

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
        full_path = os.path.join(folder, item_name)
        if not os.path.exists(folder) and not self.is_pretend:
            logger.info('creating {0}'.format(folder))
            os.makedirs(folder, 0o755)
            os.chown(folder, self.uid, self.gid)
        if os.path.exists(full_path):
            logger.debug('{0} already exists, skipping'.format(item_name))
            return
        # move previously synced file if it exists
        orig = os.path.join(self.sync_dst, item_name)
        if os.path.exists(orig):
            logger.warn("{0} exists, moving".format(orig))
            if not self.is_pretend:
                shutil.move(orig, full_path)
        else:
            logger.info('download {0} to {1}'.format(item_name, folder))
            if not self.is_pretend:
                self.client.item(id=item_id).download(full_path)
        if not self.is_pretend:
            os.chmod(full_path, 0o644)
            os.chown(full_path, self.uid, self.gid)

    def delete(self, item_id):
        if not self.is_pretend:
            self.client.item(id=item_id).delete()
