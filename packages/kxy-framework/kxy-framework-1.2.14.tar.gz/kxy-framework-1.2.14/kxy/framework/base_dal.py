# coding=UTF-8

import asyncio
from datetime import datetime
import json
from typing import Dict, List as TypeList,TypeVar, Generic, Union
from sqlalchemy.orm import declarative_base,load_only

from kxy.framework.base_config import BaseConfig
from kxy.framework.base_entity import BaseEntity
from kxy.framework.mapper import Mapper
from .context import user_id,user_info,current_tenant_id,dep_id
from .friendly_exception import FriendlyException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,delete,insert, func,text,event
from sqlalchemy.engine import Engine

from .base_config import BaseConfig

T = TypeVar("T", bound=declarative_base)

filter_dict = {
    '_tenant_field': current_tenant_id,
    '_dep_field': dep_id,
    '_user_field': user_id,
}
@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    BaseConfig.AppLogger.refresh_time()
@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if BaseConfig.AppLogger:
        BaseConfig.AppLogger.info(f'{statement} , parameters: {parameters}','sql')

class BaseDal(Generic[T]):
    _id_field = 'Id'
    _uid_field = 'UID'
    _status_field = 'Status'
    _isDelete_field = 'IsDelete'
    _createUser_field = 'CreateUser'
    _createDate_field = 'CreateDate'
    _lastModifiedUser_Field = 'LastModifiedUser'
    _lastModifiedDate_Field = 'LastModifiedDate'
    def __init__(self,modal:T,session:AsyncSession,**kwargs):
        '''
        UserId：指定用户Id
        UserName：指定用户名
        AutoCommit：是否自动提交事务，默认True
        IgnoreFilter: 忽略过滤字段，比如FilterTenant、FilterDepartment，默认False
        '''
        self.session = session
        self.UserId = kwargs.get('UserId',user_id.get())
        '''操作用户Id'''
        self.UserName = kwargs.get('UserName',user_info.get().get('chineseName',''))
        self.AutoCommit=kwargs.get('AutoCommit',True)
        self.modal = modal
        self.CurrentTenantId = current_tenant_id.get()
        self.IgnoreFilter = kwargs.get('IgnoreFilter',False)
    def _check_extend_field(self, field_name,value):
        if hasattr(self.modal, field_name):
            modal_field_name = getattr(self.modal,field_name)
            if hasattr(self.modal, modal_field_name):
                if value:
                    tenant_filter = getattr(self.modal, modal_field_name)==value
                    return tenant_filter
    # 添加一个方法来自动为查询添加额外过滤
    def _add_extend_filter(self, filters):
        """
        自动为查询条件添加租户过滤
        """
        if self.IgnoreFilter:
            return filters
        filters_copy= list(filters)
        for fieldName,v in filter_dict.items():
            filter = self._check_extend_field(fieldName,v.get())
            if not filter is None:
                filters_copy.append(filter)
        return filters_copy

    async def BeginTransaction(self):
        if not self.session.in_transaction():
            await self.session.begin()
        self.AutoCommit=False
    async def __aenter__(self):
        await self.BeginTransaction()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.Rollback()
        else:
            await self.CommitTransaction()
    async def CommitTransaction(self):
        self.AutoCommit=True
        await self.session.commit()
    async def Rollback(self):
        self.AutoCommit=True
        await self.session.rollback()
    async def Commit(self):
        await self.session.commit()
    async def IfCommit(self):
        if self.AutoCommit:
            await self.session.commit()
        
    async def TryCommit(self, entity):
        try:
            self.session.add(entity)
            await self.IfCommit()
        except Exception as ex:
            await self.session.rollback()
            raise ex
    async def Insert(self, entity):
        setattr(entity,self._createUser_field,self.UserId)
        setattr(entity,self._createDate_field,datetime.now())
        setattr(entity,self._lastModifiedUser_Field,self.UserId)
        setattr(entity,self._lastModifiedDate_Field,datetime.now())

        if hasattr(self.modal, '_tenant_field'):
            tenId = getattr(entity, self.modal._tenant_field)
            if not tenId:
                tenId = current_tenant_id.get()
                if not tenId:
                    raise FriendlyException('添加数据时未指定租户')
                setattr(entity, self.modal._tenant_field, tenId)
        if hasattr(self.modal, '_user_field'):
            userId = getattr(entity, self.modal._user_field)
            if not userId:
                userId = user_id.get()
                if not userId:
                    raise FriendlyException('添加数据时未指用户编号')
                setattr(entity, self.modal._user_field, userId)

        self._AddLogger('新增',entity)
        await self.TryCommit(entity)
    async def BatchInsert(self, entities: TypeList[T]):
        """
        批量插入实体列表，提升插入效率

        Args:
            entities (TypeList[T]): 待插入的实体列表
        """
        for entity in entities:
            setattr(entity,self._createUser_field,self.UserId)
            setattr(entity,self._createDate_field,datetime.now())
            setattr(entity,self._lastModifiedUser_Field,self.UserId)
            setattr(entity,self._lastModifiedDate_Field,datetime.now())
            self.session.add(entity)
        try:
            self._AddLogger('批量新增',entities)
            await self.IfCommit()
        except Exception as ex:
            await self.session.rollback()
            raise FriendlyException(f"批量插入失败: {str(ex)}")
    async def Update(self, entity):
        setattr(entity,self._lastModifiedUser_Field,self.UserId)
        setattr(entity,self._lastModifiedDate_Field,datetime.now())
        self._AddLogger('更新',entity)
        await self.TryCommit(entity)

    async def Delete(self, id):
        entity = await self.Get(id)
        # setattr(entity,self.__status_field,10)
        setattr(entity,self._isDelete_field,1)
        self._AddLogger('逻辑删除',f'删除id为{id}的数据')
        await self.Update(entity)
    async def DeleteWhere(self, fil:TypeList[object]):
        filters = self._add_extend_filter(fil)
        sql = update(self.modal).filter(*filters).values({self._isDelete_field:1})
        self._AddLogger('更新',f'批量逻辑删除：{sql}')
        result = await self.session.execute(sql)
        await self.IfCommit()
        return result.rowcount

    async def TrueDel(self, id):
        self._AddLogger('物理删除',f'删除id为{id}的数据')
        if self.AutoCommit:
            fil = [getattr(self.modal,self._id_field) == str(id)]
            fil = self._add_extend_filter(fil)
            await self.session.execute(delete(self.modal).where(*fil))
            await self.IfCommit()
        else:
            entity =await self.Get(id)
            if entity: await self.session.delete(entity)
    async def TrueDelWhere(self,fil:TypeList[object]):
        if self.AutoCommit:
            filters = self._add_extend_filter(fil)
            sql = delete(self.modal).where(*filters)
            self._AddLogger('物理删除',f'删除语句为{sql}')
            await self.session.execute(sql)
            await self.IfCommit()
        else:
            entitys =await self.QueryWhere(fil)
            for entity in entitys:
                self._AddLogger('物理删除',f'删除id为{entity.Id}的数据')
                await self.session.delete(entity)
    async def TrueDelBatch(self,ids):
        if len(ids):
            self._AddLogger('物理批量删除',f'id为{ids}')
            if self.AutoCommit:
                fil = [getattr(self.modal,self._id_field).in_(ids)]
                fil = self._add_extend_filter(fil)
                d = delete(self.modal).filter(*fil)
                r = await self.session.execute(d)
                await self.IfCommit()
            else:
                for id in ids:
                    entity = await self.Get(id)
                    if entity: await self.session.delete(entity)

    async def TrueDelNotCommit(self, id):
        entity = await self.Get(id)
        self._AddLogger('物理删除',f'删除id为{id}的数据')
        if entity: await self.session.delete(entity)
    async def paginate_query(self,filters, order_by, page_index, page_size)->tuple[TypeList[T],int]:
        # 计算总记录数
        total_count = await self.QueryCount(filters)
        # 分页查询
        items = await self.page_nocount_query(filters, order_by, page_index, page_size)
        return items, total_count
    async def page_nocount_query(self,filters, order_by, page_index, page_size)->TypeList[T]:
        fil = self._add_extend_filter(filters)
        query = select(self.modal).filter(*fil).order_by(order_by).offset((page_index - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        items = result.scalars().all()
        await self.IfCommit()
        return items
    async def paginate_fields_query(self,fields, filters, order_by, page_index, page_size)->tuple[TypeList[T],int]:
        # 计算总记录数
        total_count = await self.QueryCount(filters)
        # 分页查询
        items = await self.page_fields_nocount_query(fields, filters, order_by, page_index, page_size)
        return items, total_count
    async def page_fields_nocount_query(self,fields, filters, order_by, page_index, page_size)->TypeList[T]:
        fil = self._add_extend_filter(filters)
        sql = select(self.modal).filter(*fil)
        if fields:
            sql = sql.options(load_only(*fields))
        sql = sql.order_by(order_by).offset((page_index - 1) * page_size).limit(page_size)
        result = await self.session.execute(sql)
        items = result.scalars().all()
        await self.IfCommit()
        return items
    
    async def Get(self, id)->T:
        fil =[getattr(self.modal,self._id_field) == str(id)]
        fil = self._add_extend_filter(fil)
        result = await self.session.execute(select(self.modal).filter(*fil).limit(1))
        await self.IfCommit()
        return result.scalar()

    async def GetExist(self, id)->T:
        '''根据id获取数据'''
        exist =await self.Get(id)
        if exist is None:
            raise FriendlyException('不存在' + str(id))
        return exist
    async def GetExistByUser(self, id)->T:
        '''获取id和uid为当前用户数据'''
        exist = await self.session.execute(select(self.modal).filter(getattr(self.modal,self._id_field) == str(id),getattr(self.modal,self._uid_field) == self.UserId).limit(1))
        result = exist.scalar()
        await self.IfCommit()
        if result is None:
            raise FriendlyException('不存在' + str(id))
        return result
    async def GetByUser(self):
        return await self.QueryOne([getattr(self.modal,self._uid_field)==self.UserId])
        
    async def UpdateFields(self,fil:TypeList[object],fields:Dict[str,object],refreshDefault=False):
        """更新部分字段

        Args:
            fil ([]): 查询条件
            fields (Dict[fieldname:value]): {"Status":1}
            refreshDefault (bool): 如果为True则自动更新LastModifiedUser，LastModifiedDate

        Raises:
            ex: _description_
        """
        try:
            if refreshDefault:
                fields['LastModifiedUser'] = self.UserId
                fields['LastModifiedDate'] = datetime.now()
            filters = self._add_extend_filter(fil)
            sql = update(self.modal).filter(*filters).values(**fields)
            self._AddLogger('更新',f'更新语句：{sql},值:{fields}')
            result = await self.session.execute(sql)
            await self.IfCommit()
            return result.rowcount
        except Exception as ex:
            await self.session.rollback()
            raise ex
    async def QueryWhere(self,fil:TypeList[object],fields:TypeList[object]=None,orderBy:Union[TypeList[object], object]=None)->TypeList[T]:
        filters = self._add_extend_filter(fil)
        sql = select(self.modal).filter(*filters)
        if fields:
            sql = sql.options(load_only(*fields))
        if orderBy is not None:
            if not isinstance(orderBy, list):
                sql = sql.order_by(orderBy)
            else:
                sql = sql.order_by(*orderBy)
        result = await self.session.execute(sql)
        await self.IfCommit()
        return result.scalars().all()
    async def QueryOne(self,fil:TypeList[object],fields:TypeList[object]=None,orderBy:Union[TypeList[object], object]=None)->T:
        filters = self._add_extend_filter(fil)
        sql = select(self.modal).filter(*filters)
        if fields:
            sql = sql.options(load_only(*fields))
        if orderBy is not None:
            if not isinstance(orderBy, list):
                sql = sql.order_by(orderBy)
            else:
                sql = sql.order_by(*orderBy)
        result = await self.session.execute(sql.limit(1))
        await self.IfCommit()
        return result.scalar()
    async def QueryCount(self,fil:TypeList[object])->int:
        filters = self._add_extend_filter(fil)
        sql = select(func.count()).select_from(self.modal).filter(*filters)
        result = await self.session.execute(sql)
        await self.IfCommit()
        return result.scalar()
    async def _addLoggerAsync(self,action,data:Union[TypeList[T],T]):
        try:
            syslogger = Mapper.getservice('BatchSysLogService')
            if not syslogger:
                raise FriendlyException('开启了业务日志，但是未注册服务BatchSysLogService')
            logData=''
            if isinstance(data,list):
                for item in data:
                    logData += json.dumps(item.to_basic_dict(), ensure_ascii=False)+','
            elif isinstance(data,BaseEntity):
                logData = json.dumps(data.to_basic_dict(), ensure_ascii=False)
            else:
                logData = data
            await syslogger.AddLogAsync(self.modal.__tablename__, action, logData)
        except Exception as ex:
            print(f'添加日志失败{ex}')
        
    def _AddLogger(self, action, data:Union[TypeList[T],T,str]):
        if BaseConfig.BussinessLog:
            asyncio.create_task(self._addLoggerAsync(action,data))
    async def ExecSql(self,sql:str):
        '''执行自定义Sql'''
        result = await self.session.execute(text(sql))
        return result
