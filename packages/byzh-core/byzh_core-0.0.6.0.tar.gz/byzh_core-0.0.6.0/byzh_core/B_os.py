import shutil
import os
from pathlib import Path

from .Butils import b_validate_params

@b_validate_params({
    "path": __file__
})
def get_parent_dir(path) -> Path:
    '''
    获取 该py文件 所在的文件夹
    :param path: __file__
    '''
    parent_dir = Path(path).parent
    return parent_dir

def get_cwd() -> Path:
    '''
    获取 当前工作目录current working directory
    '''
    return Path.cwd()


def makedirs(path):
    def is_dir(path):
        path = Path(path)

        # 存在
        if os.path.isdir(path):
            return True

        # 不存在
        name = path.name
        if '.' in name:
            return False
        return True

    def is_file(path):
        path = Path(path)

        # 存在
        if os.path.isfile(path):
            return True

        # 不存在
        name = path.name
        if '.' in name:
            return True
        return False

    path = Path(path)

    if is_dir(path):
        os.makedirs(path, exist_ok=True)
    if is_file(path):
        os.makedirs(path.parent, exist_ok=True)

def makefile(path):
    path = Path(path)

    parent_dir = path.parent
    makedirs(parent_dir)

    path.touch() # 创建文件

def rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    if os.path.isfile(path):
        os.remove(path)


def get_dirpaths_in_dir(root_dir_path, exclude_dir=['__pycache__', '.git']):
    result = []
    for root, dirs, files in os.walk(root_dir_path):
        for i, dir in enumerate(dirs):
            if str(dir) in exclude_dir:
                dirs.pop(i)
        path = Path(root)
        result.append(path)

    result = result[1:]

    return result

def get_filepaths_in_dir(root_dir_path, exclude_name=[], exclude_suffix=['.pyc'], exclude_dir=['.git']):
    file_paths = []
    for root, dirs, files in os.walk(root_dir_path):
        for i, dir in enumerate(dirs):
            if str(dir) in exclude_dir:
                dirs.pop(i)
        for file in files:
            file_path = os.path.join(root, file)
            file_path = Path(file_path)
            if file_path.name in exclude_name or file_path.suffix in exclude_suffix:
                continue
            file_paths.append(file_path)
    return file_paths

@b_validate_params({
    "black_dirnames": {"examples": ["__pycache__", ".git"]},
    "black_filenames": {"examples": ["__init__.py", "test.py"]},
    "black_stems": {"examples": ["test", "example"]},
    "black_exts": {"examples": [".pyc"]}
})
def walk(
    root: str,
    black_dirnames: list[str] = None,
    black_filenames: list[str] = None,
    black_stems: list[str] = None,
    black_exts: list[str] = None,
):
    """
    遍历目录, 类似os.walk, 但可以指定黑名单
    :param root:
    :param black_dirnames:
    :param black_stems: 文件名
    :param black_stems: 文件名, 不包括后缀
    :param black_exts: 文件名的后缀(含.)
    :return: root, dirs, files
    """

    def get_lst(lst):
        return [] if lst is None else lst
    black_dirnames = get_lst(black_dirnames)
    black_filenames = get_lst(black_filenames)
    black_stems = get_lst(black_stems)
    black_exts = get_lst(black_exts)

    dirs = []
    files = []
    for entry in os.listdir(root):
        path = os.path.join(root, entry)
        # 是文件夹
        if os.path.isdir(path):
            dirs.append(entry)
        # 是文件
        elif os.path.isfile(path):
            files.append(entry)
        else:
            continue
    dirs = [d for d in dirs if d not in black_dirnames]
    files = [f for f in files if f not in black_filenames]
    files = [f for f in files if os.path.splitext(f)[0] not in black_stems]
    files = [f for f in files if os.path.splitext(f)[1] not in black_exts]

    yield root, dirs, files

    for dirname in dirs:
        new_path = os.path.join(root, dirname)
        yield from walk(new_path, black_dirnames, black_filenames, black_stems, black_exts)

if __name__ == '__main__':
    # print(get_dirpaths_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi'))
    a = get_filepaths_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi')
    print(a)