import os
import sys

from smartutils.file._path import norm_path, check_path_exist, get_file_path


def file_name(filepath: str) -> str:
    return os.path.basename(filepath)


def check_file_exist(path: str) -> bool:
    """
    校验文件存在且是文件，而不仅仅是路径
    :param path:
    :return:
    """
    return check_path_exist(path) and _path_format_is_file(path)


def _path_format_is_file(path: str) -> bool:
    return is_really_file(path) or "." in path


def filename_base_ext(filename: str) -> tuple[str, str]:
    filename = file_name(filename)
    root, ext = os.path.splitext(filename)
    ext = ext[1:]
    return root, ext


def filename_other_format(filename: str, _format: str) -> str:
    root, ext = filename_base_ext(filename)
    if not _format:
        return root
    return f"{root}.{_format}"


def filename_add_num(filename: str, num: int) -> str:
    root, ext = filename_base_ext(filename)
    name = f"{root}{num}"
    if ext:
        name = f"{name}.{ext}"
    return name


def is_remote_path(path):
    """判断一个路径是不是远程路径，以"\\"开头，注意："\\\\127.0.0.1\\xxx" 也会认为是远程路径。"""
    path = norm_path(path)
    return path.startswith(r"\\")


def my_listdir(path: str, list_name: list):  # 传入存储的list
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            my_listdir(file_path, list_name)
        else:
            list_name.append(file_path)


def deep_list_dir_files(path) -> list[str]:
    fs = []
    my_listdir(path, fs)
    return fs


def paths_in_path(path: str) -> set[str]:
    return {p for p in os.listdir(path) if os.path.isdir(get_file_path(path, p))}


dirs_in_dir = paths_in_path


def full_paths_in_path(path: str) -> set[str]:
    result = set()
    for p in full_all_fs_in_dir(path):
        if os.path.isdir(p):
            result.add(p)
    return result


def full_all_fs_in_dir(path: str) -> set[str]:
    result = set()
    for p in os.listdir(path):
        _p = get_file_path(path, p)
        result.add(_p)
    return result


def all_fs_in_dir(path: str) -> set[str]:
    return set(os.listdir(path))


def is_link(filepath: str) -> bool:
    return os.path.islink(filepath)


def link_target(filepath: str) -> str:
    return os.path.realpath(filepath)


def is_really_file(filepath: str) -> bool:
    return os.path.isfile(filepath) and not is_link(filepath)


def filepath_in_dir(path: str) -> set[str]:
    result = set()
    for p in os.listdir(path):
        _p = get_file_path(path, p)
        if is_really_file(_p):
            result.add(_p)
    return result


def filename_in_dir(path: str) -> set[str]:
    """
    获取指定路径中的文件名，不包括路径
    :param path:
    :return:
    """
    result = set()
    for p in os.listdir(path):
        _p = get_file_path(path, p)
        if is_really_file(_p):
            result.add(p)
    return result


def buff_size() -> int:
    return 65536


def get_name_with_i(name, i):
    if i == 0:
        return name
    return filename_add_num(name, i)


def format_file_name(name: str, version: int = sys.maxsize) -> str:
    """
    规范化文件名中，一些会导致显示异常的字符
    :param name:
    :param version: 1原样 2替换|/\\
    :return:
    """
    if version == 1:
        return name

    name = name.replace("|", "_").replace("/", "").replace("\\", "")
    if version <= 2:
        return name

    # 版本3除了下面替换，还有最后的去空格和_
    if version >= 3:
        name = name.replace("\n", " ").replace("\r\n", " ")
        # -不能换成_
        name = (
            name.replace("……", "_")
            .replace('"', "_")
            .replace("'", "_")
            .replace("！", " ")
            .replace("!", " ")
            .replace(",", " ")
            .replace(".", " ")
            .replace("，", " ")
            .replace("。", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace("【", " ")
            .replace("】", " ")
        )

    if version >= 4:
        name = (
            name.replace("(", " ")
            .replace(")", " ")
            .replace("~", " ")
            .replace("&", " ")
            .replace("$", " ")
            .replace("=", " ")
        )

    if version >= 5:
        name = (
            name.replace(":", " ")
            .replace("*", " ")
            .replace("?", " ")
            .replace("<", " ")
            .replace(">", " ")
        )

    name = name.strip()
    name = " ".join(name.split())
    name = name.replace(" ", "_")
    return name


linux_illegal = ("/", "\\", "?", "%", "*", ":", "|", '"', "<", ">", ".", " ")
windows_illegal = ("<", ">", ":", '"', "/", "\\", "|", "?", "*")


def sanitize_filename(name: str, linux: bool = True, windows: bool = True):
    """
    格式化文件名非法字符
    :param name:
    :param linux:
    :param windows:
    :return:
    """
    replace_char = "_"
    if linux:
        for char in linux_illegal:
            name = name.replace(char, replace_char)
    if windows:
        for char in windows_illegal:
            name = name.replace(char, replace_char)
        name = name.rstrip(". ")

    return name
