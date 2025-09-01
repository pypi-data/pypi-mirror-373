#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/19 11:06
# @Author  : 江斌
# @Software: PyCharm

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint, Index

Base = declarative_base()


class Firm(Base):  # 定义映射类User，其继承上一步创建的Base
    __tablename__ = 'index_t'
    # 如果有多个类指向同一张表，那么在后边的类需要把extend_existing设为True，表示在已有列基础上进行扩展
    # 或者换句话说，sqlalchemy允许类是表的字集
    # __table_args__ = {'extend_existing': True}
    # 如果表在同一个数据库服务（datebase）的不同数据库中（schema），可使用schema参数进一步指定数据库
    # __table_args__ = {'schema': 'test_database'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)
    is_crawled = Column(Integer)

    def __repr__(self):
        return "<Firm(id=%s)>" % (self.id,)


class User(Base):
    __tablename__ = 'user_t'
    # 如果有多个类指向同一张表，那么在后边的类需要把extend_existing设为True，表示在已有列基础上进行扩展
    # 或者换句话说，sqlalchemy允许类是表的子集
    # __table_args__ = {'extend_existing': True}
    # 如果表在同一个数据库服务（datebase）的不同数据库中（schema），可使用schema参数进一步指定数据库
    # __table_args__ = {'schema': 'test_database'}
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_id_name'),
        # Index('ix_id_name', 'name', 'extra'),  # 索引
        # Index('my_index', my_table.c.data, mysql_length=10) length 索引长度
        # Index('a_b_idx', my_table.c.a, my_table.c.b, mysql_length={'a': 4,'b': 9})
        # Index('my_index', my_table.c.data, mysql_prefix='FULLTEXT') 指定索引前缀
        # Index('my_index', my_table.c.data, mysql_using='hash') 指定索引类型
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    password = Column(String(100))

    def __repr__(self):
        return f"<User(id={self.id} name={self.name})>"
