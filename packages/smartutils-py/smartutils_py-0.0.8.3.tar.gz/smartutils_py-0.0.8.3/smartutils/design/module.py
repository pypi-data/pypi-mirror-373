from functools import wraps

from smartutils.error.sys import LibraryUsageError


def require_modules(**modules):
    """
    检查传入的多个模块，若有未安装，则抛出 ImportError，信息中包含变量名。
    用法: @require_modules(pyotp=pyotp, xyzlib=xyzlib)
    """

    def decorator(func):
        missing = [name for name, mod in modules.items() if mod is None]
        if not missing:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            raise LibraryUsageError(
                f"Required module(s) not installed: {', '.join(missing)}"
            )

        return wrapper

    return decorator
