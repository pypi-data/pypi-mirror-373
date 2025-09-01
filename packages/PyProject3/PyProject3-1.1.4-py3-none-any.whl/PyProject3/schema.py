from dataclasses import dataclass, field
from typing import List
from PyProject3.utils import create_file, create_dir
import os
from typing import Protocol


class ContentMiddlewareProtocol(Protocol):
    def process(self, content: str) -> str:
        pass


class ContentMiddleware(ContentMiddlewareProtocol):
    def __init__(self, old: str, new: str):
        self.old = old
        self.new = new

    def process(self, content: str) -> str:
        new_content = content.replace(self.old, self.new)
        return new_content


@dataclass
class Dir:
    name: str
    dirs: List['Dir'] = field(default_factory=list)
    files: List['File'] = field(default_factory=list)

    def create(self, base_dir: str = '.', override: bool = False):
        p = os.path.join(base_dir, self.name)
        if os.path.exists(p) and not override:
            raise FileExistsError(f"Directory {p} already exists")
            return
        create_dir(p)
        for dir in self.dirs:
            dir.create(p)
        for file in self.files:
            file.create(base_dir=p)


@dataclass
class File:
    name: str
    content: str
    override: bool = False
    middlewares: List['ContentMiddlewareProtocol'] = field(
        default_factory=list)

    @property
    def processed_content(self):
        content = self.content
        for middleware in self.middlewares:
            content = middleware.process(content)
        return content

    @classmethod
    def from_file(cls, file_path: str, override: bool = False, middlewares: List['ContentMiddlewareProtocol'] = None):
        with open(file_path, 'r') as f:
            content = f.read()
        return cls(name=os.path.basename(file_path),
                   content=content,
                   override=override,
                   middlewares=middlewares)

    def create(self, base_dir: str = '.'):
        content = self.processed_content
        create_file(abs_filename=os.path.join(base_dir, self.name),
                    content=content,
                    override=self.override)


@dataclass
class Project:

    # 项目基本信息
    name: str
    # 项目目录结构
    base_dir: str
    root_dir: Dir
    context: dict
    override: bool = True

    # 创建项目
    def create(self):
        self.root_dir.create(self.base_dir, self.override)
