from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from smartutils.app.const import RunEnv

load_dotenv(dotenv_path=Path("config") / ".env", override=True)

# if os.environ.get("ENABLE_OTEL_AUTO_INSTRUMENT", "1") == "1":
#    from opentelemetry.instrumentation.auto_instrumentation.sitecustomize import initialize
#
#    print("load open telemetry.")
#    initialize()

__all__ = ["run"]


def run():
    import argparse

    from smartutils.app.const import AppKey

    parser = argparse.ArgumentParser(description="Run app/main")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=80, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument(
        "--conf",
        type=str,
        default="config.yaml",
        help="Path to config yaml file",
    )
    parser.add_argument(
        "--app",
        type=str,
        default=AppKey.FASTAPI.value,
        choices=AppKey.list(),
        help=f"App type, choices: {AppKey.list()}",
    )
    args = parser.parse_args()

    RunEnv.set_conf_path(args.conf)
    # TODO: 这里是否需要？后续create_app会自动设置
    RunEnv.set_app(AppKey(args.app))

    uvicorn.run(
        f"smartutils.app.main.{args.app}:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1,
        factory=True,
        access_log=False,
    )
