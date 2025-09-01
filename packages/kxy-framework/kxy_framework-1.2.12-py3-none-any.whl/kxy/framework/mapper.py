from typing import Generic, TypeVar


T = TypeVar("T")

class Mapper:
    __mapper_relation = {}
    logger=None
    @staticmethod
    def register(cls):
        name=cls.__name__
        if Mapper.__mapper_relation.get(name) is None:
            Mapper.__mapper_relation[cls.__name__] = cls

    @staticmethod
    def getservice(clsName,*arg,**agrs):
        return Mapper.__mapper_relation[clsName](*arg,**agrs)
    @staticmethod
    def getservice_by_contract(contract:T,*arg,**agrs)->T:
        clsName=contract.__name__.replace("I","",1)
        return Mapper.__mapper_relation[clsName](*arg,**agrs)
    @staticmethod
    def getclass(clsName):
        return Mapper.__mapper_relation[clsName]