# smartutils

`smartutils` 是一个面向 Python 的通用工具库，集成了配置管理、上下文、ID生成、数据处理、设计模式、文件操作、日志、定时器、异常处理等常用功能，适用于中大型项目的基础设施搭建和快速开发。

## 主要功能模块

- **配置管理**：支持 YAML 配置加载、工厂模式、配置键管理。
- **上下文管理**：基于 contextvars，支持多种上下文变量注册与管理。
- **ID 生成**：支持多种分布式唯一 ID 生成方案。
- **数据处理**：包括类型校验、哈希环、URL、CSV、中文数字等工具。
- **设计模式**：内置单例、工厂、弃用等常用设计模式实现。
- **文件操作**：文件读写、压缩、路径、锁、类型判断等。
- **日志系统**：基于 loguru，支持多级别日志与自定义扩展。
- **定时与计时**：Timer 类和 timeit 装饰器，支持同步/异步计时。
- **异常处理**：业务异常、系统异常、异常映射与工厂。
- **系统工具**：进程管理、平台信息、cgroup 资源管理等。
- **应用层支持**：插件、适配器、请求上下文、FastAPI 响应模型等。

## 安装依赖

项目使用 [Poetry](https://python-poetry.org/) 管理依赖，核心依赖如下：

- Python >= 3.8
- PyYAML
- loguru
- contextvars
- python-dotenv
- orjson

可选依赖（数据库、缓存、Web 框架等）详见 `pyproject.toml`。

安装命令：

```bash
poetry install
```

依赖配置
```
[project]
dependencies = [
    # "smartutils-py[fastapi,mysql,kafka,redis,client-http] @ git+https://github.com/wuruimiao/smartutils.git@main",
    "smartutils-py[fastapi,mysql,kafka,redis,client-http]==0.0.7",
]
```
或
```
[tool.poetry.dependencies]
# smartutils-py = { git = "https://github.com/wuruimiao/smartutils.git", branch = "main", extras = [
#     "fastapi",
#     "mysql",
#     "redis",
#     "auth",
# ] }
smartutils-py = { version = "0.0.7", extras = ["fastapi", "mysql", "redis", "auth"] }
```

## 快速开始

```python
from smartutils.init import init

# 初始化 smartutils，加载配置
await init("config.yaml")

# 使用时间工具
from smartutils import time
now = time.get_now_str()

# 使用定时器
from smartutils import timer

@timer.timeit("任务耗时：")
def my_task():
    # ... 业务逻辑 ...
    pass

my_task()
```

## 测试

项目内置丰富的单元测试，运行如下：

```bash
pytest -s --cov=smartutils --cov-report=html tests tests_real
```

## 贡献

欢迎提交 issue 和 PR，完善文档和功能！
