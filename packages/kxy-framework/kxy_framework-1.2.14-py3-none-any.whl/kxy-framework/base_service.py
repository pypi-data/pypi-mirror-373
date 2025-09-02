from sqlalchemy.ext.asyncio import AsyncSession
from simple_util.slogger import user_id,user_info
class BaseService():
    def __init__(self,session:AsyncSession,**kwargs):
        self.session = session
        self.user_id = kwargs.get('UserId',user_id.get())
        self.user_name = kwargs.get('UserName',user_info.get().get('chineseName',''))