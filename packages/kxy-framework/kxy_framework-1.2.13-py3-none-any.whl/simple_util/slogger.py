import json
import logging
import os
import time
import uuid

from simple_util.util import SUtil
from .DailyRotatingFileHandler import DailyRotatingFileHandler
from contextvars import ContextVar

trace_id = ContextVar("trace_id", default='')
session_id = ContextVar("session_id", default='')
seq = ContextVar("seq", default=0)
user_id = ContextVar("user_id", default='0')
user_info = ContextVar("user_info", default={})

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

def create_logger(logLeve,appName,env,filename='log/app',file_type='log',backupCount=5,maxBytes=10485760,mutiple_process=False):
    localIp = SUtil.get_local_ip()
    class JsonFormatter(logging.Formatter):
        def format(self, record):
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
                "message": record.getMessage(),
                "CreateTime": self.formatTime(record, self.datefmt),
                "createdOn": int(time.time() * 1000)  # 添加 Unix 时间戳
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
        when='midnight',
        interval=300,
        backupCount=backupCount,
        maxBytes=maxBytes,  # 10MB
        mutiple_process = mutiple_process
    )
    formatter = JsonFormatter()

    # 设置日志记录级别
    handler.setLevel(logLeve)
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())

    _logger.addHandler(handler)
    return _logger,handler