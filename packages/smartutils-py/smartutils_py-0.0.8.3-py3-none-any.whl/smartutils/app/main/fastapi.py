from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Generic, Optional, TypeVar

from pydantic import BaseModel

from smartutils.app.const import RunEnv
from smartutils.error.base import BaseData, BaseError
from smartutils.error.sys import LibraryUsageError

try:
    from fastapi import APIRouter, FastAPI, Request
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import APIRouter, FastAPI, Request


__all__ = ["create_app", "ResponseModel"]

T = TypeVar("T")


class ResponseModel(BaseModel, BaseData, Generic[T]):
    code: int = 0
    msg: str = "success"
    status_code: int = 200
    detail: str = ""
    data: Optional[T] = None

    @classmethod
    def from_error(cls, error: BaseError) -> "ResponseModel":
        return ResponseModel(**error.as_dict)


def _check_app_routes(app):
    unique_routes = set()
    duplicates = []
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", set())
        # 只检查常见REST方法
        if not path or not methods:
            continue
        for m in methods:
            key = (path, m.upper())
            if key in unique_routes:
                duplicates.append(key)
            else:
                unique_routes.add(key)
    if duplicates:
        import warnings

        msg = f"Duplicate route detected: {duplicates}"
        warnings.warn(msg)
        raise LibraryUsageError(msg)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    init(app.state.smartutils_conf_path)

    from smartutils.config import Config
    from smartutils.error.base import BaseError
    from smartutils.log import logger

    conf = Config.get_config()

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description
    app.debug = conf.in_debug
    BaseError.set_debug(conf.in_debug)
    logger.info("!!!======run in {}======!!!", "dev" if conf.in_debug else "prod")
    if not conf.in_debug:
        app.docs_url = None

    from smartutils.app.hook import AppHook

    await AppHook.call_startup(app)
    _check_app_routes(app)

    yield

    logger.info("shutdown start close")
    from smartutils.init import release

    await release()

    await AppHook.call_shutdown(app)

    logger.info("shutdown all closed")


def create_app(_conf_path="config.yaml"):
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException

    from smartutils.app.adapter.json_resp._fastapi import STJsonResponse
    from smartutils.app.adapter.middleware.manager import MiddlewareManager
    from smartutils.app.const import AppKey
    from smartutils.app.factory import ExcJsonResp
    from smartutils.init import init

    RunEnv.set_app(AppKey.FASTAPI)

    app = FastAPI(lifespan=lifespan, default_response_class=STJsonResponse)

    conf_path = RunEnv.get_conf_path(_conf_path)
    app.state.smartutils_conf_path = conf_path

    # TODO: 初始化一次，这里是为了middleware初始化能读取配置
    init(conf_path)
    MiddlewareManager().init_app(app)

    @app.exception_handler(RequestValidationError)
    async def _(request: Request, exc: RequestValidationError):
        return ExcJsonResp().handle(exc).response

    @app.exception_handler(HTTPException)
    async def _(request: Request, exc: HTTPException):
        return ExcJsonResp().handle(exc).response

    router = APIRouter(route_class=MiddlewareManager().init_default_route())

    @router.get("/")
    def root() -> ResponseModel:
        return ResponseModel()

    @router.get("/healthy")
    def healthy() -> ResponseModel:
        return ResponseModel()

    app.include_router(router)

    return app
