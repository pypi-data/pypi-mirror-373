# coding=UTF-8

from friendly_exception import FriendlyException

from simple_util import SnowflakeIDGenerator
idgenerator = SnowflakeIDGenerator()
class BaseEntity():

    InsertOtherFields = []
    InsertRequireFields = []
    UpdateFiles = []
    __AutoId__ = True
    
    def __init__(self):
        if self.__AutoId__:
            self.Id = str(idgenerator.get_next_id())

    # 插入字段
    def InitInsertEntityWithJson(self, json_data):
        self.__init_require__(json_data, self.InsertRequireFields)
        self.__init_fileds__(json_data, self.InsertOtherFields)
        if self.__AutoId__ and not self.Id:
            self.Id = str(idgenerator.get_next_id())

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
