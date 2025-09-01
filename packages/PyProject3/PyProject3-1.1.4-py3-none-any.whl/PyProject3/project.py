#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/11/17 19:16
# @Author  : 江斌
# @Software: PyCharm
import os
import shutil
import PyProject3.contents as contents
from PyProject3.utils import CUR_DIR, create_dir, create_file
from PyProject3.TemplateProject.package_template.package_template import create_package_project


class BaseProject(object):
    def __init__(self, name, root_dir=None):
        self.name = name
        self.raw_root_dir = root_dir
        if self.raw_root_dir is None:
            self.root_dir = os.path.join(CUR_DIR, self.name)
        elif self.raw_root_dir == '.':
            self.root_dir = os.path.abspath(
                os.path.join(self.raw_root_dir, self.name))
        else:
            self.root_dir = os.path.abspath(self.raw_root_dir)

        self.package_dir = os.path.join(self.root_dir, self.name)
        self.tests_dir = os.path.join(self.root_dir, 'tests')
        self.docs_dir = os.path.join(self.root_dir, 'docs')
        self.ignore_file = os.path.join(self.root_dir, '.gitignore')
        self.setup_file = os.path.join(self.root_dir, 'setup.py')
        self.readme_file = os.path.join(self.root_dir, 'README.md')
        self.requirements_file = os.path.join(
            self.root_dir, 'requirements.txt')
        self.package_init_file = os.path.join(self.package_dir, '__init__.py')
        self.logging_utils_file = os.path.join(
            self.package_dir, 'logging_utils.py')
        self.sql_utils_file = os.path.join(self.package_dir, 'sql_utils.py')
        self.install_cmd_file = os.path.join(self.root_dir, 'install.cmd')
        self.manifest_file = os.path.join(self.root_dir, 'MANIFEST.in')

    def copy_dir(self, src_dir_name, dst_dir_name=None, root=None):
        """
        Copy data in directory. if dst_dir is None, use src_dir instead.
        :param src_dir_name:
        :param dst_dir_name: 默认src_dir_name
        :param root: 默认package_dir
        :return:
        """
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        src = os.path.join(cur_dir, 'TemplateProject', src_dir_name)
        dst_name = dst_dir_name if dst_dir_name else src_dir_name
        if root:
            dst = f'{root}/{dst_name}'
        else:
            dst = f'{self.package_dir}/{dst_name}'
        shutil.copytree(src, dst)

    def create(self, override=False):
        create_dir(self.package_dir)
        create_dir(self.docs_dir)
        create_file(self.ignore_file, contents.GITIGNORE_CONTENT)
        create_file(self.setup_file, contents.SETUP_CONTENT.replace(
            '{project_name}', self.name))
        create_file(self.readme_file, contents.README_CONTENT)
        create_file(self.requirements_file, contents.REQUIREMENTS_CONTENT)
        create_file(self.package_init_file, contents.init_content)
        create_file(self.logging_utils_file, contents.LOGGING_UTILS_CONTENT)
        create_file(self.sql_utils_file, contents.SQL_UTILS_CONTENT)
        create_file(self.install_cmd_file, contents.SETUP_INSTALL_CMD)
        create_file(self.manifest_file, contents.MANIFEST_CONTENT)
        self.copy_dir('test_project',
                      dst_dir_name=f'test_{self.name}', root=self.root_dir)
        self.copy_dir('examples', dst_dir_name='examples', root=self.root_dir)
        self.copy_dir('TemplateProject/connections',
                      dst_dir_name='connections', root=self.package_dir)
        self.copy_dir('TemplateProject/threads',
                      dst_dir_name='threads', root=self.package_dir)
        self.copy_dir('TemplateProject/settings',
                      dst_dir_name='settings', root=self.package_dir)
        self.copy_dir('TemplateProject/stores',
                      dst_dir_name='stores', root=self.package_dir)


class PyQtProject(BaseProject):
    def __init__(self, name, root_dir=None):
        super(PyQtProject, self).__init__(name, root_dir=root_dir)

    def create(self, override=False):
        super(PyQtProject, self).create(override=override)
        ui_dir = os.path.join(self.root_dir, 'ui_files')
        ui_file = os.path.join(ui_dir, 'mainWindow.ui')
        ui_icon = os.path.join(ui_dir, 'main.ico')
        app_file = os.path.join(self.root_dir, 'mainApp.py')
        create_file(ui_file, contents.UI_FILE_CONTENT)
        create_file(ui_icon, contents.UI_ICON_CONTENT)
        create_file(app_file, contents.APP_CONTENT.replace(
            "{project_name}", self.name))
        self.copy_dir('TemplateProject/widgets',
                      dst_dir_name='widgets', root=self.package_dir)


class CythonProject(BaseProject):
    def __init__(self, name, root_dir=None):
        super(CythonProject, self).__init__(name, root_dir=root_dir)

    def create(self, override=False):
        super(CythonProject, self).create(override=override)
        create_file(self.setup_file, contents.CYTHON_SETUP_CONTENT)

        hello_pxd = os.path.join(self.package_dir, 'hello.pxd')
        hello_pyx = os.path.join(self.package_dir, 'hello.pyx')
        world_pyx = os.path.join(self.package_dir, 'world.pyx')
        test_file = os.path.join(self.tests_dir, 'test_cython.py')
        create_file(test_file, contents.CYTHON_TEST_FILE.replace(
            "{project_name}", self.name))
        create_file(self.setup_file, contents.CYTHON_SETUP_CONTENT.replace(
            '{project_name}', self.name), override=True)
        create_file(hello_pxd, contents.CYTHON_HELLO_PXD)
        create_file(hello_pyx, contents.CYTHON_HELLO_PYX)
        create_file(world_pyx, contents.CYTHON_WORLD_PYX.replace(
            "{project_name}", self.name))


class PackageProject(BaseProject):
    def __init__(self, name, root_dir=None):
        super(PackageProject, self).__init__(name, root_dir=root_dir)

    def create(self, override=False):
        project = create_package_project(project_name=self.name,
                               base_dir=self.raw_root_dir,
                               context={}
                               )
        project.create()
        print(f'project(name={self.name}) created')

