from zipfile import ZipFile
import util


def pack(dir_path, zip_file_path):
    with ZipFile(zip_file_path, 'w') as zf:
        for real_path, path_in_zip_file in util.walk_files(dir_path):
            zf.write(real_path, path_in_zip_file)


def unpack(zip_file_path, dir_path):
    ZipFile(zip_file_path).extractall(dir_path)
