import os
import shutil
import stat
import traceback
from pathlib import Path

from smartutils.data.base import is_num
from smartutils.error import OK, BaseError
from smartutils.log import logger
from smartutils.system import is_win


def norm_path(path: str) -> str:
    return os.path.normpath(path)


def norm_case_insensitive_path(path: str) -> str:
    path = path.lower()
    return norm_path(path)


def norm_spe(path: str) -> str:
    return path.replace(os.path.sep, "/")


def check_path_exist(path: str) -> bool:
    """
    校验文件是否存在，若filepath是路径且存在，也会返回True
    :param path:
    :return:
    """
    if not os.path.exists(norm_path(path)):
        # logger.error(f"1 check_file_exist no file {path}")
        return False
    return True


def abs_path(path: str) -> str:
    return os.path.abspath(path)


def get_file_path(*paths) -> str:
    """
    获取文件路径，转换成系统统一格式
    :param paths:
    :return:
    """
    _path = []
    for p in paths:
        if is_num(p):
            _path.append(str(p))
            continue
        _path.extend(_split_all_path(p))
    p = os.path.join(*_path)
    return p


def _split_all_path(file_path: str) -> list[str]:
    _path = []
    if is_win():
        driver, file_path = os.path.splitdrive(file_path)
        if driver:
            driver = f"{driver}\\"
    else:
        file_path = file_path.replace("\\\\", "/")
        file_path = file_path.replace("\\", "/")
        if file_path.startswith("/"):
            driver = "/"
        else:
            driver = ""

    head = file_path
    while head != "" and head != "\\" and head != "/":
        head, tail = os.path.split(head)
        _path.append(tail)
    if driver:
        # Linux目录，/c/test，/c不会被识别为driver
        _path.append(driver)
    _path.reverse()
    return _path


def get_path_parent(path: str) -> str:
    """
    获取路径的父路径，如d:/a/b/c/d，返回d:/a/b/c
    :param path:
    :return:
    """
    return os.path.join(*_split_all_path(path)[:-1])


def get_path_last_part(path) -> str:
    return _split_all_path(path)[-1]


def get_path_back_second_part(path) -> str:
    return _split_all_path(path)[-2]


def make_dirs(path: str) -> BaseError:
    if check_path_exist(path):
        return OK
    path = norm_path(path)
    os.makedirs(path)
    os.chmod(path, stat.S_IRWXO)
    return OK


def _remove_readonly(func, path, _):
    """
    Clear the readonly bit and reattempt the removal
    :param func:
    :param path:
    :param _:
    :return:
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rm_dirs(path: str) -> BaseError:
    if not check_path_exist(path):
        return OK
    # logger.debug(f"===============rm_dirs {path}")
    path = get_file_path(path)
    try:
        shutil.rmtree(path, onerror=_remove_readonly)
    except Exception:  # noqa
        logger.error(f"rm_dirs {path} err={traceback.format_exc()}")
    return OK


def path_to_url(filepath: str) -> str:
    p = Path(filepath)
    return p.as_uri()
