class FilterDepartment:
    def __init__(self, field_name='DepartmentId'):
        self.field_name = field_name
    
    def __call__(self, cls):
        cls._dep_field = self.field_name
        return cls