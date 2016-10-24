"""
This module provides universal file manipulating functions.

When invoking one of the functions, you can pass in either normal file paths,
or paths that contain compressed files. For example, if you have a file
located in a normal directory::

  C:/example/dir/file.txt

and a file located in a compressed archive named ``archive.tar.gz``::

  C:/example/compressed/archive.tar.gz/archive.tar/file.txt

and you'd like to replace the ``file.txt`` in the archive with the other,
just call ``ori_zip.zpath.copy`` like this::

  copy('C:/example/dir/file.txt',
       'C:/example/compressed/archive.tar.gz/archive.tar/file.txt')

To construct custom functions that work on zpaths, use the ``access`` function
to create context managers that provide access to zpaths.
For example, doing this::

  with access('C:/example/compressed/archive.tar.gz/archive.tar') as path:
    copy(os.path.join(path, 'file.txt'), 'C:/example/dir')

will copy the archived ``file.txt`` to ``C:/example/dir``.
You can treat the variable ``path`` in the code above as an
accessible version of ``C:/example/compressed/archive.tar.gz/archive.tar``.
"""

import compress
import util
import tempfile
import os
import filecmp
from contextlib import contextmanager
from functools import wraps


def join(zpath_1, zpath_2):
    return os.path.join(zpath_1, zpath_2)


def normalize(zpath):
    return os.path.normpath(zpath)


def to_list(path):
    if not path:
        return []
    path, filename = os.path.split(path)
    if not filename:
        return [path]
    return to_list(path) + [filename]


def access(zpath, readonly=False):
    """ create a context manager to access a zpath
    """
    @contextmanager
    def compress_accessor(compressed):
        decompressed = tempfile.mkdtemp()
        compress.unpack(compressed, decompressed)
        yield decompressed
        if not readonly:
            compress.pack(decompressed, compressed)
        util.remove_dir_f(decompressed)

    @contextmanager
    def normal_accessor(dir_or_file):
        yield dir_or_file

    def get_accessor(filename):
        if compress.is_compressed(filename):
            return compress_accessor
        else:
            return normal_accessor

    @contextmanager
    def create_nested_accessor(parent_accessor, filename):
        accessor = get_accessor(filename)
        with parent_accessor as parent_path:
            path_to_access = os.path.join(parent_path, filename)
            with accessor(path_to_access) as path:
                yield path

    zpath = normalize(zpath)
    return reduce(create_nested_accessor, to_list(zpath), normal_accessor('.'))


def access_readonly(zpath):
    return access(zpath, True)


def extend_to_zpath(accessor_1, accessor_2):
    def decorator(func):
        @wraps(func)
        def wrapper(zpath_1, zpath_2):
            with accessor_1(zpath_1) as p1, accessor_2(zpath_2) as p2:
                return func(p1, p2)
        return wrapper
    return decorator


@extend_to_zpath(access_readonly, access)
def copy(p1, p2):
    """ copy files or directories under normal paths or zpaths
    """
    util.meta_copy(p1, p2)


@extend_to_zpath(access, access)
def move(p1, p2):
    """ move files or directories under normal paths or zpaths
    """
    util.move(p1, p2)


@extend_to_zpath(access_readonly, access_readonly)
def compare(p1, p2):
    """ compare files or directories under normal paths or zpaths
    """
    def is_result_equal(dircmp_obj):
        def eq(o):
            return o.left_only == o.right_only == o.diff_files == []
        return eq(dircmp_obj) and all(map(is_result_equal,
                                          dircmp_obj.subdirs.values()))

    is_dir_1 = os.path.isdir(p1)
    is_dir_2 = os.path.isdir(p2)

    if is_dir_1 and is_dir_2:
        return is_result_equal(filecmp.dircmp(p1, p2))

    if not is_dir_1 and not is_dir_2:
        return filecmp.cmp(p1, p2)
    return False
