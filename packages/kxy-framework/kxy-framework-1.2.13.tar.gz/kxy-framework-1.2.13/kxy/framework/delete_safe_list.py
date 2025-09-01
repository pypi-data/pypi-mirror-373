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
        
        
    # def remove(self, value):
    #     current_cursor=-1
    #     while True:
    #         if current_cursor < 0:
    #             break
    #         if self.list[self.cursor] == value:
    #             self.list.pop(self.cursor)
    #         else:
    #             break
    #     self.cursor -= 1