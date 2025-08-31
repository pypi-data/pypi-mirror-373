import socket
import struct
import time
# 获取机器标识
def get_machine_id():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return struct.unpack('!L', socket.inet_aton(ip_address))[0] & 0xFFFF
MACHINEID = get_machine_id()
class SnowflakeIDGenerator:
    def __init__(self):
        self.machine_id = MACHINEID  # 机器标识，每个实例不同
        self.sequence = 0  # 序列号，每毫秒内递增
        self.last_timestamp = -1  # 上次生成ID的时间戳

    def _get_timestamp(self):
        return int(time.time() * 1000)

    def get_next_id(self)->int:
        timestamp = self._get_timestamp()

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFFF  # 序列号循环
            if self.sequence == 0:
                timestamp = self._wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        # 构建ID
        id = (timestamp << 22) | (self.machine_id << 12) | self.sequence
        return id

    def _wait_next_millis(self, last_timestamp):
        timestamp = self._get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp()
        return timestamp


