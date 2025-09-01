# from django.conf import settings
# from django.core.wsgi import get_wsgi_application
# from django.http import JsonResponse, HttpRequest
# from django.urls import path

# from smartutils.app.adapter.middleware.factory import MiddlewareFactory
# from smartutils.app.const import AppKey
# from smartutils.app.plugin.exception import ExceptionPlugin
# from smartutils.app.plugin.header import HeaderPlugin
# from smartutils.app.plugin.log import LogPlugin

# __all__ = ["create_app"]


# def _init_smartutils(conf_path: str):
#     # 初始化 smartutils
#     from smartutils.init import init
#     from smartutils.config import get_config
#     from smartutils.log import logger

#     init(conf_path)  # 同步调用
#     conf = get_config()
#     logger.info(
#         "!!!======run in {env}======!!!", env="prod" if conf.project.debug else "dev"
#     )


# def create_app(conf_path: str = "config/config.yaml"):
#     # 1. 初始化 smartutils
#     _init_smartutils(conf_path)

#     # 2. 注入 smartutils 中间件到 settings.MIDDLEWARE
#     #    插件顺序：ExceptionPlugin/HeaderPlugin/LogPlugin
#     middleware_classes = [
#         lambda get_response: MiddlewareFactory.get(AppKey.DJANGO)(
#             ExceptionPlugin(AppKey.DJANGO)
#         )(get_response),
#         lambda get_response: MiddlewareFactory.get(AppKey.DJANGO)(HeaderPlugin())(
#             get_response
#         ),
#         lambda get_response: MiddlewareFactory.get(AppKey.DJANGO)(LogPlugin())(
#             get_response
#         ),
#     ]

#     # 动态注入到 settings
#     if not hasattr(settings, "MIDDLEWARE"):
#         settings.MIDDLEWARE = []

#     # 插到最前，保证生效优先级
#     for mw in reversed(middleware_classes):
#         settings.MIDDLEWARE.insert(0, mw)

#     # 3. 注册健康检查路由
#     def root_view(request: HttpRequest):
#         return JsonResponse({"code": 0, "msg": "ok", "data": {}})

#     def healthy_view(request: HttpRequest):
#         return JsonResponse({"code": 0, "msg": "ok", "data": {}})

#     # 动态注册 URL（如果没 urls.py 或希望自动注册健康检查）
#     if not hasattr(settings, "ROOT_URLCONF") or not settings.ROOT_URLCONF:
#         # 动态添加
#         from types import ModuleType

#         urls = ModuleType("smartutils_auto_urls")
#         urls.urlpatterns = [
#             path("", root_view),
#             path("healthy", healthy_view),
#         ]
#         settings.ROOT_URLCONF = "smartutils_auto_urls"
#         import sys

#         sys.modules["smartutils_auto_urls"] = urls
#     else:
#         # 已有 ROOT_URLCONF，建议在主 urls.py 里加健康检查
#         ...

#     # 4. 创建并返回 WSGI app
#     return get_wsgi_application()
