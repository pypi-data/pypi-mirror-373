#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/12/15 16:18
# @Author  : 江斌
# @Software: PyCharm
import os
import sys

cur = os.path.abspath(os.path.dirname(__file__))
sys.path.append(cur)
from model import Base, User
from sql_helper import SqlHelper


def test_add(self):
    """ 增加记录。"""
    ed_user = User(name='ed', password='as')
    self.session.add(ed_user)  # 将该实例插入到users表
    self.session.add_all(
        [User(name='ed1', password=None),
         User(name='ed2', password='password2'),
         User(name='ed3', password='password3')]
    )
    self.session.commit()  # 当前更改只是在session中，需要使用commit确认更改才会写入数据库


def test_delete(self):
    """ 删除记录。"""
    firm = self.session.query(User).first()
    self.session.delete(firm)
    self.session.commit()


def test_update(self):
    """ 修改记录。 """
    import random
    user = self.session.query(User).first()
    old_name = user.name
    new_name = f"fakename{random.random()}"
    print(f'oldname: {old_name}  new_name: {new_name}')
    self.session.commit()


def test_query(self):
    """ 查询记录。"""
    # item_count = self.session.query(User).filter(User.name.like(f"%{to_unicode_ascii('中学')}%")).count()
    user = self.session.query(User).filter(User.name.isnot(None)).first()
    print(f'first item: {user}')
    item_count = self.session.query(User).count()
    print(f'User count: {item_count}')


def test_helper():
    """

    :return:
    """
    helper = SqlHelper(conn_str=r'data.db')
    helper.create_all_table(Base)
    data = helper.execute("select * from main.sqlite_master;")
    print('-------------data---------')
    print(data)
    print('-------------test_query---------')
    test_query(helper)
    print('-------------test_add---------')
    test_add(helper)


if __name__ == '__main__':
    test_helper()
