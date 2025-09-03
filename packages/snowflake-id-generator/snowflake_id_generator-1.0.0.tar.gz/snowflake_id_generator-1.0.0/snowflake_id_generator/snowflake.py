"""
雪花算法服务模块
提供分布式唯一ID生成，解决高并发下的用户ID冲突问题
支持多实例部署和水平扩展
"""

import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


class SnowflakeError(Exception):
    """雪花算法相关异常"""

    pass


class SnowflakeService:
    """
    雪花算法ID生成器

    64位ID结构：
    1位符号位(0) + 41位时间戳 + 10位机器ID + 12位序列号

    - 时间戳：41位，可用约69年（从epoch开始）
    - 机器ID：10位，支持0-1023个实例
    - 序列号：12位，每毫秒最多4096个ID

    特性：
    - 全局唯一
    - 大致有序（基于时间戳）
    - 高性能（本地生成，无IO）
    - 分布式友好
    """

    # 位数配置
    WORKER_ID_BITS = 5  # 工作机器ID位数
    DATACENTER_ID_BITS = 5  # 数据中心ID位数
    SEQUENCE_BITS = 12  # 序列号位数

    # 最大值计算
    MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1  # 31
    MAX_DATACENTER_ID = (1 << DATACENTER_ID_BITS) - 1  # 31
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1  # 4095

    # 位移量
    WORKER_ID_SHIFT = SEQUENCE_BITS  # 12
    DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS  # 17
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS  # 22

    def __init__(self, worker_id: int, datacenter_id: int, epoch: Optional[int] = None):
        """
        初始化雪花算法生成器

        Args:
            worker_id: 工作机器ID (0-31)
            datacenter_id: 数据中心ID (0-31)
            epoch: 起始时间戳（毫秒），默认为2020-01-01 00:00:00
        """
        # 参数验证
        if worker_id < 0 or worker_id > self.MAX_WORKER_ID:
            raise SnowflakeError(f"worker_id必须在0-{self.MAX_WORKER_ID}之间")

        if datacenter_id < 0 or datacenter_id > self.MAX_DATACENTER_ID:
            raise SnowflakeError(f"datacenter_id必须在0-{self.MAX_DATACENTER_ID}之间")

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id

        # 默认epoch为2020年1月1日（UTC）
        self.epoch = epoch or 1577836800000  # 2020-01-01 00:00:00 UTC

        # 状态变量
        self.sequence = 0
        self.last_timestamp = -1

        # 线程锁，确保线程安全
        self._lock = threading.Lock()

        logger.debug(
            f"Snowflake service configuration: worker_id={worker_id}, "
            f"datacenter_id={datacenter_id}, epoch={self.epoch}"
        )

    def _current_millis(self) -> int:
        """获取当前毫秒时间戳"""
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp: int) -> int:
        """等待下一个毫秒"""
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_millis()
        return timestamp

    def generate_id(self) -> int:
        """
        生成雪花ID

        Returns:
            int: 64位雪花ID

        Raises:
            SnowflakeError: 时钟回拨或其他错误
        """
        with self._lock:
            timestamp = self._current_millis()

            # 时钟回拨检测
            if timestamp < self.last_timestamp:
                offset = self.last_timestamp - timestamp
                raise SnowflakeError(
                    f"时钟回拨检测到，回拨了{offset}毫秒，请检查系统时钟"
                )

            # 同一毫秒内的序列号处理
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    # 序列号用完，等待下一毫秒
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                # 新的毫秒，序列号重置为0
                self.sequence = 0

            # 更新最后时间戳
            self.last_timestamp = timestamp

            # 构建64位ID
            snowflake_id = (
                    ((timestamp - self.epoch) << self.TIMESTAMP_LEFT_SHIFT)
                    | (self.datacenter_id << self.DATACENTER_ID_SHIFT)
                    | (self.worker_id << self.WORKER_ID_SHIFT)
                    | self.sequence
            )

            return snowflake_id

    def parse_id(self, snowflake_id: int) -> dict:
        """
        解析雪花ID，提取各组件信息

        Args:
            snowflake_id: 雪花ID

        Returns:
            dict: 包含时间戳、数据中心ID、工作机器ID、序列号的字典
        """
        # 提取各部分
        sequence = snowflake_id & self.MAX_SEQUENCE

        worker_id = (snowflake_id >> self.WORKER_ID_SHIFT) & self.MAX_WORKER_ID

        datacenter_id = (
                                snowflake_id >> self.DATACENTER_ID_SHIFT
                        ) & self.MAX_DATACENTER_ID

        timestamp = (snowflake_id >> self.TIMESTAMP_LEFT_SHIFT) + self.epoch

        return {
            "timestamp": timestamp,
            "datacenter_id": datacenter_id,
            "worker_id": worker_id,
            "sequence": sequence,
            "readable_time": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime(timestamp / 1000)
            ),
        }

    def get_info(self) -> dict:
        """
        获取雪花算法生成器状态信息

        Returns:
            dict: 状态信息
        """
        return {
            "worker_id": self.worker_id,
            "datacenter_id": self.datacenter_id,
            "epoch": self.epoch,
            "current_timestamp": self._current_millis(),
            "last_timestamp": self.last_timestamp,
            "current_sequence": self.sequence,
            "max_sequence": self.MAX_SEQUENCE,
        }

    def generate_username(self, user_id: int) -> str:
        """
        基于雪花ID生成用户名

        Args:
            user_id: 雪花算法生成的用户ID

        Returns:
            str: 用户名格式为 u{user_id}
        """
        return f"u{user_id}"


# 全局雪花算法服务实例
_snowflake_service: Optional[SnowflakeService] = None

# =================================
# 雪花算法配置 - 用于生成分布式唯一ID
# =================================
# 工作机器ID（0-31），每个实例应使用不同的ID
SNOWFLAKE_WORKER_ID: int = 1

# 数据中心ID（0-31），用于区分不同部署环境
SNOWFLAKE_DATACENTER_ID: int = 1

# 起始时间戳（毫秒），默认为2020-01-01 00:00:00 UTC
# 可用约69年，直到2089年
SNOWFLAKE_EPOCH: int = 1577836800000

# 雪花算法性能监控
SNOWFLAKE_ENABLE_METRICS: bool = True


def init_snowflake_service() -> None:
    """初始化雪花算法服务"""
    global _snowflake_service

    if _snowflake_service is not None:
        logger.warning("Snowflake service already initialized")
        return

    try:
        _snowflake_service = SnowflakeService(
            worker_id=SNOWFLAKE_WORKER_ID,
            datacenter_id=SNOWFLAKE_DATACENTER_ID,
            epoch=SNOWFLAKE_EPOCH,
        )
        logger.debug("Snowflake service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize snowflake service: {e}")
        raise


def get_snowflake_service() -> SnowflakeService:
    """
    获取雪花算法服务实例

    Returns:
        SnowflakeService: 雪花算法服务实例

    Raises:
        SnowflakeError: 服务未初始化
    """
    if _snowflake_service is None:
        raise SnowflakeError(
            "Snowflake service not initialized. Call init_snowflake_service() first."
        )

    return _snowflake_service


def generate_user_id() -> int:
    """
    便捷函数：生成用户ID

    Returns:
        int: 雪花算法生成的用户ID
    """
    return get_snowflake_service().generate_id()


def generate_username_from_id(user_id: int) -> str:
    """
    便捷函数：基于用户ID生成用户名

    Args:
        user_id: 用户ID

    Returns:
        str: 用户名
    """
    return get_snowflake_service().generate_username(user_id)

