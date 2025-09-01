#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/7/29 15:27
# @Author  : 江斌
# @Software: PyCharm
import os
import logging
import configs
import shutil
import time
from F3dWidgets.MyProgressDialog import ProgressDialog


# from path import Path
class Path(object):
    def __init__(self, root):
        self.root = root

    def dirs(self):
        items = []
        for item in os.listdir(self.root):
            p = os.path.join(self.root, item)
            if os.path.isdir(p):
                items.append(item)
        return items

    def exists(self):
        return os.path.exists(self.root)


logger = logging.getLogger(configs.APP_ID)


def is_local(name):
    return name.startswith('[LOCAL]')


def get_actor_list(actor_dir, suffix=""):
    """
    获取所有可用的演员。例如：遍历目录T:\projects\Asset_XMOV\actor下的所有演员子目录。
    如果演员子目录中有face_model文件夹且face_model又包含neutral.obj文件,则该演员视为
    可用演员。
    :param actor_dir: 演员根目录
    :param suffix: 子目录
    :return: 所有可用的演员列表。
    """
    dirs = os.listdir(actor_dir)
    try:
        actors = [""]
        for actor in dirs:
            face_model_dir = os.path.join(actor_dir, actor, suffix)
            obj_file = os.path.join(face_model_dir, "neutral.obj")
            if os.path.isdir(face_model_dir) and os.path.isfile(obj_file):
                actors.append(actor)
    except:
        actors = ["", "chenbailing", "chenruijie", "chenyanyi", "shiyan",
                  "siran", "wuqiuyun", "xiaowen", "xiaoyou",
                  "yexiu", "yuxuan", "zhangyibei", "zhuyijing"]
    return actors


def _get_project_list(project_dir):
    projects = ["", "[LOCAL]"]
    if os.path.isdir(project_dir):
        for item in os.listdir(project_dir):
            full_item = os.path.join(project_dir, item)
            if os.path.isdir(full_item):
                projects.append(item)
                # actor_list = get_actor_list_by_project(full_item)
                # if len(actor_list) > 0:
                #     projects.append(item)
    else:
        logger.warning(f'无法访问文件夹：{project_dir}')
    return projects


def get_project_list(project_dir):
    return _get_project_list(project_dir)


def get_character_list(train_data_root_dir):
    """
    获取角色目录。
    :param train_data_root_dir:
    :return:
    """
    dirs = [""]
    for item in os.listdir(train_data_root_dir):
        full_item = os.path.join(train_data_root_dir, item)
        if os.path.isdir(full_item):
            dirs.append(item)
    return dirs


def get_char_root(project):
    if is_local(project):
        char_root = configs.LOCAL_CHAR_DIR
    else:
        char_root = os.path.join(configs.PROJECT_DIR, project, 'asset', 'char')
    return char_root


def get_actor_list_by_project(project):
    """
    获取指定项目中的演员列表。
    :param project:
    :return:
    """
    char_root = get_char_root(project)
    char_list = get_char_list_by_project(project)

    actor_set = set()
    for char in char_list:
        char_dir = os.path.join(char_root, char, "face_retarget", "train")
        char_dir = Path(char_dir)
        if char_dir.exists():
            for each in char_dir.dirs():
                actor_set.add(each)
    actor_list = list(actor_set)

    return actor_list


def get_actor_by_project_and_char(project_name, char_name):
    char_root = get_char_root(project_name)
    actor_list = []
    char_dir = os.path.join(char_root, char_name, "face_retarget", "train")
    char_dir = Path(char_dir)
    if char_dir.exists():
        for each in char_dir.dirs():
            actor_list.append(each)
    return actor_list


def get_char_list_by_project(project):
    char_root = get_char_root(project)
    char_root = Path(char_root)
    if not char_root.exists():
        return []
    char_list = [each for each in char_root.dirs()]
    return char_list


def get_character_by_project_and_actor(project, actor):
    """
    根据【演员】和【项目】获取【角色列表】。
    :param project: 项目名称
    :param actor: 演员名称
    :return:
    """
    chars = []
    char_root = get_char_root(project)
    if os.path.exists(char_root):
        for item in os.listdir(char_root):
            full_item = os.path.join(char_root, item, 'face_retarget', 'train', actor)
            if os.path.isdir(full_item):
                chars.append(item)
    return chars


# def get_nodegraph_dll_path(p):
#     """
#     获取指定目录中的第一个dll文件。
#     :param p: 指定的目录
#     :return: 目录中的第一个dll文件的完整路径，若找不到返回None
#     """
#     if not os.path.exists(p):
#         return None
#
#     dlls = [item for item in os.listdir(p) if item.lower().endswith(".dll")]
#     if len(dlls) > 0:
#         dll_path = os.path.join(p, dlls[0])
#         dll_path = os.path.abspath(dll_path)
#         return dll_path
#     else:
#         return None

def get_actor_json_file(actor, local=False):
    if local:  # 本地
        actor_json_file = os.path.join(configs.LOCAL_ACTOR_DIR, actor,
                                       f'config_{actor}.json')  # config_{actor}.json文件路径
    else:  # CGT中项目asset_xmov
        actor_json_file = os.path.join(configs.PERFORMER_DATA_DIR, actor,
                                       f'config_{actor}.json')  # config_{actor}.json文件路径
    return actor_json_file


def get_actor_dir(actor, local=False):
    if local:
        actor_data_dir = os.path.join(configs.LOCAL_ACTOR_DIR, actor, "face_model/")  # 演员人脸模型目录
    else:
        actor_data_dir = os.path.join(configs.PERFORMER_DATA_DIR, actor, "face_model/")  # 演员人脸模型目录
    return actor_data_dir


def get_model_file_dir(local=False):
    if local:
        model_file_dir = configs.LOCAL_MODEL_FILE_DIR  # fare 模型目录
    else:
        model_file_dir = configs.MODEL_FILE_DIR  # fare 模型目录
    return model_file_dir


def get_nodegraph_dll(project_name, char_name):
    """
    根据指定的【项目】、【角色】获取所需nodegraph DLL文件完整路径。
        1. LOCAL项目为本地文件夹。
            【LOCAL根】/char/【角色】/【角色】_face.dll
            【LOCAL根】/char/【角色】/【演员】/*.train
            【LOCAL根】/actor/【演员】/*.obj

        2. CGT标准项目
            【CGT根】/【项目】/asset/char/【角色】/face_retarget/nodegraph/【角色】_face.dll

    :param project_name:
    :param char_name:
    :return:
    """
    if is_local(project_name):
        p = fr'{configs.LOCAL_CHAR_DIR}/{char_name}/face_retarget/nodegraph/{char_name}_face.dll'
    else:
        p = fr"{configs.PROJECT_DIR}/{project_name}/asset/char/{char_name}/face_retarget/nodegraph/{char_name}_face.dll"

    return p


def get_train_data_dir(project, char, actor):
    if is_local(project):
        train_data_dir = fr'{configs.LOCAL_CHAR_DIR}/{char}/face_retarget/train/{actor}/'
    else:
        train_data_dir = f'{configs.PROJECT_DIR}/{project}/asset/char/{char}/face_retarget/train/{actor}/'
    return train_data_dir


def get_f3d_config(actor, is_local=False):
    """
    f3dcore 依赖配置生成 【支持本地项目】。
    :param actor:
    :param is_local:
    :return:
    """
    actor_json_file = get_actor_json_file(actor, local=is_local)
    actor_data_dir = get_actor_dir(actor, local=is_local)
    model_file_dir = get_model_file_dir(local=is_local)
    return actor_json_file, actor_data_dir, model_file_dir


def get_retarget_config(project, character, actor):
    """
    根据角色和演员获取对应重定向配置。【支持本地项目】

    :param project: 项目，例如: XNZB_CF
    :param character: 角色，例如: linghu
    :param actor: 演员，例如：wuqiuyun
    :return: dict类型配置, dict类型状态
    """
    train_data_dir = get_train_data_dir(project, character, actor)
    nodegraph_dll = get_nodegraph_dll(project, character)
    config = {
        "train_data_dir": train_data_dir,
        "nodegraph_dll": nodegraph_dll,
        "character": character,
        "engine": "nodegraph",
    }
    exist = dict(train_data_dir=os.path.exists(train_data_dir),
                 nodegraph_dll=os.path.exists(nodegraph_dll))
    return config, exist


def copy_tree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    if os.path.exists(src):
        shutil.copytree(src, dst)
        logger.info(f'copytree. src:{src}, dst:{dst}')
    else:
        logger.info(f'src not exist. src:{src}')


def copy_project_to_local(project, parent_widget=None):
    """
    演员:
    T:\projects\Asset_XMOV\actor\shiyan
    角色:
    T:\projects\KOL_DaJi\asset\char\DaJi\face_retarget\nodegraph
    T:\projects\KOL_DaJi\asset\char\DaJi\face_retarget\train
    T:\projects\KOL_DaJi\asset\char\DaJi\TPose

    :param project:
    :return:
    """
    progress_dlg = ProgressDialog(title="复制到本地项目", label='开始...', parent=parent_widget)

    progress_dlg.set_label_text(f'正在获取项目演员和角色...')
    progress_dlg.set_value(0)

    actor_list = get_actor_list_by_project(project)
    char_list = get_char_list_by_project(project)
    total_idx = len(actor_list) + len(char_list)
    current_idx = 0
    # 1. 复制人脸模型
    for actor in actor_list:
        current_idx = current_idx + 1
        progress_dlg.set_label_text(f'正在复制演员：{actor}')
        progress_dlg.set_value(current_idx / total_idx * 100)

        actor_dir = get_actor_dir(actor)  # face_model目录
        actor_dir = os.path.abspath(os.path.join(actor_dir, '..'))  # 演员目录
        local_actor_dir = get_actor_dir(actor, local=True)
        local_actor_dir = os.path.abspath(os.path.join(local_actor_dir, '..'))
        copy_tree(actor_dir, local_actor_dir)

    # 2. 复制node_graph train_data
    for char in char_list:
        current_idx = current_idx + 1
        progress_dlg.set_label_text(f'正在复制角色：{char}')
        progress_dlg.set_value(current_idx / total_idx * 100)

        root_dir = os.path.dirname(get_nodegraph_dll(project, char))
        root_dir = os.path.abspath(os.path.join(root_dir, '..', '..'))
        nodegraph_dll_dir = os.path.join(root_dir, 'face_retarget', 'nodegraph')
        train_root = os.path.join(root_dir, 'face_retarget', 'train')
        tpose_root = os.path.join(root_dir, 'TPose')
        body_retarget_root = os.path.join(root_dir, 'retarget')
        model_dir = get_model_file_dir(local=False)

        local_root_dir = os.path.dirname(get_nodegraph_dll('[LOCAL]', char))
        local_root_dir = os.path.abspath(os.path.join(local_root_dir, '..', '..'))
        local_nodegraph_dll_dir = os.path.join(local_root_dir, 'face_retarget', 'nodegraph')
        local_train_root = os.path.join(local_root_dir, 'face_retarget', 'train')
        local_tpose_root = os.path.join(local_root_dir, 'TPose')
        local_body_retarget_root = os.path.join(root_dir, 'retarget')
        local_model_dir = get_model_file_dir(local=True)

        copy_tree(nodegraph_dll_dir, local_nodegraph_dll_dir)
        copy_tree(train_root, local_train_root)
        copy_tree(tpose_root, local_tpose_root)
        copy_tree(body_retarget_root, local_body_retarget_root)

        if not os.path.exists(local_model_dir):
            copy_tree(model_dir, local_model_dir)
    # 3. 复制人脸识别模型


def test_get_list():
    actors = get_actor_list(r"T:\projects\Asset_XMOV\actor", suffix='face_model')
    print(actors)
    characters = get_character_list(r"D:\xmov\projects\git.xmov\PyOnlineAnimF3D\f3d_deps_files\train_data")
    print(characters)


def test_copy():
    copy_project_to_local('KOL_Meide')


if __name__ == "__main__":
    test_copy()
