from enum import Enum
from typing import Any, Dict, Union

class ConditionOperator(Enum):
    """查询条件操作符枚举"""
    GREATER_THAN = '$gt'      # 大于
    LESS_THAN = '$lt'         # 小于
    NOT_EQUAL = '$ne'         # 不等于
    CONTAINS = '$contains'    # 包含

class QueryCondition:
    """查询条件类，用于构建复杂的查询条件"""
    
    def __init__(self):
        self.conditions = {}
    
    @classmethod
    def eq(cls, field: str, value: Any) -> 'QueryCondition':
        """等于条件"""
        instance = cls()
        instance.conditions[field] = value
        return instance
    
    @classmethod
    def gt(cls, field: str, value: Any) -> 'QueryCondition':
        """大于条件"""
        instance = cls()
        instance.conditions[field] = {ConditionOperator.GREATER_THAN: value}
        return instance
    
    @classmethod
    def lt(cls, field: str, value: Any) -> 'QueryCondition':
        """小于条件"""
        instance = cls()
        instance.conditions[field] = {ConditionOperator.LESS_THAN: value}
        return instance
    
    @classmethod
    def ne(cls, field: str, value: Any) -> 'QueryCondition':
        """不等于条件"""
        instance = cls()
        instance.conditions[field] = {ConditionOperator.NOT_EQUAL: value}
        return instance
    
    @classmethod
    def contains(cls, field: str, value: str) -> 'QueryCondition':
        """包含条件"""
        instance = cls()
        instance.conditions[field] = {ConditionOperator.CONTAINS: value}
        return instance
    
    def and_(self, other: 'QueryCondition') -> 'QueryCondition':
        """与操作，组合多个条件"""
        new_condition = QueryCondition()
        new_condition.conditions.update(self.conditions)
        new_condition.conditions.update(other.conditions)
        return new_condition
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，供查询使用"""
        return self.conditions
