#!/usr/bin/python
# -*- coding:utf-8 -*-

from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime,BigInteger
from kxy.framework.base_entity import BaseEntity
from sqlalchemy.ext.declarative import declarative_base
from kxy.framework.filter import FilterTenant,FilterDepartment,FilterUser

Modal = declarative_base()

@FilterTenant('TenantId')
@FilterDepartment("DepId")
@FilterUser('user_id')
class TestTable(BaseEntity, Modal):
    def __init__(self):
        super().__init__('int',False)
    __tablename__ = 'test_table'
    
    Id = Column(BigInteger, comment='编号',primary_key=True,autoincrement=True)
    user_id = Column('UID', String(200), comment='用户编号')
    UserName = Column(String(200), comment='用户名')
    Sex = Column(Integer, comment='性别(1-男 2-女)')
    ExpiresTime = Column(DateTime, comment='过期时间')
    Status = Column(Integer, comment='状态(1-生效 10-禁用)')
    IsDelete = Column(Integer, comment='删除')
    CreateUser = Column(String(36), comment='创建用户')
    CreateDate = Column(DateTime, comment='创建时间')
    LastModifiedUser = Column(String(36), comment='最后修改用户')
    LastModifiedDate = Column(DateTime, comment='最后修改时间')
    TenantId = Column(Integer, comment='租户编号')
    DepId = Column(Integer, comment='部门')


    InsertRequireFields = ['Sex', 'ExpiresTime', 'TenantId', 'DepId']

    InsertOtherFields= ['user_id', 'UserName', 'Status']

    def to_basic_dict(self):
        """返回基本信息"""
        resp_dict = {
            'Id': self.Id,
           'UID': self.user_id,
           'UserName': self.UserName,
           'Sex': self.Sex,
           'ExpiresTime': self.ExpiresTime,
           'Status': self.Status,
           'IsDelete': self.IsDelete,
           'CreateUser': self.CreateUser,
           'CreateDate': self.CreateDate.strftime("%Y-%m-%d %H:%M:%S") if self.CreateDate else None,
           'LastModifiedUser': self.LastModifiedUser,
           'LastModifiedDate': self.LastModifiedDate.strftime("%Y-%m-%d %H:%M:%S") if self.LastModifiedDate else None,
           'TenantId': self.TenantId,
           'DepId': self.DepId,

        }
        return resp_dict