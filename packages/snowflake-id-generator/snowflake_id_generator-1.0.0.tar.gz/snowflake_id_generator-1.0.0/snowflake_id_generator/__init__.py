"""
雪花算法ID生成器包
提供分布式唯一ID生成，解决高并发下的ID冲突问题
支持多实例部署和水平扩展
"""

from .snowflake import (
    SnowflakeService,
    SnowflakeError,
    init_snowflake_service,
    get_snowflake_service,
    generate_user_id,
    generate_username_from_id,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "分布式雪花算法ID生成器"

__all__ = [
    "SnowflakeService",
    "SnowflakeError", 
    "init_snowflake_service",
    "get_snowflake_service",
    "generate_user_id",
    "generate_username_from_id",
]

