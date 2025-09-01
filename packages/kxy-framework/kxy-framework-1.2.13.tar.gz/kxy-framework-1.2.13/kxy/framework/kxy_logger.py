from datetime import datetime, timedelta
import json
from logging import Logger
import os
import re
import time
from typing import Any, Dict, List, Optional

from .kxy_logger_filter import ConditionOperator, QueryCondition
from .context import last_log_time

class KxyLogger(Logger):
    def __init__(self, logger:Logger, level=0,basePath='',file_type=''):
        super().__init__(logger.name,logger.level)
        self.logger = logger
        self.parent = logger.parent
        self.propagate = logger.propagate
        self.handlers = logger.handlers
        self.disabled = logger.disabled
        self.basePath = basePath
        self.file_type = file_type
    def refresh_time(self):
        last_log_time.set(time.time())
    def get_filtered_files(self, start_date=None, end_date=None):
        """
        返回self.basePath目录下的文件列表，只返回文件名称为file_type结尾的文件名
        
        Args:
            start_date (str, optional): 开始日期，格式为'20250815'，默认为当天
            end_date (str, optional): 结束日期，格式为'20250815'，默认为当天
            
        Returns:
            list: 符合条件的文件名列表
        """
        if not os.path.exists(self.basePath):
            return []
        
        # 获取目录下所有文件
        all_files = os.listdir(self.basePath)
        
        # 根据文件后缀过滤
        filtered_files = [f for f in all_files if f.endswith(self.file_type)]
        
        # 如果没有指定日期范围，默认使用当天日期
        if start_date is None and end_date is None:
            today = datetime.now().strftime('%Y%m%d')
            start_date = today
            end_date = today
        # 如果只指定了开始日期，结束日期默认为开始日期
        elif start_date is not None and end_date is None:
            end_date = start_date
        # 如果只指定了结束日期，开始日期默认为结束日期
        elif start_date is None and end_date is not None:
            start_date = end_date
        
        # 将日期字符串转换为整数进行比较
        try:
            start_int = int(start_date)
            end_int = int(end_date)
        except (ValueError, TypeError):
            # 如果日期格式不正确，返回空列表
            return []
        
        date_range_files = []
        date_pattern = r'(\d{8})'
        
        for filename in filtered_files:
            match = re.search(date_pattern, filename)
            if match:
                try:
                    file_date = int(match.group(1))
                    # 检查文件日期是否在指定范围内
                    if start_int <= file_date <= end_int:
                        date_range_files.append(filename)
                except ValueError:
                    # 忽略无法解析为整数的日期
                    continue
        
        return date_range_files
    
    def _add_log_category(self, log_method, msg, logCategory='default', *args, **kwargs):
        """通用的日志分类添加方法"""
        extra = kwargs.get('extra', {})
        extra["logCategory"] = logCategory
        kwargs['extra'] = extra
        return log_method(msg, *args, **kwargs)
    
    
    def info(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.info, msg, logCategory, *args, **kwargs)
    
    def debug(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.debug, msg, logCategory, *args, **kwargs)
    
    def warning(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.warning, msg, logCategory, *args, **kwargs)
    
    def error(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.error, msg, logCategory, *args, **kwargs)
    
    def critical(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.critical, msg, logCategory, *args, **kwargs)
    
    def exception(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.exception, msg, logCategory, *args, **kwargs)
    def query(self, start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, 
                            filter: QueryCondition = None) -> List[Dict]:
        """
        查询日志内容，根据traceId组织日志结构
        
        Args:
            start_date (str, optional): 开始日期，格式为'YYYY-MM-DD'，默认为当天
            end_date (str, optional): 结束日期，格式为'YYYY-MM-DD'，默认为当天
            conditions (dict, optional): 查询条件字典，用于过滤日志
        
        Returns:
            List[Dict]: 按traceId组织的日志记录列表
        """
        # 确定查询日期范围
        if start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = start_date

        # 将日期字符串转换为datetime对象
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date == end_date:
            files = self.get_filtered_files(start_date.replace('-', ''))
        else:
            # 将日期格式从 YYYY-MM-DD 转换为 YYYYMMDD
            start_date_fmt = start_date.replace('-', '')
            end_date_fmt = end_date.replace('-', '')
            files = self.get_filtered_files(start_date=start_date_fmt, end_date=end_date_fmt)

        
        # 存储所有相关日志和traceId映射
        trace_logs = {}  # traceId -> [log_entries]
        matched_logs = []  # 初步匹配的日志
        
        # 第一步：遍历指定日期范围内的所有日志文件
        conditions = []
        if filter:
            conditions = filter.to_dict()

        for filename in files:
            file_path = os.path.join(self.basePath, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            
                            # 收集所有日志中的traceId
                            trace_id = log_entry.get('traceId', '')
                            if trace_id:
                                if trace_id not in trace_logs:
                                    trace_logs[trace_id] = []
                                trace_logs[trace_id].append(log_entry)
                            
                            # 检查是否符合查询条件
                            if not conditions or self._match_conditions(log_entry, conditions):
                                matched_logs.append(log_entry)
                        except json.JSONDecodeError:
                            # 跳过无效的JSON行
                            continue
            except IOError:
                # 跳过无法读取的文件
                continue
        
        # 第二步：找出匹配日志相关的所有traceId
        related_trace_ids = set()
        for log_entry in matched_logs:
            trace_id = log_entry.get('traceId', '')
            if trace_id:
                related_trace_ids.add(trace_id)
        
        # 第三步：收集所有相关traceId的所有日志（包括其他日期的）
        all_related_logs = []
        for trace_id in related_trace_ids:
            if trace_id in trace_logs:
                all_related_logs.extend(trace_logs[trace_id])
            else:
                # 如果traceId不在当前日期范围内，需要在整个日志目录中查找
                all_files = self.get_filtered_files()  # 获取所有文件
                for filename in all_files:
                    file_path = os.path.join(self.basePath, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                try:
                                    log_entry = json.loads(line.strip())
                                    if log_entry.get('traceId', '') == trace_id:
                                        all_related_logs.append(log_entry)
                                except json.JSONDecodeError:
                                    continue
                    except IOError:
                        continue
        
        # 第四步：重新组织traceId映射
        final_trace_logs = {}
        for log_entry in all_related_logs:
            trace_id = log_entry.get('traceId', '')
            if trace_id not in final_trace_logs:
                final_trace_logs[trace_id] = []
            final_trace_logs[trace_id].append(log_entry)
        
        # 第五步：按seqId组织日志结构
        result = []
        for trace_id, logs in final_trace_logs.items():
            # 按seqId排序
            logs.sort(key=lambda x: x.get('seqId', 0))
            
            # 找到seqId为1的首行日志
            head_log = None
            children_logs = []
            
            for log in logs:
                if log.get('seqId', 0) == 1:
                    head_log = log
                else:
                    children_logs.append(log)
            
            # 构造返回结构
            if head_log:
                head_log['children'] = children_logs
                result.append(head_log)
            else:
                # 如果没有找到seqId为1的日志，则将第一个作为首行
                if logs:
                    head_log = logs[0]
                    head_log['children'] = logs[1:]
                    result.append(head_log)
        
        return result

    def _match_conditions(self, log_entry: Dict, conditions: Dict[str, Any]) -> bool:
        """
        检查日志条目是否符合给定条件，支持多种比较操作
        
        Args:
            log_entry (Dict): 日志条目
            conditions (Dict): 查询条件，支持以下操作符：
                - 默认(直接比较): {'level': 'ERROR'}
                - 大于: {'seqId': {ConditionOperator.GREATER_THAN: 10}}
                - 小于: {'seqId': {ConditionOperator.LESS_THAN: 100}}
                - 不等于: {'level': {ConditionOperator.NOT_EQUAL: 'DEBUG'}}
                - 包含: {'message': {ConditionOperator.CONTAINS: 'error'}}
            
        Returns:
            bool: 是否匹配
        """
        for key, condition in conditions.items():
            # 如果字段不存在于日志条目中，不匹配
            if key not in log_entry:
                return False
                
            log_value = log_entry[key]
            
            # 处理不同的条件类型
            if isinstance(condition, dict):
                # 处理操作符条件
                for op, value in condition.items():
                    # 支持字符串和枚举形式的操作符
                    op_value = op.value if isinstance(op, ConditionOperator) else op
                    
                    if op_value == ConditionOperator.GREATER_THAN.value:  # 大于
                        if not (log_value > value):
                            return False
                    elif op_value == ConditionOperator.LESS_THAN.value:  # 小于
                        if not (log_value < value):
                            return False
                    elif op_value == ConditionOperator.NOT_EQUAL.value:  # 不等于
                        if not (log_value != value):
                            return False
                    elif op_value == ConditionOperator.CONTAINS.value:  # 包含
                        if not isinstance(log_value, str) or value not in log_value:
                            return False
                    else:
                        # 不支持的操作符
                        return False
            else:
                # 默认相等比较
                if log_value != condition:
                    return False
                    
        return True
