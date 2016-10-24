import os
import unittest2
from zpath import zpath, util
import shutil


def copy_f(src, dst):
    try:
        util.make_writable(dst)
    except WindowsError:
        pass
    shutil.copy(src, dst)


class Tester(unittest2.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir('cases')

    def test_zip(self):
        copy_f('zip/t1.original.zip', 'zip/t1.zip')
        zpath.copy('zip/token.txt', 'zip/t1.zip')
        self.assertEqual(
            zpath.compare('zip/t1.zip', 'zip/t1.expected.zip'),
            True)
        os.remove('zip/t1.zip')

    def test_nested_zip(self):
        copy_f('zip/lc3.original.zip', 'zip/lc3.zip')
        zpath.copy('zip/token.txt', 'zip/lc3.zip/lc2/lc.zip')
        self.assertEqual(
            zpath.compare(
                'zip/lc3.zip/lc2/lc.zip',
                'zip/lc3.expected.zip/lc2/lc.zip'),
            True)
        os.remove('zip/lc3.zip')

    def test_abs_path(self):
        copy_f('zip/lc3.original.zip', 'zip/lc3.zip')
        zip_abs = os.path.abspath('zip/lc3.zip/lc2/lc.zip')
        zpath.copy('zip/token.txt', zip_abs)
        self.assertEqual(
            zpath.compare(
                zip_abs,
                'zip/lc3.expected.zip/lc2/lc.zip'),
            True)
        os.remove('zip/lc3.zip')

    def test_tar(self):
        copy_f('tar/pip.original.tar', 'tar/pip.tar')
        zpath.copy('tar/LICENSE.txt', 'tar/pip.tar/pip-7.1.0')
        self.assertEqual(
            zpath.compare('tar/pip.tar', 'tar/pip.expected.tar'),
            True)
        os.remove('tar/pip.tar')

    def test_tar_gz(self):
        copy_f('gz/pip.original.tar.gz', 'gz/pip.tar.gz')
        zpath.copy('gz/LICENSE.txt', 'gz/pip.tar.gz/pip.tar/pip-7.1.0')
        self.assertEqual(
            zpath.compare(
                'gz/pip.tar.gz/pip.tar',
                'gz/pip.expected.tar.gz/pip.expected.tar'),
            True)
        os.remove('gz/pip.tar.gz')

    def test_mixed(self):
        copy_f('mixed/pip.original.tar.gz.zip', 'mixed/pip.zip')
        zpath.copy('mixed/LICENSE.txt',
                   'mixed/pip.zip/pip.tar.gz/pip.tar/pip-7.1.0')
        self.assertEqual(
            zpath.compare(
                'mixed/pip.zip/pip.tar.gz/pip.tar',
                'mixed/pip.expected.tar.gz.zip/pip.tar.gz/pip.tar'),
            True)
        os.remove('mixed/pip.zip')