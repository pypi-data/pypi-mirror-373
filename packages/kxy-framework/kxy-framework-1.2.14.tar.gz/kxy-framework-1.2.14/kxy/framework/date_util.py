from datetime import datetime, timedelta
import time
from typing import Tuple

class DateUtil():
    @staticmethod
    def now_timestamp()->float:
        '''获取当前时间戳'''
        return time.time()
    
    @staticmethod
    def convert_timestamp_to_datetime(timestamp:int)->datetime:
        '''时间戳转时间'''
        # 判断时间戳单位：如果大于1e10，则认为是毫秒单位
        if timestamp > 1e10:
            # 毫秒单位，需要转换为秒
            timestamp_seconds = timestamp / 1000
        else:
            # 秒单位，直接使用
            timestamp_seconds = timestamp
        
        return datetime.fromtimestamp(timestamp_seconds)
    @staticmethod
    def is_expired_timestamp(timestamp)->bool:
        '''判断时间戳是否过期'''
        return DateUtil.now_timestamp() > timestamp
    @staticmethod
    def is_expired_date(date:datetime)->bool:
        '''判断时间是否过期'''
        return DateUtil.is_expired_timestamp(date.timestamp())
    
    @staticmethod
    def timestamp_range_str(begin_time_str,end_time_str)->Tuple[float,float]:
        date_format = "%Y-%m-%d %H:%M:%S"
        start_time = datetime.strptime(begin_time_str, date_format)
        end_time = datetime.strptime(end_time_str, date_format)
        return DateUtil.timestamp_range(start_time,end_time)
    @staticmethod
    def timestamp_range(start_time:datetime,end_time:datetime)->Tuple[float,float]:
        # 转换为时间戳
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        return start_timestamp,end_timestamp
    @staticmethod
    def timestamp_from_now(day=0,hours=0,minutes=0,seconds=0)->Tuple[float,float]:
        """计算从当前时间到未来时间，返回时间戳(精确到秒)，如果传入负数，则返回从过去到当前的时间戳

        Args:
            day (int, optional): 天. Defaults to 0.
            hours (int, optional): 小时. Defaults to 0.
            minutes (int, optional): 分钟. Defaults to 0.
            seconds (int, optional): 秒. Defaults to 0.

        Returns:
            Tuple[float,float]: 开始时间戳，结束时间戳
        """        
        now =datetime.now()
        end = now + timedelta(days=day,hours=hours,minutes=minutes,seconds=seconds)
        now_t = int(now.timestamp())
        end_t = int(end.timestamp())
        if now_t > end_t:
            return end_t,now_t
        return now_t,end_t
    @staticmethod
    def get0230(day:datetime)->Tuple[datetime,datetime]:
        begin = datetime(day.year, day.month, day.day,hour=0,minute=0,second=0)
        end = datetime(day.year, day.month, day.day,hour=23,minute=59,second=59)
        return begin,end
        
    @staticmethod
    def datetime_range(day:datetime,beginHour=22,beginMinits=0,willHour=0) -> Tuple[datetime,datetime]:
        """获取指定日期的指定小时到指定小时的时间，如果endHour小于beginHour，则结束时间为第二天

        Args:
            day (datetime): 日期
            beginHour (int, optional): 开始小时. Defaults to 22.
            beginMinits (int, optional): 开始分钟. Defaults to 0.
            willHour (int, optional): 未来偏移量小时. Defaults to 8.

        Returns:
            Tuple[datetime.datetime,datetime.datetime]: _description_
        """        
        begin=datetime(day.year, day.month, day.day,hour=beginHour,minute=beginMinits)
        end=None
        if willHour:
            end=begin+timedelta(hours=willHour)
        else:
            end = begin
        if end<begin:
            return end,begin
        return begin,end
        
        
if __name__ == '__main__':
    # print(DateUtil.timestamp_from_now(minutes=-5))
    print(DateUtil.getRangeDate(datetime.now(),beginHour=22,willHour=10))