import shutil
import os
import gzip
import struct
from gzip import FEXTRA, FNAME


def pack_file(file_path, gz_file_path):
    with open(file_path, 'rb') as f_in:
        with gzip.open(gz_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def unpack_file(gz_file_path, file_path):
    with gzip.open(gz_file_path, 'rb') as tf:
        with open(file_path, 'wb') as f:
            f.write(tf.read())


def pack(dir_path, gz_file_path):
    pack_file(
        os.path.join(dir_path, get_first_file_in_dir(dir_path)),
        gz_file_path)


def unpack(gz_file_path, dir_path):
    with gzip.GzipFile(gz_file_path) as f:
        filename, filesize = read_gzip_info(f)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    unpack_file(gz_file_path, os.path.join(dir_path, filename))


def get_first_file_in_dir(dir_path):
    _, _, files = os.walk(dir_path).next()
    return files[0]


def read_gzip_info(gzipfile):
    gf = gzipfile.fileobj
    pos = gf.tell()

    # Read archive size
    gf.seek(-4, 2)
    size = struct.unpack('<I', gf.read())[0]

    gf.seek(0)
    magic = gf.read(2)
    if magic != '\037\213':
        raise IOError('Not a gzipped file')

    method, flag, mtime = struct.unpack("<BBIxx", gf.read(8))

    if not flag & FNAME:
        # Not stored in the header, use the filename sans .gz
        gf.seek(pos)
        fname = gzipfile.name
        if fname.endswith('.gz'):
            fname = fname[:-3]
        return fname, size

    if flag & FEXTRA:
        # Read & discard the extra field, if present
        gf.read(struct.unpack("<H", gf.read(2)))

    # Read a null-terminated string containing the filename
    fname = []
    while True:
        s = gf.read(1)
        if not s or s == '\000':
            break
        fname.append(s)

    gf.seek(pos)
    return ''.join(fname), size
