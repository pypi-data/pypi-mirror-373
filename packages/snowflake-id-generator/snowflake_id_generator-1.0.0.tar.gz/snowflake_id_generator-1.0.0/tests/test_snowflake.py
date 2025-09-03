"""
雪花算法测试模块
"""

import unittest
import time
from snowflake_id_generator import (
    SnowflakeService,
    SnowflakeError,
    init_snowflake_service,
    get_snowflake_service,
    generate_user_id,
)


class TestSnowflakeService(unittest.TestCase):
    """雪花算法服务测试类"""

    def setUp(self):
        """测试前准备"""
        self.generator = SnowflakeService(worker_id=1, datacenter_id=1)

    def test_init_with_valid_params(self):
        """测试有效参数初始化"""
        generator = SnowflakeService(worker_id=1, datacenter_id=1)
        self.assertEqual(generator.worker_id, 1)
        self.assertEqual(generator.datacenter_id, 1)

    def test_init_with_invalid_worker_id(self):
        """测试无效工作机器ID"""
        with self.assertRaises(SnowflakeError):
            SnowflakeService(worker_id=32, datacenter_id=1)

    def test_init_with_invalid_datacenter_id(self):
        """测试无效数据中心ID"""
        with self.assertRaises(SnowflakeError):
            SnowflakeService(worker_id=1, datacenter_id=32)

    def test_generate_id(self):
        """测试ID生成"""
        id1 = self.generator.generate_id()
        id2 = self.generator.generate_id()
        
        self.assertIsInstance(id1, int)
        self.assertIsInstance(id2, int)
        self.assertGreater(id1, 0)
        self.assertGreater(id2, 0)
        self.assertNotEqual(id1, id2)

    def test_id_uniqueness(self):
        """测试ID唯一性"""
        ids = set()
        for _ in range(1000):
            id = self.generator.generate_id()
            self.assertNotIn(id, ids)
            ids.add(id)

    def test_parse_id(self):
        """测试ID解析"""
        id = self.generator.generate_id()
        info = self.generator.parse_id(id)
        
        self.assertIn('timestamp', info)
        self.assertIn('datacenter_id', info)
        self.assertIn('worker_id', info)
        self.assertIn('sequence', info)
        self.assertIn('readable_time', info)
        
        self.assertEqual(info['datacenter_id'], 1)
        self.assertEqual(info['worker_id'], 1)

    def test_get_info(self):
        """测试获取状态信息"""
        info = self.generator.get_info()
        
        self.assertIn('worker_id', info)
        self.assertIn('datacenter_id', info)
        self.assertIn('epoch', info)
        self.assertIn('current_timestamp', info)
        self.assertIn('last_timestamp', info)
        self.assertIn('current_sequence', info)
        self.assertIn('max_sequence', info)

    def test_generate_username(self):
        """测试用户名生成"""
        user_id = 123456789
        username = self.generator.generate_username(user_id)
        self.assertEqual(username, f"u{user_id}")


class TestGlobalService(unittest.TestCase):
    """全局服务测试类"""

    def test_init_and_get_service(self):
        """测试初始化和获取服务"""
        # 重置全局服务
        import snowflake_id_generator.snowflake as snowflake_module
        snowflake_module._snowflake_service = None
        
        # 初始化服务
        init_snowflake_service()
        
        # 获取服务
        service = get_snowflake_service()
        self.assertIsInstance(service, SnowflakeService)

    def test_generate_user_id(self):
        """测试生成用户ID"""
        # 重置全局服务
        import snowflake_id_generator.snowflake as snowflake_module
        snowflake_module._snowflake_service = None
        
        # 初始化服务
        init_snowflake_service()
        
        # 生成用户ID
        user_id = generate_user_id()
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)


if __name__ == '__main__':
    unittest.main()

