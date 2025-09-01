from typing import TYPE_CHECKING

try:
    import filetype
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    import filetype

"""
extension形如zip
mine形如application/zip
"""

msg = "smartutils.file.type depend on filetype, install before use."


def file_mime(filepath: str) -> str:
    assert filetype, msg
    kind = filetype.guess(filepath)
    if not kind:
        return ""
    return kind.mime


def _first_type(filepath: str) -> str:
    """
    返回image/video类似的大类
    :param filepath:
    :return:
    """
    return file_mime(filepath).split("/")[0]


def file_type(filepath: str) -> str:
    """
    返回png, gif类似的具体类别
    :param filepath:
    :return:
    """
    assert filetype, msg
    kind = filetype.guess(filepath)
    if not kind:
        return ""
    return kind.extension


def is_img(filepath: str) -> bool:
    """
    Image
        dwg - image/vnd.dwg
        xcf - image/x-xcf
        jpg - image/jpeg
        jpx - image/jpx
        png - image/png
        apng - image/apng
        gif - image/gif
        webp - image/webp
        cr2 - image/x-canon-cr2
        tif - image/tiff
        bmp - image/bmp
        jxr - image/vnd.ms-photo
        psd - image/vnd.adobe.photoshop
        ico - image/x-icon
        heic - image/heic
        avif - image/avif
    :param filepath:
    :return:
    """
    return _first_type(filepath) == "image"


def is_video(filepath: str) -> bool:
    """
    Video
        3gp - video/3gpp
        mp4 - video/mp4
        m4v - video/x-m4v
        mkv - video/x-matroska
        webm - video/webm
        mov - video/quicktime
        avi - video/x-msvideo
        wmv - video/x-ms-wmv
        mpg - video/mpeg
        flv - video/x-flv
    :param filepath:
    :return:
    """
    return _first_type(filepath) == "video"


def is_audio(filepath: str) -> bool:
    """
    Audio
        aac - audio/aac
        mid - audio/midi
        mp3 - audio/mpeg
        m4a - audio/mp4
        ogg - audio/ogg
        flac - audio/x-flac
        wav - audio/x-wav
        amr - audio/amr
        aiff - audio/x-aiff
    :param filepath:
    :return:
    """
    return _first_type(filepath) == "audio"


def is_archive(filepath: str) -> bool:
    """
    Archive
        br - application/x-brotli
        rpm - application/x-rpm
        dcm - application/dicom
        epub - application/epub+zip
        zip - application/zip
        tar - application/x-tar
        rar - application/x-rar-compressed
        gz - application/gzip
        bz2 - application/x-bzip2
        7z - application/x-7z-compressed
        xz - application/x-xz
        pdf - application/pdf
        exe - application/x-msdownload
        swf - application/x-shockwave-flash
        rtf - application/rtf
        eot - application/octet-stream
        ps - application/postscript
        sqlite - application/x-sqlite3
        nes - application/x-nintendo-nes-rom
        crx - application/x-google-chrome-extension
        cab - application/vnd.ms-cab-compressed
        deb - application/x-deb
        ar - application/x-unix-archive
        Z - application/x-compress
        lzo - application/x-lzop
        lz - application/x-lzip
        lz4 - application/x-lz4
        zstd - application/zstd
    :param filepath:
    :return:
    """
    return file_type(filepath) in ("zip", "tar", "rar", "gz", "7z")


def is_doc(filepath: str) -> bool:
    """
    Document
        doc - application/msword
        docx - application/vnd.openxmlformats-officedocument.wordprocessingml.document
        odt - application/vnd.oasis.opendocument.text
        xls - application/vnd.ms-excel
        xlsx - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        ods - application/vnd.oasis.opendocument.spreadsheet
        ppt - application/vnd.ms-powerpoint
        pptx - application/vnd.openxmlformats-officedocument.presentationml.presentation
        odp - application/vnd.oasis.opendocument.presentation
    :param filepath:
    :return:
    """
    return False


"""
Font
    woff - application/font-woff
    woff2 - application/font-woff
    ttf - application/font-sfnt
    otf - application/font-sfnt
Application
    wasm - application/wasm
"""
