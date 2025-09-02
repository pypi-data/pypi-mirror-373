import time
from typing import Any

from fastapi.exceptions import RequestValidationError


# 64位ID的划分
from fastgenerateapi.settings.all_settings import settings

WORKER_ID_BITS = 5   # 机器位
DATACENTER_ID_BITS = 5    # 数据位
SEQUENCE_BITS = 12    # 循环位

# 最大取值计算
MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)
MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)

# 移位偏移计算
WOKER_ID_SHIFT = SEQUENCE_BITS
DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

# 序号循环掩码
SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

# Twitter元年时间戳
# TWEPOCH = 1288834974657
# 2022年10月24号00:00
TWEPOCH = 1666540800000


class InvalidSystemClock(Exception):
    def __init__(
            self,
            status_code: int = 400,
            message: str = "请求失败",
            detail: Any = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.detail = detail


class IdWorker(object):
    """
    用于生成IDs
    """

    def __init__(self, datacenter_id=1, worker_id=1, sequence=0):
        """
        初始化
        :param datacenter_id: 数据中心（机器区域）ID
        :param worker_id: 机器ID
        :param sequence: 其实序号
        """
        # sanity check
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError('worker_id值越界')

        if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError('datacenter_id值越界')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence

        self.last_timestamp = -1  # 上次计算的时间戳

    def _gen_timestamp(self):
        """
        生成整数时间戳
        :return:int timestamp
        """
        return int(time.time() * 1000)

    def get_code(self, prefix: str = ""):
        """
        获取有序编码,高并发不推荐使用，会出现重复值
        :return:
        """
        def make_code():
            timestamp = self._gen_timestamp()

            # 时钟回拨
            if timestamp < self.last_timestamp:
                raise RequestValidationError

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 7
                if self.sequence == 0:
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            new_id = (int((timestamp - TWEPOCH) / 100) << 2) | (self.datacenter_id << 2) | \
                     (self.worker_id << 2) | self.sequence
            return prefix + str(new_id)
        return make_code

    def get_id(self):
        """
        获取新ID
        :return:
        """
        timestamp = self._gen_timestamp()

        # 时钟回拨
        if timestamp < self.last_timestamp:
            # logging.error('clock is moving backwards. Rejecting requests until {}'.format(self.last_timestamp))
            raise InvalidSystemClock(
                status_code=500,
                message='时钟回拨异常',
                detail='clock is moving backwards. Rejecting requests until {}'.format(self.last_timestamp))

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT) | (self.datacenter_id << DATACENTER_ID_SHIFT) | \
                 (self.worker_id << WOKER_ID_SHIFT) | self.sequence
        return new_id

    def _til_next_millis(self, last_timestamp):
        """
        等到下一毫秒
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp


worker = IdWorker(datacenter_id=settings.app_settings.DATACENTER_ID, worker_id=settings.app_settings.WORKER_ID)


if __name__ == '__main__':
    # worker = IdWorker()
    print(worker.get_code()())
    print(worker.get_code("A")())
#     pk = worker.get_id()
#     print(pk)
#     print(len(str(pk)), len("9223372036854775807"))
#     print(bin(pk))
#     print(len(bin(pk)))
