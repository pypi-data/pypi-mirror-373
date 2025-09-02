# coding=UTF-8

from .friendly_exception import FriendlyException

from .id_generator import SnowflakeIDGenerator
idgenerator = SnowflakeIDGenerator()
class BaseEntity():

    InsertOtherFields = []
    InsertRequireFields = []
    UpdateFiles = []
    __AutoId__ = True
    def setId(self):
        if self._id_type == 'str':
            self.Id = str(idgenerator.get_next_id())
        else:
            self.Id = idgenerator.get_next_id()
    def __init__(self,id_type='str',auto_id=True):
        '''
        id_type: str or int,指定Id的数据类型
        auto_id: 是否自动生成id
        '''
        self._id_type = id_type
        self.__AutoId__ = auto_id
        if self.__AutoId__:
            self.setId()
    def init_with_dict(self,fields):
        for field,value in fields.items():
            setattr(self, field, value)
        return self

    # 插入字段
    def InitInsertEntityWithJson(self, json_data):
        self.__init_require__(json_data, self.InsertRequireFields)
        self.__init_fileds__(json_data, self.InsertOtherFields)
        if self.__AutoId__ and not self.Id:
            self.setId()

    # 更新字段
    def InitUpdateFiles(self, json_data):
        self.__init_fileds__(json_data, self.UpdateFiles)
        self.__init_fileds__(json_data, self.InsertRequireFields)
        self.__init_fileds__(json_data, self.InsertOtherFields)

    def __init_fileds__(self, json_data, fields):
        for field in fields:
            value = json_data.get(field, None)
            if value is not None:
                setattr(self, field, value)

    def __init_require__(self, json_data, fields):
        for field in fields:
            value = json_data.get(field, None)
            if value is None:
                raise FriendlyException(field+' can not empty')
            setattr(self, field, value)

    def toDic(self):
        result = {}
        for name, value in vars(self).items():
            if name != '_sa_instance_state':
                result[name] = value
        return result


from sqlalchemy.types import TypeDecorator, VARCHAR
import json
class JSONString(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        # 保存到数据库时，自动转为字符串
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        # 查询出来时，自动转为 dict
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return value