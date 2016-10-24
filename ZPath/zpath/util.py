import os
import stat
import itertools
import shutil


def walk_files(dir_path):
    """
    :parameter dir_path: the directory to walk
    :return: an iterable of (real_file_path, relative_file_path)
    """
    def walk_files_with_abspath(dir_path):
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                yield os.path.join(root, f)

    def strip_root_path(path, root_path):
        return path.replace(root_path, '', 1)

    dir_path = os.path.normpath(dir_path)
    return itertools.imap(
        lambda p: (p, strip_root_path(p, dir_path)),
        walk_files_with_abspath(dir_path))


def make_writable(file_path):
    os.chmod(file_path, stat.S_IWRITE)


def meta_copy(file_path, directory):
    shutil.copy2(file_path, directory)


def move(src, dst):
    shutil.move(src, dst)


def remove_dir_f(dir_path):
    def retry_delete(action, name, exc):
        make_writable(name)
        os.remove(name)
    shutil.rmtree(dir_path, onerror=retry_delete)
