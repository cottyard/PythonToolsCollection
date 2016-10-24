import tar
import gz
import zip
import os
import util

codec_dict = {
    '.zip': zip,
    '.tar': tar,
    '.gz': gz
}


def is_compressed(file_name):
    _, extension = os.path.splitext(file_name)
    return extension in codec_dict


def pack(src_file, dest_file):
    # print 'packing', src_file, 'to', dest_file
    util.make_writable(dest_file)
    find_codec(dest_file).pack(src_file, dest_file)


def unpack(src_file, dest_file):
    # print 'unpacking', src_file, 'to', dest_file
    find_codec(src_file).unpack(src_file, dest_file)


def find_codec(file_name):
    _, extension = os.path.splitext(file_name)
    try:
        return codec_dict[extension]
    except KeyError:
        raise Exception(
            extension + "is an unsupported type of compressed file")
