import os
import hashlib


class File:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path
        self.hashid = sha_hash(path)

    def __repr__(self):
        return self.name


def sha_hash(path):
    with open(path, 'rb') as f:
        content = f.read()
    return hashlib.sha1(content).hexdigest()


def all_file_paths(directory):
    for dir_path, sub_dirs, files in os.walk(directory):
        for f in files:
            yield os.path.join(dir_path, f)


def all_files(directory):
    return [File(fp) for fp in all_file_paths(directory)]


def find_match(item, container, key=lambda i: i):
    for i in container:
        if item == key(i):
            return i
    return None


#    All Cases                  Name Match    Content Match    Default Merge Action
# 1. identical                  Y             Y                delete
# 2. new                        N             N                move
# 3. name divergence            N             Y                delete
# 4. name clash                 Y             N                rename and move


identical = []
new = []
divergence = []
clash = []


def categorize(name_match, hashid_match, file):
    def append_to_identical():
        identical.append((name_match, file))

    def append_to_clash():
        clash.append((name_match, file))

    def append_to_divergence():
        divergence.append((hashid_match, file))

    def append_to_new():
        new.append(file)

    def append_to_both():
        append_to_clash()
        append_to_divergence()

    category_select_dict = {
        True: {
            True:
            append_to_identical
            if name_match == hashid_match
            else append_to_both,

            False: append_to_clash
        },
        False: {
            True: append_to_divergence,
            False: append_to_new
        }
    }
    category_select_dict[bool(name_match)][bool(hashid_match)]()


def melt(dir_host, dir_guest):
    host_files = all_files(dir_host)
    guest_files = all_files(dir_guest)
    for f in guest_files:
        melt_guest_file(f, host_files)


def melt_guest_file(file, host_files):
    hashid_match = find_match(file.hashid, host_files, lambda f: f.hashid)
    name_match = find_match(file.name, host_files, lambda f: f.name)
    categorize(name_match, hashid_match, file)


def print_report():
    print('identical:')
    for f1, f2 in identical:
        print(f1, f2)
    print('new:')
    for f in new:
        print(f)
    print('divergence:')
    for f1, f2 in divergence:
        print(f1, f2)
    print('clash:')
    for f1, f2 in clash:
        print(f1, f2)


dir_2 = r"tests\lib1"
dir_1 = r"tests\lib2"

melt(dir_1, dir_2)
print_report()
