import os
from unittest import TestCase
from psync.config import Configuration


class TestConfig(TestCase):

    def test_defaults(self):
        Configuration.config_file = os.path.abspath(os.path.join(os.curdir,
                                                                 os.path.pardir,
                                                                 os.path.pardir,
                                                                 'psync.conf'))
        self.assertTrue(os.path.exists(Configuration.config_file))

        c = Configuration()

        self.assertEqual(10, c.sync_interval)
        self.assertEqual('www-data', c.owner)
        self.assertEqual(['one', 'two'], c.accounts)

        self.assertEqual('http://localhost:8080/', c.redirect_uri)
        self.assertEqual('client_secret', c.client_secret)
        self.assertEqual('client_id', c.client_id)

        self.assertEqual('session-one.pickle', c.session_file('one'))
        self.assertEqual('Pictures/Camera Roll 1', c.sync_src('one'))
        self.assertEqual('/datadisk/galleries/OneDrive 1', c.sync_dst('one'))

        self.assertEqual('session-two.pickle', c.session_file('two'))
        self.assertEqual('Pictures/Camera Roll 2', c.sync_src('two'))
        self.assertEqual('/datadisk/galleries/OneDrive 2', c.sync_dst('two'))
