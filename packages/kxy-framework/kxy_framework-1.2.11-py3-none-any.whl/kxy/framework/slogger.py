import json
import logging
import os
import time
import uuid
from logging import Handler

from .kxy_logger import KxyLogger
from .util import SUtil
from .DailyRotatingFileHandler import DailyRotatingFileHandler
from .context import trace_id,session_id,seq,user_id,last_log_time

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id.get()
        record.session_id = session_id.get()
        record.userid = user_id.get()
        cur_seq = seq.get()
        record.seq = cur_seq
        seq.set(cur_seq+1)
        return True
def new_trace(traceId=''):
    if not traceId:
        traceId = uuid.uuid4().hex[:16]
    trace_id.set(traceId)
    session_id.set(uuid.uuid4().hex[:16])
    seq.set(0)
def create_logger(logLeve,appName,env,filename='log/app',file_type='log',backupCount=5,maxBytes=10485760,mutiple_process=False,cleanup_mode='delete', disk_max=80)->tuple[KxyLogger,Handler]:
    """
        初始化日志处理器实例
        
        Args:
            appName:应用名称
            filename (str): 日志文件名
            file_type (str, optional): 文件类型，默认为'log'
            when (str, optional): 日志轮转时间点，默认为'D', S:秒,M:每分,H:每小时,D:一天,W:每周
            interval (int, optional): 日志轮转间隔，默认为1
            backupCount (int, optional): 保留的备份文件数量，默认为5
            maxBytes (int, optional): 单个日志文件最大字节数，默认为10485760（10MB）
            mutiple_process (bool, optional): 是否支持多进程写入，默认为False
            cleanup_mode (str, optional): 清理模式，默认为'delete'- 删除， 'zip'-压缩
            disk_max (int, optional): 压缩阈值，默认为80，当磁盘超过80%时，立即压缩日志文件，否则在夜间0-6 之间压缩日志
    """
    localIp = SUtil.get_local_ip()
    if '/' not in filename or filename[-1]=='/':
        raise Exception('filename must be like "log/xxx"')
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            # 计算与上次日志的时间间隔
            current_time = time.time()
            prev_time = last_log_time.get()
            duration = current_time - prev_time if prev_time > 0 else 0
            last_log_time.set(current_time)
            
            # 构建日志记录的字典
            log_record = {
                "appName":appName,
                "serverAddr":os.environ.get('IP',localIp),
                "cluster": env,
                "level": record.levelname,
                "filename": record.filename,
                "lineno": record.lineno,
                "traceId": record.trace_id,
                "sessionId": record.session_id,
                "userId":record.userid,
                "seqId": record.seq,
                "logCategory":record.logCategory,
                "message": record.getMessage(),
                "CreateTime": self.formatTime(record, self.datefmt),
                "createdOn": int(time.time() * 1000),  # 添加 Unix 时间戳
                "duration": int(duration * 10000000)  # 添加持续时间，单位毫秒，保留2位小数
            }
            # 将字典转换为 JSON 字符串
            return json.dumps(log_record, ensure_ascii=False)
        
    logging.basicConfig(
        level=logLeve
    )
    _logger = logging.getLogger(appName)
    _logger.setLevel(logLeve)
    # 创建一个 RotatingFileHandler 对象
    # 确保 log 目录存在
    if '/' in filename:
        floder = filename.split('/')[0]
        os.makedirs(floder, exist_ok=True)
    handler = DailyRotatingFileHandler(
        filename=filename,
        file_type=file_type,
        when='D',
        interval=300,
        backupCount=backupCount,
        maxBytes=maxBytes,  # 10MB
        mutiple_process = mutiple_process,
        cleanup_mode = cleanup_mode,
        disk_max = disk_max
    )
    formatter = JsonFormatter()

    # 设置日志记录级别
    handler.setLevel(logLeve)
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())

    _logger.addHandler(handler)
    logger = KxyLogger(_logger,filename,file_type)
    return logger,handler