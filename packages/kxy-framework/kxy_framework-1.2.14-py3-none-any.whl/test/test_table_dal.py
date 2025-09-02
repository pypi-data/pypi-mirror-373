import re
from typing import Dict,List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Sequence, select, or_
from kxy.framework.friendly_exception import FriendlyException
from kxy.framework.filter import ignore_filter
from test.test_table import TestTable

from kxy.framework.base_dal import BaseDal

class TestTableDal(BaseDal[TestTable]):
    def __init__(self,session:AsyncSession,**kwargs):
        super().__init__(TestTable,session,**kwargs)
        # self.CreateUser_Field = 'CreateUser1'
    
    # 获取列表
    async def Search(self,search:Dict[str,object],page_index, page_size)->tuple[List[TestTable],int]:
        fil = list()
        fil.append(TestTable.IsDelete == 0)
        search_text=search.get('search')
        if search_text:
            if re.search(r"^(\d)*$", search_text):
                fil.append(TestTable.Id == int(search_text))
            #else:
            #    search_text =search_text.strip()
            #    fil.append(TestTable.Name.ilike("%" + search_text + "%"))
            #    fil.append(or_(TestTable.DicType.ilike("%" + search_text + "%"),
            #                  TestTable.Description.ilike("%" + search_text + "%")))
        status = search.get('status')
        if status:
            fil.append(TestTable.Status == int(status))
        items, total_count = await self.paginate_query(fil, TestTable.CreateDate.desc(), page_index, page_size)
        return items, total_count
    async def SearchByUser(self,search:Dict[str,object],page_index:int, page_size:int, need_count=True)->tuple[List[TestTable],int]:
        fil = list()
        fil.append(TestTable.UID == self.UserId)
        fil.append(TestTable.IsDelete == 0)
        search_text=search.get('search')
        if search_text:
            if re.search(r"^(\d)*$", search_text):
                fil.append(TestTable.Id == int(search_text))
            #else:
            #    search_text =search_text.strip()
            #    fil.append(TestTable.Name.ilike("%" + search_text + "%"))
        status = search.get('status')
        if status:
            fil.append(TestTable.Status == int(status))
        total_count = 0
        if need_count:
            total_count = await self.QueryCount(fil)
        items = await self.page_nocount_query(fil, TestTable.CreateDate.desc(), page_index, page_size)
        return items, total_count
    async def AddByJsonData(self, jsonData)->TestTable:
        entity = TestTable()
        entity.InitInsertEntityWithJson(jsonData)    
        entity.Status = 1
        entity.IsDelete = 0
        await self.Insert(entity)
        return entity

    async def AddByJsonDataUser(self, jsonData)->TestTable:
        entity = TestTable()
        entity.InitInsertEntityWithJson(jsonData)
        entity.UID=self.UserId
        entity.Status = 1
        entity.IsDelete = 0
        await self.Insert(entity)
        return entity

    async def UpdateByJsonData(self,jsonData)->TestTable:
        id=jsonData.get('Id',None)
        if id==None:
            raise FriendlyException('更新时必须传回主键')
        entity:TestTable=await self.GetExist(id)
        entity.InitUpdateFiles(jsonData) 
        await self.Update(entity)
        return entity

    async def UpdateByJsonDataUser(self,jsonData)->TestTable:
        '''更新客户自己的数据'''
        id=jsonData.get('Id',None)
        if id==None:
            raise FriendlyException('更新时必须传回主键')
        entity:TestTable=await self.GetExistByUser(id)
        entity.InitUpdateFiles(jsonData) 
        entity.UID = self.UserId
        await self.Update(entity)
        return entity
    
    async def Delete(self,id):
        await self.UpdateFields([TestTable.Id==id],{'IsDelete':1})
    
    async def GetCustomer(self,id):
        return await self.QueryWhere([TestTable.Id==id])
    
    @ignore_filter
    async def GetCustomerNoFilter(self,id):
        return await self.QueryWhere([TestTable.Id==id])

    async def DeleteByUser(self,id):
        await self.UpdateFields([TestTable.Id==id,TestTable.UID==self.UserId],{'IsDelete':1})
