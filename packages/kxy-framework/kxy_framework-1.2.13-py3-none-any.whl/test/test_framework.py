import asyncio
import random
import sys
import os

# 正确添加项目根路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from kxy.framework.kxy_logger_filter import QueryCondition
from kxy.framework.http_client import HttpClient
from kxy.framework.context import user_id, user_info, current_tenant_id, dep_id
from datetime import datetime

user_id.set('43')
current_tenant_id.set(1)
dep_id.set(0)
user_info.set({'chineseName':'张三'})

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from test.config import config

engine = create_async_engine(config.mysql_url, pool_size=5,pool_pre_ping=True,pool_recycle=1800, max_overflow=20,echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False,autoflush=False,autocommit=False)

import logging
from kxy.framework.slogger import create_logger,new_trace
from kxy.framework.base_config import BaseConfig
logger,handler = create_logger(logging.DEBUG,'appName','production',filename='log/app',file_type='log',backupCount=5,maxBytes=200,mutiple_process=False)
new_trace()
logger.info('hello world','grpc')
BaseConfig.AppLogger = logger

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
from test.test_table_dal import TestTableDal
from test.test_table import TestTable

async def test_table_add():
    async with AsyncSessionLocal() as session:
        dal = TestTableDal(session)
        for i in range(20,30):
            tab = TestTable()
            tab.user_id=user_id.get()
            tab.UserName = f'张三{i}'
            tab.Sex =1
            tab.ExpiresTime =datetime.now()
            tab.IsDelete = 0
            tab.TenantId = i%3
            tab.DepId=i%3
            await dal.Insert(tab)
async def query():
    async with AsyncSessionLocal() as session:
        dal = TestTableDal(session)
        tab = TestTable()
        tab.user_id=user_id.get()
        tab.UserName = f'张三{random.randint(1,1000)}'
        tab.Sex =1
        tab.ExpiresTime =datetime.now()
        tab.IsDelete = 0
        # tab.TenantId = 1
        tab.DepId=1
        await dal.Insert(tab)
        logger.info(f'插入数据成功,id为{tab.Id}','sql')
        
        exist =await dal.Get(tab.Id)
        assert exist is not None , '查询失败'
        
        result = await dal.ExecSql('select * from test_table')
        items = result.all()
        test_table_objects = [TestTable().init_with_dict(row._asdict()) for row in items]
        
        assert len(test_table_objects) > 0, '自定义查询失败'

        results,total = await dal.Search({},1,30)
        print(total,[res.Id for res in results])

        data = await dal.Get(results[0].Id)
        print(data.toDic())

        # await dal.Delete(data.Id)
        await dal.GetCustomer(data.Id)
        await dal.GetCustomerNoFilter(data.Id)
        total = await dal.DeleteWhere([TestTable.Id==data.Id])
        print(f'删除了{total}条数据')
        assert total == 1,'删除结果不为1'
        
        new_trace()
        response = await HttpClient.get('https://www.baidu.com')
        print(response.text)
        
        result = logger.query(filter=QueryCondition.eq('logCategory', 'http').and_(QueryCondition.lt('duration', 1000)))
        print(result)




loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()
# loop.run_until_complete(test_table_add())
loop.run_until_complete(query())