from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import os
import time
import shutil
import gzip

class DailyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename,file_type='log', when='D', interval=30, backupCount=5, encoding=None, delay=False, utc=False,maxBytes=10485760,mutiple_process=False,cleanup_mode='delete', disk_max=80):
        """
        初始化日志处理器实例
        
        Args:
            filename (str): 日志文件名
            file_type (str, optional): 文件类型，默认为'log'
            when (str, optional): 日志轮转时间点，默认为'D', S:秒,M:每分,H:每小时,D:一天,W:每周
            interval (int, optional): 日志轮转间隔，默认为1
            backupCount (int, optional): 保留的备份文件数量，默认为5
            encoding (str, optional): 文件编码格式，默认为None
            delay (bool, optional): 是否延迟创建文件，默认为False
            utc (bool, optional): 是否使用UTC时间，默认为False
            maxBytes (int, optional): 单个日志文件最大字节数，默认为10485760（10MB）
            mutiple_process (bool, optional): 是否支持多进程写入，默认为False
            cleanup_mode (str, optional): 清理模式，默认为'delete'- 删除， 'zip'-压缩
            disk_max (int, optional): 压缩阈值，默认为80，当磁盘超过80%时，立即压缩日志文件，否则在夜间压缩日志
        """
        # 获取基础文件名（不带日期）
        self.base_filename = filename
        self.file_type = file_type
        # 初始文件名包含当前日期
        self.suffix = "%Y%m%d"
        self.mutiple_process = mutiple_process
        self.baseFilename = self._get_filename()
        self.maxBytes = maxBytes
        self.tommorw = self.get_next_midnight_timestamp()
        # 检查gzip是否可用
        self.gzip_available = self._check_gzip_availability()
        # 新增参数
        self.cleanup_mode = cleanup_mode  # 'delete' 或 'compress'
        self.compression_threshold = disk_max  # 磁盘使用率阈值
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
    def DeleteFiles(self):
        dirName = './'+self.base_filename
        baseName = self.base_filename
        if '/' in self.base_filename:
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
                file_path = os.path.join(dirName, f)
                if self.cleanup_mode == 'delete':
                    # 保持现有逻辑，直接删除
                    os.remove(file_path)
                elif self.cleanup_mode == 'zip':
                    # 压缩模式
                    disk_usage = self._get_disk_usage()
                    # 如果磁盘使用率大于阈值或当前为低峰时段，则压缩
                    if disk_usage > self.compression_threshold or self._is_off_peak_time():
                        self._compress_file(file_path)
                    else:
                        break
    def _check_gzip_availability(self):
        """检查gzip模块是否可用"""
        try:
            import gzip
            return True
        except ImportError:
            return False
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
            self.DeleteFiles()
        if not self.delay:
            self.stream = self._open()
        
        # 更新下次滚动时间
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at += self.interval
        
        self.rolloverAt = new_rollover_at
    def _get_disk_usage(self):
        """获取磁盘使用率"""
        total, used, free = shutil.disk_usage(os.path.dirname(self.base_filename) or '.')
        return (used / total) * 100 if total > 0 else 0
        
    def _is_off_peak_time(self):
        """判断是否为0-8点之间"""
        current_hour = datetime.now().hour
        return 0 <= current_hour < 8
        
    def _compress_file(self, filepath):
        """压缩文件并删除原文件"""
        # 只有在gzip可用时才执行压缩
        if not self.gzip_available:
            # 如果gzip不可用，则直接删除文件
            os.remove(filepath)
            return
            
        try:
            import gzip
            compressed_path = filepath + '.gz'
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(filepath)
            return compressed_path
        except Exception as e:
            # 如果压缩失败，则直接删除原文件
            # os.remove(filepath)
            # 可以选择记录错误日志
            print(f"Compression failed for {filepath}: {e}")
            return None