import copy
from typing import Tuple,List,Any
class DeleteSafeList():
    def __init__(self, list):
        self.list = list
        self.cursor = len(list)
    
    def __iter__(self):
        self.cursor = len(self.list)
        return self
    
    def __next__(self):
        if self.cursor <= 0:
            self.cursor = len(self.list)
            raise StopIteration
        self.cursor -= 1
        return self.list[self.cursor]
    def RemoveCurrent(self):
        self.list.pop(self.cursor)
    def __len__(self):
        return len(self.list)
        
    def diffrent_with(self,newlist:List[Any])->Tuple[List[Any],List[Any]]:
        """_summary_

        Args:
            self (_type_): 原来的列表
            newlist (_type_): 新的列表

        Returns:
            Tuple[List[any],List[any]]: 删除的列表,新增的列表
        """        
        if not self.list:
            return [],newlist
        if not newlist:
            return self.list,[]
        c_oldlist=copy.deepcopy(self.list) 
        c_newlist=copy.deepcopy(newlist) 
        
        c_oldlist=DeleteSafeList(c_oldlist)
        for item in c_oldlist:
            if item in c_newlist:
                c_oldlist.RemoveCurrent()
                c_newlist.remove(item)
        return list(c_oldlist),list(c_newlist)