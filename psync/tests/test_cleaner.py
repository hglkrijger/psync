import os
import shutil
import tempfile

from unittest import TestCase
from psync.cleaner import clean_segment, clean_path, clean


class TestCleaner(TestCase):

    def test_clean_path(self):
        src, dst = clean_path('/var/log/foo')
        self.assertEqual(src, dst)

    def test_clean_segment(self):
        self.assertEqual('foo_1_', clean_segment('foo(1)'))
        self.assertEqual('foo_1', clean_segment('foo 1'))
        self.assertEqual('foo-1', clean_segment('foo - 1'))
        self.assertEqual('foo.jpg', clean_segment('foo.jpg'))

    def test_clean(self):
        def create(f):
            with open(f, 'w') as fh:
                fh.write('')

        temp = tempfile.mkdtemp()
        try:
            a = os.path.join(temp, 'A')
            aa = os.path.join(a, 'A A')
            b = os.path.join(temp, 'B')
            c = os.path.join(temp, 'C C')

            os.mkdir(a)
            os.mkdir(aa)
            os.mkdir(b)
            os.mkdir(c)

            a1 = os.path.join(a, 'a1.txt')
            aa1 = os.path.join(aa, 'A 1.txt')
            b1 = os.path.join(b, '1.txt')
            c1 = os.path.join(c, 'C - 1.txt')
            c2 = os.path.join(c, 'C!1.txt')

            create(a1)
            create(aa1)
            create(b1)
            create(c1)
            create(c2)

            clean(temp, is_pretend=False)

        except Exception as e:
            self.fail(e)
        finally:
            shutil.rmtree(temp)
