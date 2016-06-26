from os import listdir, stat , walk
from os.path import isfile, join


def is_valid_file(path):
    file_name = path.split('/')[-1]
    return isfile(path) and not(file_name.startswith('.'))


def get_full_file_structure(folder_name):
    return [f for f in listdir(folder_name) if is_valid_file(join(folder_name, f))]


def get_full_folder_structure(folder_name):
    ret = []
    for root, subfolders, files in walk(folder_name):
        print root , subfolders
        for f in files:
            if f.startswith('.'):
                continue
            # root_modified is root without the sync folder
            root_modified = root.split('/')
            root_modified = "".join(root_modified[1:])
            if len(root_modified):
                file_name = root_modified + '/' + f
            else:
                file_name = f

            ret.append({
                'file_name': file_name,
                'last_modified': stat(root + '/' + f).st_mtime
            })
    return ret

print get_full_folder_structure('db')