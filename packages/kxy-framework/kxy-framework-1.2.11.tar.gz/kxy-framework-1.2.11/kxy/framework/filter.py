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

class FilterTenant:
    """
    用于标记模型类需要进行租户数据过滤的注解
    """
    def __init__(self, field_name='tenantId'):
        """
        初始化 FilterTenant 注解
        
        Args:
            field_name (str): 租户字段名称，默认为 'TenantId'
        """
        self.field_name = field_name
    
    def __call__(self, cls):
        """
        使 FilterTenant 成为一个类装饰器
        
        Args:
            cls: 被装饰的模型类
            
        Returns:
            cls: 返回被装饰的类，并添加 tenant_field 属性
        """
        # 为类添加租户字段信息
        cls._tenant_field = self.field_name
        return cls
    
class FilterDepartment:
    def __init__(self, field_name='DepartmentId'):
        self.field_name = field_name
    
    def __call__(self, cls):
        cls._dep_field = self.field_name
        return cls
    
class FilterUser:

    def __init__(self, field_name='userId'):
        self.field_name = field_name
    
    def __call__(self, cls):
        """
        使 FilterTenant 成为一个类装饰器
        
        Args:
            cls: 被装饰的模型类
            
        Returns:
            cls: 返回被装饰的类，并添加 tenant_field 属性
        """
        # 为类添加租户字段信息
        cls._user_field = self.field_name
        return cls