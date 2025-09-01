# coding=utf-8
from PyProject3.schema import Project, Dir, File, ContentMiddleware

class ContentConstant:
    DEMO_PROJECT_NAME = "demo_project"

    test_content = """
    from demo_project import *


    print(f"Hello, demo_project!")

    """

    MAKEFILE_CONTENT = """
    build:
        python setup.py bdist_wheel

    clean:
        rm -rf build dist *.egg-info

    install:
        python setup.py install


    upload:
        twine upload dist/*

    build_upload:
        make build
        make upload
    """

    README_CONTENT = """
# demo_project

一个用于demo_project的工具，可以读取demo_project的日志文件，并按照时间顺序执行demo_project请求。

## Features


## 安装

```bash
# 本地
pip install demo_project -i https://pypi.org/simple/
# 阿里云
pip install demo_project -i https://pypi.org/simple/
```

## 用法

```bash
python -m demo_project <log_file>
```


### 开发配置

```bash
# 克隆仓库
git clone git@github.com:atanx/demo_project.git
cd demo_project

# 安装开发依赖
pip install -e ".[dev]"

# 手动修改修改__init__.py中的__version__， 然后打包
make build

# 上传到xmov-pypi, 需要安装twine， 配置~/.pypirc
make upload
```

    """

    SETTINGS_JSON_CONTENT = """
    {
        "python.testing.pytestArgs": [
            "demo_project/tests"
        ],
        "python.testing.unittestEnabled": false,
        "python.testing.pytestEnabled": true
    }
    """

    GITIGNORE_CONTENT = """
    # Byte-compiled / optimized / DLL files
    __pycache__/
    *.py[cod]
    *$py.class

    # C extensions
    *.so

    # Distribution / packaging
    .Python
    build/
    develop-eggs/
    dist/
    downloads/
    eggs/
    .eggs/
    lib/
    lib64/
    parts/
    sdist/
    var/
    wheels/
    *.egg-info/
    .installed.cfg
    *.egg
    MANIFEST
    """

    PYPROJECT_TOML_CONTENT = """
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "demo_project"
dynamic = ["version"]
description = "A Python library for demo_project"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "demo_project", email = "07jiangbin@gmail.com"},
]
keywords = ["python", "demo_project"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
requires-python = ">=3.6"
dependencies = [
    "requests",
]

[project.optional-dependencies]
dev = [
    "twine",
    "pip-tools",
    "build",
    "pytest>=6.0",
    "pytest-cov>=2.0",
    "black>=22.0",
    "flake8>=4.0",
    "mypy>=0.900",
]

[project.urls]
Homepage = "https://git.xmov.ai/jiangbin/demo_project"
Repository = "https://git.xmov.ai/jiangbin/demo_project"
Issues = "https://git.xmov.ai/jiangbin/demo_project"

[tool.setuptools.packages.find]
where = ["."]
include = ["demo_project*"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.setuptools.dynamic]
version = {attr = "demo_project.__version__"}
    """

def create_package_project(project_name: str, base_dir: str, context: dict) -> Project:
    """ 创建项目

    Args:
        project_name: 项目名称
        base_dir: 项目所在父级目录
        context: 项目上下文，预留字段 暂时还没使用到该字段内容

    Returns:
        Project 对象
    """

    middleware = ContentMiddleware(old=ContentConstant.DEMO_PROJECT_NAME, new=project_name)

    project = Project(name=project_name,
                      base_dir=base_dir,
                      root_dir=Dir(name=project_name,
                                   dirs=[
                                       Dir(name=project_name,
                                           dirs=[],
                                           files=[
                                               File(name='__init__.py',
                                                    content='',
                                                    override=True,
                                                    middlewares=[middleware]
                                                    ),
                                           ]),
                                       Dir(name='tests',
                                           dirs=[],
                                           files=[
                                               File(name='__init__.py',
                                                    content=ContentConstant.test_content,
                                                    override=True,
                                                    middlewares=[middleware]
                                                    ),
                                           ]),
                                       Dir(name='docs',
                                           dirs=[],
                                           files=[
                                               File(name='__init__.py',
                                                    content='',
                                                    override=True,
                                                    middlewares=[middleware]
                                                    ),
                                           ]),
                                       Dir(name='scripts',
                                           dirs=[],
                                           files=[
                                               File(name='__init__.py',
                                                    content='',
                                                    override=True,
                                                    middlewares=[middleware]
                                                    ),
                                           ]),
                                       Dir(name='.vscode',
                                           dirs=[],
                                           files=[
                                               File(name='settings.json',
                                                    content=ContentConstant.SETTINGS_JSON_CONTENT,
                                                    override=True,
                                                    middlewares=[middleware]
                                                    ),
                                           ]),
                                   ],
                                   files=[
                                       File(name='pyproject.toml',
                                            content=ContentConstant.PYPROJECT_TOML_CONTENT,
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                       File(name='Makefile',
                                            content=ContentConstant.MAKEFILE_CONTENT,
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                       File(name='README.md',
                                            content=ContentConstant.README_CONTENT,
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                       File(name='.gitignore',
                                            content=ContentConstant.GITIGNORE_CONTENT,
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                   ]),
                      context=context,
                      override=True
                      )
    return project
