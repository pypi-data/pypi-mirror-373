import platform

__all__ = ["is_win", "is_linux", "fix_win_focus"]


def is_win() -> bool:  # pragma: no cover
    """
    是否运行在windows下
    :return:
    """
    return platform.system().lower() == "windows"


def is_linux() -> bool:  # pragma: no cover
    """
    是否运行在linux下
    :return:
    """
    return platform.system().lower() == "linux"


def fix_win_focus():  # pragma: no cover
    """
    防止鼠标误触导致阻塞，但也会导致不响应ctrl+c
    :return:
    """
    print("patch windows console")
    import ctypes

    kernel32 = ctypes.windll.kernel32  # type: ignore
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)
