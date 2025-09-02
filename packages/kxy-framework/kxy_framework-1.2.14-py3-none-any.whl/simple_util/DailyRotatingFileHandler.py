from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import os
import time

class DailyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename,file_type='log', when='midnight', interval=1, backupCount=5, encoding=None, delay=False, utc=False,maxBytes=10485760,mutiple_process=False):
        # 获取基础文件名（不带日期）
        self.base_filename = filename
        self.file_type = file_type
        # 初始文件名包含当前日期
        self.suffix = "%Y%m%d"
        self.mutiple_process = mutiple_process
        self.baseFilename = self._get_filename()
        self.maxBytes = maxBytes
        self.tommorw = self.get_next_midnight_timestamp()
        super().__init__(
            filename=self.baseFilename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            utc=utc
        )
    def get_next_midnight_timestamp(self):
        # 获取当前时间
        now = datetime.now()
        
        # 计算明天的日期
        next_day = now + timedelta(days=1)
        
        # 设置时间为明天的0点0分0秒
        next_midnight = datetime(next_day.year, next_day.month, next_day.day, 0, 0, 0)
        
        # 转换为时间戳
        next_midnight_timestamp = int(next_midnight.timestamp())
        
        return next_midnight_timestamp
    def _get_base_file_name(self):
        dt = time.strftime('%Y%m%d')
        if self.mutiple_process:
            return f"{self.base_filename}{os.getpid()}.{dt}"
        else:
            return f"{self.base_filename}.{dt}"
    def _get_filename(self):
        return f'{self._get_base_file_name()}.0.{self.file_type}'
    def shouldRollover(self, record):
        # 检查文件大小或日期变更
        if self.stream is None:
            self.stream = self._open()
        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # 文件末尾
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        current_time = int(time.time())
        if current_time >= self.tommorw:
            return 1
        return 0
    def DeleteFiels(self):
        dirName, baseName = os.path.split(self.base_filename)
        fileNames = os.listdir(dirName)
        if len(fileNames)<self.backupCount:
            return
        # 过滤出符合模式的文件
        matching_files = [f for f in fileNames if f.startswith(baseName) and f.endswith(f".{self.file_type}")]
        
        # 按时间排序，最新的文件在最后
        matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(dirName, x)))
        
        # 计算需要保留的文件数量
        files_to_keep = matching_files[-self.backupCount:]
        
        # 删除不需要的文件
        for f in matching_files:
            if f not in files_to_keep:
                os.remove(os.path.join(dirName, f))
          
    def doRollover(self):
        # 处理日期变更和文件大小限制
        if self.stream:
            self.stream.close()
            self.stream = None

        current_time = int(time.time())
        if current_time>=self.tommorw:
            self.baseFilename = self._get_filename()
            self.tommorw = self.get_next_midnight_timestamp()
            self.base_dir = os.path.dirname(self.baseFilename)
            os.makedirs(self.base_dir, exist_ok=True)
        else:
            cnt = int(self.baseFilename.split(".")[-2:][0])
            cnt +=1
            baseFile = self._get_base_file_name()
            dfn = f"{baseFile}.{cnt}.{self.file_type}"
            if os.path.exists(dfn):
                cnt += 1
                while True:
                    dfn = f"{baseFile}.{cnt}.{self.file_type}"
                    if not os.path.exists(dfn):
                        break
                    cnt += 1
            self.baseFilename = dfn
        if self.backupCount > 0:
            self.DeleteFiels()
        if not self.delay:
            self.stream = self._open()
        
        # 更新下次滚动时间
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at += self.interval
        
        self.rolloverAt = new_rollover_at