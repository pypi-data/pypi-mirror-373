import builtins
import importlib
import importlib.util
import inspect
import os
import pkgutil
import types
from contextlib import contextmanager

__all__ = [
    "call_hook",
    "register_package",
    "exit_on_fail",
    "installed",
]


async def call_hook(hook, *args, **kwargs):
    if hook is None:
        return

    result = hook(*args, **kwargs)
    if inspect.isawaitable(result):
        await result
    return result


def register_package(package: types.ModuleType):
    """
    自动递归扫描并import package下所有模块（包括子包），从而触发注册。
    """
    for finder, modname, ispkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        # try:
        importlib.import_module(modname)
        # except ImportError as e:
        # logger.debug("register_package fail: {e}", e=e)


def installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def exit_on_fail():
    # 非0，k8s判定启动失败；应用在 lifespan 阶段（即启动/关闭事件）报错，uvicorn 退出码是 3
    os._exit(1)  # noqa


@contextmanager
def mock_dbcli(mocker, patch_target):
    """
    通用patch Manager依赖db client的上下文管理器。
    用法：
        with mock_dbcli(mocker, ...) as (MockDBCli, fake_session, instance):
            # ...测试体...
    """
    MockDBCli = mocker.patch(patch_target)
    fake_session = mocker.AsyncMock()
    fake_session.commit = mocker.AsyncMock()
    fake_session.rollback = mocker.AsyncMock()
    fake_session.in_transaction = mocker.MagicMock(return_value=True)

    async_context_mgr = mocker.AsyncMock()
    async_context_mgr.__aenter__.return_value = (fake_session, None)
    async_context_mgr.__aexit__.return_value = None

    instance = MockDBCli.return_value
    instance.db.return_value = async_context_mgr
    instance.close = mocker.AsyncMock()

    yield MockDBCli, fake_session, instance


def recursive_reload(mod):
    """
    递归 reload 祖先，从叶子到父包，能让父包的 from ... import ... 重新绑定到“最新实例”。
    :param mod: 目标module对象
    """
    if not hasattr(mod, "__name__"):
        raise ValueError(f"{mod} is not a module")
    names = mod.__name__.split(".")
    mods = []
    # build modules from top到叶子
    for i in range(1, len(names) + 1):
        part = ".".join(names[:i])
        mods.append(importlib.import_module(part))
    # 从叶子到顶依次 reload
    for m in reversed(mods):
        importlib.reload(m)


def mock_module_absent(mocker):
    """
    让 import 指定模块时真正触发 ImportError，而不是 sys.modules[name] = None
    """

    def _mock(*module_names, mod):
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name in module_names:
                raise ImportError(f"No module named '{name}'")
            return real_import(name, *args, **kwargs)

        mocker.patch("builtins.__import__", side_effect=fake_import)
        mocker.patch(
            "importlib.util.find_spec",
            side_effect=lambda name, *a, **kw: (
                None
                if name in module_names
                else importlib.util.find_spec(name, *a, **kw)
            ),
        )
        if mod:
            # 若不递归reload，顶包中A和叶子中A id不同，单例中存叶子A，外部用顶包A，会走__init__逻辑，导致失败
            recursive_reload(mod)

    return _mock
