import os
import zipfile
import time
from pathlib import Path

from .. import B_os
from ..Btqdm import B_Tqdm
from ..Butils import b_validate_params

@b_validate_params({
    "black_dirnames": {"examples": ["__pycache__", ".git", ".idea"]},
    "black_filenames": {"examples": [".gitignore", "README.md"]},
    "black_stems": {"examples": ["README"]},
    "black_exts": {"examples": [".csv", ".npy", ".pt", ".pth"]},
    "white_filepath": {"examples": ["./.gitignore", "./README.md"]},
    "white_dirpath": {"examples": [r"E:\byzh_workingplace\...\文件夹1"]},
})
def b_archive_zip(
    source_path,
    output_path:str|Path=None,
    black_dirnames:list[str]=None,
    black_filenames:list[str]=None,
    black_stems:list[str]=None,
    black_exts:list[str]=None,
    white_filepath:list[str]=None,
    white_dirpath:list[str]=None,
    contain_empty_folder:bool=True,
):
    '''
    压缩文件夹，排除 指定文件夹and指定后缀文件

    name代表前缀, ext代表后缀(包括.)

    :param source_path:
    :param output_path: 如果不传入, 则默认为source_path同名同路径的zip文件
    :param black_dirnames: 黑名单-文件夹名
    :param black_filenames: 黑名单-文件全名
    :param black_stems: 黑名单-文件名(不含后缀)
    :param black_exts: 黑名单-文件后缀(包括.)
    :param white_filepath: 白名单-文件全名
    :param white_dirpath: 白名单-文件夹路径
    :param contain_empty_folder: 是否包含空文件夹
    :return:
    '''
    if output_path is None:
        if os.path.isdir(source_path):
            output_path = source_path + '.zip'
        else:
            output_path = os.path.splitext(source_path)[0] + '.zip'

    if os.path.exists(output_path):
        print(f"检测到{output_path}已存在, 将在3秒后删除...")
        time.sleep(3)
        B_os.rm(output_path)
        print(f"{output_path}已删除")
    def get_lst(lst):
        return [] if lst is None else lst
    black_dirnames = get_lst(black_dirnames)
    black_filenames = get_lst(black_filenames)
    black_stems = get_lst(black_stems)
    black_exts = get_lst(black_exts)
    white_filepath = get_lst(white_filepath)
    white_dirpath = get_lst(white_dirpath)

    my_tqdm = B_Tqdm(prefix='[b_archive_zip]')

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 如果传入的是文件:
        if os.path.isfile(source_path):
            arcname = os.path.basename(source_path)
            zipf.write(source_path, arcname)
            my_tqdm.update(1)
            return

        # 如果传入的是文件夹:
        if os.path.isdir(source_path):
            for root, dirs, files in B_os.walk(source_path,
                                               black_dirnames=black_dirnames,
                                               black_filenames=black_filenames,
                                               black_stems=black_stems,
                                               black_exts=black_exts):

                # 压缩文件:
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path) # 相对于source_path的相对路径
                    zipf.write(file_path, arcname)
                    my_tqdm.update(1)
                # 压缩文件夹:
                for i, dir in enumerate(dirs):
                    if len(os.listdir(os.path.join(root, dir))) == 0:
                        if not contain_empty_folder:
                            dirs.pop(i)
                            continue
                    dir_path = os.path.join(root, dir)
                    arcname = os.path.relpath(dir_path, source_path) # 相对于source_path的相对路径
                    zipf.write(dir_path, arcname)
                    my_tqdm.update(1)

        # 白名单-文件:
        for filepath in white_filepath:
            arcname = os.path.relpath(filepath, source_path)
            zipf.write(filepath, arcname)
            my_tqdm.update(1)

        # 白名单-文件夹:
        for dirpath in white_dirpath:
            for root, dirs, files in B_os.walk(dirpath):
                # 压缩文件:
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path)  # 相对于source_path的相对路径
                    zipf.write(file_path, arcname)
                    my_tqdm.update(1)
                # 压缩文件夹:
                for i, dir in enumerate(dirs):
                    if len(os.listdir(os.path.join(root, dir))) == 0:
                        if not contain_empty_folder:
                            dirs.pop(i)
                            continue
                    dir_path = os.path.join(root, dir)
                    arcname = os.path.relpath(dir_path, source_path)  # 相对于source_path的相对路径
                    zipf.write(dir_path, arcname)
                    my_tqdm.update(1)

if __name__ == '__main__':
    # 不包含空文件夹:`文件夹111`
    B_os.makedirs('根文件夹/文件夹1/文件夹11/文件夹111')
    contain_empty_folder = False

    # 不包含`文件夹12`
    B_os.makefile('根文件夹/文件夹1/文件夹12/file1.txt')
    B_os.makefile('根文件夹/文件夹1/文件夹12/文件夹123/file2.txt')
    B_os.makefile('根文件夹/文件夹1/文件夹12/文件夹1234/文件夹12345/file3.txt')
    black_dirnames = ['文件夹12']

    # 不包含`file4.txt`, 且因此`文件夹21`变为空文件夹, 因此不包含
    B_os.makefile('根文件夹/文件夹2/文件夹21/file4.txt')
    black_filenames = ['file4.txt']

    # 不包含`awa.txt`, `awa.html`
    B_os.makefile('根文件夹/文件夹3/awa.txt')
    B_os.makefile('根文件夹/文件夹3/文件夹31/awa.html')
    black_stems = ['awa']

    # 不包含`file5.csv`
    B_os.makefile('根文件夹/文件夹4/file5.csv')
    black_exts = ['.csv']

    white_filepath = ['根文件夹/文件夹1/文件夹12/文件夹1234/文件夹12345/file3.txt']
    white_dirpath = ['根文件夹/文件夹1/文件夹12/文件夹123']

    b_archive_zip(
        source_path=r'根文件夹',
        output_path=r'awaqwq.zip',
        black_dirnames=black_dirnames,
        black_filenames=black_filenames,
        black_stems=black_stems,
        black_exts=black_exts,
        white_filepath=white_filepath,
        white_dirpath=white_dirpath,
        contain_empty_folder=contain_empty_folder,
    )