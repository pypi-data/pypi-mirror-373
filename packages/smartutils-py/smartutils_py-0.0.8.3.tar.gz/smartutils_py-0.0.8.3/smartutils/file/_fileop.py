import contextlib
import glob
import hashlib
import os
import shutil
import tempfile
from subprocess import call
from typing import BinaryIO, Callable, Dict, Optional

import yaml

from smartutils.error import OK, BaseError
from smartutils.error.sys import FileError, FileInvalidError, NoFileError
from smartutils.file._filename import (
    _path_format_is_file,
    buff_size,
    check_file_exist,
    filepath_in_dir,
    get_file_path,
    is_link,
)
from smartutils.file._path import check_path_exist, get_path_last_part, norm_path
from smartutils.log import logger
from smartutils.system import is_win

_TextChars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
TMP_PREFIX = "ds_utils_download_"


def load_f_line(filename: str) -> tuple[list[str], BaseError]:
    if not check_file_exist(filename):
        return [], NoFileError()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [item.strip() for item in f.readlines()], OK
    except UnicodeDecodeError as e:
        logger.error(f"load f line {filename} err={e}")
        return [], FileInvalidError()


def dump_f(filename: str, s: str) -> BaseError:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(s)
    return OK


def dump_b_f(filename: str, b: bytes) -> BaseError:
    with open(filename, "wb") as f:
        f.write(b)
    return OK


def dump_f_lines(filename: str, _lines: list) -> BaseError:
    lines = []
    for line in _lines:
        if not isinstance(line, str):
            line = str(line)
        line = f"{line.strip()}\n"
        lines.append(line)
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return OK


def append_f_line(filename: str, line: str, line_break: bool = True) -> BaseError:
    line = line.strip()
    if line_break:
        line = f"{line}\n"
    with open(filename, "a+", encoding="utf-8") as f:
        f.write(line)
    return OK


def append_f_lines(filename: str, lines: list[str]) -> BaseError:
    lines = [
        f"{line.strip() if isinstance(line, str) else str(line)}\n" for line in lines
    ]
    with open(filename, "a+", encoding="utf-8") as f:
        f.writelines(lines)
    return OK


def copy_param_files(source_path, target_path):
    names = os.listdir(source_path)
    for name in names:
        srcname = os.path.join(source_path, name)
        dstname = os.path.join(target_path, name)
        if os.path.isdir(srcname):
            if os.path.exists(dstname):
                continue
            else:
                shutil.copytree(srcname, dstname)
        else:
            # file
            shutil.copy(srcname, dstname)


def copy_file(source: str, dest: str) -> tuple[str, BaseError]:
    source = norm_path(source)
    dest = norm_path(dest)
    if not _path_format_is_file(dest):
        dest = get_file_path(dest, get_path_last_part(source))
    if check_file_exist(dest):
        return dest, NoFileError()
    try:
        shutil.copyfile(source, dest)
    except IOError as e:
        logger.error(f"!!!!copy_file err={e}")
        return dest, FileError()
    return dest, OK


def rename_f(source: str, dest: str) -> BaseError:
    if not check_path_exist(source):
        return OK
    os.rename(source, dest)
    return OK


def _move(src, dst):
    try:
        shutil.move(src, dst)
    except OSError as e:
        if e.errno == 18:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
                shutil.rmtree(src)
            else:
                shutil.copy2(src, dst)
                os.remove(src)
        else:
            raise


def move_file(source: str, dest: str) -> BaseError:
    if not _path_format_is_file(dest):
        dest = get_file_path(dest, get_path_last_part(source))
        logger.debug(f"move_file {dest} actually")
    _move(source, dest)
    return OK


def move_dir(source: str, dest: str) -> BaseError:
    if not check_path_exist(source):
        logger.error(f"move dir no {source}, do nothing")
    else:
        _move(source, dest)
    return OK


def move_file_in_dir(source: str, dest: str) -> BaseError:
    for filepath in filepath_in_dir(source):
        move_file(filepath, dest)
    return OK


def rm_file(filename: str) -> BaseError:
    filename = get_file_path(filename)
    if not check_file_exist(filename):
        return OK
    os.remove(filename)
    return OK


def rm_link(filename: str) -> BaseError:
    if not is_link(filename):
        logger.error(f"rm link {filename} not link")
        return NoFileError()
    os.unlink(filename)
    return OK


def copy_dir(src, dest, override=False):
    src = norm_path(src)
    dest = norm_path(dest)

    count = 0
    if not check_path_exist(dest):
        os.mkdir(dest)
    items = glob.glob(get_file_path(src, "*"))
    for item in items:
        if os.path.isdir(item):
            path = get_file_path(dest, get_path_last_part(item))
            count += copy_dir(src=item, dest=path, override=override)
        else:
            file = os.path.join(dest, get_path_last_part(item))
            if not check_file_exist(file) or override:
                shutil.copyfile(item, file)
                count += 1
    return count


def link(src_path: str, link_path: str) -> BaseError:
    if is_link(link_path):
        # target是链接，删除再链接
        rm_link(link_path)

    no_src = not check_path_exist(src_path)
    if no_src or check_path_exist(link_path):
        logger.debug(f"link do nothing {no_src} {check_path_exist(link_path)}")
        return OK

    if not is_win():
        os.symlink(src_path, link_path)
        return OK

    call(["mklink", "/J", link_path, src_path], shell=True)
    return OK


def read_file_iter(filename: str):
    if not check_file_exist(filename):
        yield
        return
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(buff_size())
            if not chunk:
                break
            yield chunk


def load_f(filename: str) -> tuple[str, BaseError]:
    if not check_file_exist(filename):
        return "", NoFileError()
    with open(filename, "r", encoding="utf-8") as f:
        return f.read(), OK


def is_binary_f(filepath: str) -> bool:
    if not check_file_exist(filepath):
        return False
    with open(filepath, "rb") as f:
        b = f.read(1024)
    return bool(b.translate(None, _TextChars))


def is_binary_f2(filepath: str) -> bool:
    if not check_file_exist(filepath):
        return False
    try:
        with open(filepath, "r") as f:
            f.read(1024)
            return True
    except UnicodeDecodeError:
        return False


def sha2_io(f: BinaryIO) -> str:
    """
    计算内存中内容的sha256
    :param f:
    :return:
    """
    f.seek(0)
    sha2 = hashlib.sha256()
    buf_size = 65536
    while True:
        data = f.read(buf_size)
        if not data:
            break
        sha2.update(data)
    return sha2.hexdigest()


def sha2_file(filepath: str) -> str:
    """
    计算文件的sha256
    :param filepath:
    :return:
    """
    if not check_file_exist(filepath):
        return ""
    with open(filepath, "rb") as f:
        return sha2_io(f)


def cmp_file(f1: str, f2: str) -> bool:
    st1 = os.stat(f1)
    st2 = os.stat(f2)
    # 比较文件大小
    if st1.st_size != st2.st_size:
        return False
    size = 8 * 1024
    with open(f1, "rb") as fp1, open(f2, "rb") as fp2:
        while True:
            b1 = fp1.read(size)  # 读取指定大小的数据进行比较
            b2 = fp2.read(size)
            if b1 != b2:
                return False
            if not b1:
                return True


def get_f_time(filepath: str) -> tuple[float, float]:
    """
    :param filepath:
    :return: 文件创建时间，文件修改时间
    """
    s = os.stat(filepath)
    return s.st_ctime, s.st_mtime


def get_f_last_line(filepath: str) -> str:
    with open(filepath, "rb") as f:
        try:  # catch OSError in case of a one line file
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        return f.readline().decode(encoding="utf-8")


def merge_file(f1: str, f2: str, f2_first=True) -> BaseError:
    """
    合并f2内容到f1，f2内容放在最前面
    """
    if f1 == f2:
        return OK
    if not check_file_exist(f2):
        logger.error(f"merge_file no f2 {f2}")
        return OK
    if not check_file_exist(f1):
        logger.error(f"merge_file no f1 {f1}")
        return NoFileError()

    lines1, _ = load_f_line(f1)
    lines2, _ = load_f_line(f2)

    result = []
    fs = (f2, f1) if f2_first else (f1, f2)
    for f in fs:
        lines, _ = load_f_line(f)
        result.extend(lines)
    dump_f_lines(f1, result)
    return OK


def utils_tmp_dir():
    return os.getenv("UTILS_TMP")


@contextlib.contextmanager
def save_content(
    _dir: str,
    filename: str,
    merge: bool = False,
    file_checker: Optional[Callable] = None,
    ext: Optional[str] = None,
):
    if not file_checker:
        file_checker = lambda x: True  # noqa

    tmp_fd, tmp_f = tempfile.mkstemp(prefix=TMP_PREFIX, suffix=ext, dir=utils_tmp_dir())
    os.close(tmp_fd)
    logger.info(f"save_content {filename} {tmp_f}")

    final_f = get_file_path(_dir, f"{filename}")
    yield tmp_f

    if not check_file_exist(tmp_f):
        logger.info(f"save_content no {tmp_f}, may del for err")
        return

    if not file_checker(tmp_f):
        logger.error(f"save_content check {tmp_f} fail")
        return

    if file_size(tmp_f) == 0:
        logger.info(f"save_content empty {tmp_f}")
        return

    if not check_file_exist(final_f) or not merge:
        move_file(tmp_f, final_f)
    else:
        merge_file(final_f, tmp_f)
        rm_file(tmp_f)
    dump_f(get_file_path(_dir, "__dir.txt"), _dir)


def file_size(filepath: str) -> int:
    return os.path.getsize(filepath)


def load_yaml(filepath: str) -> Dict:
    try:
        with open(filepath) as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, PermissionError, yaml.YAMLError) as e:
        raise FileError(f"yaml file {filepath} load fail")
