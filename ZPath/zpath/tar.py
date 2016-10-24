import tarfile
import util


def pack(dir_path, tar_file_path):
    with tarfile.open(tar_file_path, 'w') as tf:
        for real_path, path_in_tar_file in util.walk_files(dir_path):
            tf.add(real_path, path_in_tar_file)


def unpack(tar_file_path, dir_path):
    tarfile.TarFile(tar_file_path).extractall(dir_path)
