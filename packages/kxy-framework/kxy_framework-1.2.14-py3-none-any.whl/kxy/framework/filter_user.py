# 在 base_dal.py 文件的顶部附近添加以下代码

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