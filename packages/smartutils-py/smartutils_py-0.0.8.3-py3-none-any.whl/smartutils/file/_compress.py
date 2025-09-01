import os
import shutil
import zipfile
import zlib
from typing import Optional

from smartutils.error import OK, BaseError
from smartutils.error.sys import FileError, NoFileError
from smartutils.file._filename import check_file_exist
from smartutils.file._path import get_file_path
from smartutils.log import logger

_compress_suffix = {"gz", "tar", "zip", "rar", "tar.gz"}


def is_compress_file(filepath: str) -> bool:
    if "." not in filepath:
        return False
    suffix = filepath.split(".")[-1]
    return suffix in _compress_suffix


def check_zip_file(filepath: str) -> BaseError:
    """
    校验文件是否是完好的zip文件
    :param filepath:
    :return:
    """
    if not check_file_exist(filepath):
        return NoFileError()
    try:
        zip_f = zipfile.ZipFile(filepath)
    except Exception as e:
        logger.error(f"check_zip_file {filepath} get broken zip {e}")
        return FileError()
    else:
        if zip_f.testzip() is not None:
            logger.error(f"check_zip_file {filepath} get broken file")
            return FileError()
    return OK


def extract_compressed(path: str, target_path: Optional[str] = None) -> BaseError:
    """
    解压压缩文件
    :param target_path:
    :param path:
    :return:
    """
    if not target_path:
        target_path = os.path.dirname(path)
    shutil.unpack_archive(path, target_path)
    return OK


def compress(path: str, target_path: Optional[str] = None) -> tuple[str, BaseError]:
    path = get_file_path(path, "")
    if target_path is None:
        target_path = f"{path}"
    shutil.make_archive(target_path, "zip", path)
    return f"{target_path}.zip", OK


def decode_gzip(b: bytes) -> bytes:
    try:
        return zlib.decompress(b, 16 + zlib.MAX_WBITS)
    except zlib.error:
        return b
