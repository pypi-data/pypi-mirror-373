import glob
import os
import shutil
from distutils.dir_util import copy_tree


def is_exist(path):
    return os.path.exists(path)


def is_directory(path):
    return os.path.isdir(path)


def get_current_dir():
    return os.getcwd()


def change_current_dir(new_dir):
    if is_directory(new_dir):
        os.chdir(new_dir)


def get_dir_name(directory):
    return os.path.basename(os.path.normpath(directory))


def get_parent_dir(directory, return_full_path=False):
    if not return_full_path:
        return os.path.basename(os.path.dirname(directory))
    else:
        return os.path.dirname(directory)


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def copy_dir(src_dir, dst_dir, dirs_exist_ok=True, ignore_patterns=None):
    shutil.copytree(
        src_dir, dst_dir, dirs_exist_ok=dirs_exist_ok, ignore=ignore_patterns
    )


def delete_dir(directory):
    shutil.rmtree(directory)


def list_dirs(directory):
    folders = list(
        filter(
            lambda x: os.path.isdir(os.path.join(directory, x)), os.listdir(directory)
        )
    )
    return folders


def list_files(directory):
    files = list(
        filter(
            lambda x: os.path.isfile(os.path.join(directory, x)), os.listdir(directory)
        )
    )
    return files


def filter_files_by_extension(directory, ext, recursive=True):
    if is_directory(directory):
        result_files = []
        if isinstance(ext, list):
            ext_list = ext
        else:
            ext_list = [ext]
        if not recursive:
            filter_pattern = f"{directory}/*"
        else:
            filter_pattern = f"{directory}/**/*"

        for ext_item in ext_list:
            ext_filter = f"{filter_pattern}.{ext_item}"
            files = glob.glob(filter_pattern, recursive=True)
            files = [f for f in files if is_file(f) and f.endswith(ext_item)]
            result_files.extend(files)
        return result_files
    else:
        raise OSError("Directory not exists")


def is_file(path):
    return os.path.isfile(path)


def get_file_name(file_path, split_file_ext=False):
    if is_file(file_path):
        if split_file_ext:
            filename, file_extension = os.path.splitext(os.path.basename(file_path))
            return filename, file_extension
        else:
            return os.path.basename(file_path)
    else:
        raise OSError("Not a file")


def get_absolute_path(file_path):
    return os.path.abspath(file_path)


# dest can be a directory
def copy_file(source, dest):
    shutil.copy2(source, dest)


def delete_file(path):
    if is_file(path):
        os.remove(path)


def rename_dir_or_file(old, new):
    os.renames(old, new)


def move_dir_or_file(source, destination):
    shutil.move(source, destination)
