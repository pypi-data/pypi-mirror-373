## 使用方法：
pip install kxy-framework
```python
from kxy.framework.context import *


```


# 日志
```python
from kxy.framework.slogger import create_logger

logger,handler = create_logger(logging.DEBUG,'appName','production',filename='log/app',file_type='log',backupCount=5,maxBytes=10485760,mutiple_process=False)

# mutiple_process 是否多进程，多进程需要生成不同的文件

logger.info('hello world',extra={"logCategory":'http'})
```
### 日志进阶用法，设置traceId：
```python
from kxy.framework.slogger import user_id,user_info,new_trace
req_trace_id = request.headers.get("X-Trace-ID") or str(uuid4())
new_trace(req_trace_id)
user_id.set('login user id')
# user_info用于存储用户自定义的信息，方便在其他地方取用
user_info.set({'name':'login user name','email':'login user email'})

```
### 日志自定义打印格式：
```python

class JsonFormatter(logging.Formatter):
    def format(self, record):
        # 构建日志记录的字典
        log_record = {
            "appName":appName,
            "serverAddr":os.environ.get('IP',localIp),
            "cluster": env,
            "levelname": record.levelname,
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

from simple_util.slogger import create_logger

logger,handler = create_logger(logging.DEBUG,'appName','production',filname='log/app',file_type='log',backupCount=5,maxBytes=10485760)
handler.setFormatter(JsonFormatter())
logger.info('hello world')
```