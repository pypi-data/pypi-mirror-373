from functools import wraps

def ignore_filter(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # 保存原始状态
        original_state = getattr(self, 'IgnoreFilter', False)
        self.IgnoreFilter = True
        try:
            return await func(self, *args, **kwargs)
        finally:
            # 恢复原始状态
            self.IgnoreFilter = original_state
    return wrapper