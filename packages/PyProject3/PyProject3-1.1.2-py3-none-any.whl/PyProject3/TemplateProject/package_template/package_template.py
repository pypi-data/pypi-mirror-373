# coding=utf-8
from PyProject3.schema import Project, Dir, File, ContentMiddleware


test_content = """
from demo_project import *


print(f"Hello, demo_project!")

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

    middleware = ContentMiddleware(old='demo_project', new=project_name)

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
                                                    content=test_content,
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
                                                    content='',
                                                    override=True,
                                                    middlewares=[middleware]
                                                    ),
                                           ]),
                                   ],
                                   files=[
                                       File(name='pyproject.toml',
                                            content='test',
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                       File(name='Makefile',
                                            content='test',
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                       File(name='README.md',
                                            content='test',
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                       File(name='.gitignore',
                                            content='test',
                                            override=True,
                                            middlewares=[middleware]
                                            ),
                                   ]),
                      context=context,
                      override=True
                      )
    return project
