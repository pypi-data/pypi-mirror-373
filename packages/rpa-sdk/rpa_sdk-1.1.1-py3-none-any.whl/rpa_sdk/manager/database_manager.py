"""
数据库管理器模块
提供全局数据库连接管理和业务方法
"""

from typing import Optional, Dict, Any
from ..kit.MySql import DatabaseManager as MySqlDatabaseManager
from ..kit.Utils import Logger


class DatabaseManager:
    """全局数据库管理器单例"""
    _instance: Optional['DatabaseManager'] = None
    _db_manager: Optional[MySqlDatabaseManager] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, db_config: Dict[str, Any]) -> bool:
        """
        初始化数据库连接
        
        Args:
            db_config: 数据库配置字典，包含host, port, user, password, database
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            self._db_manager = MySqlDatabaseManager(
                host=db_config['host'],
                port=int(db_config['port']),
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            
            # 测试连接
            with self._db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    
            Logger.info(f"数据库连接初始化成功: {db_config['host']}:{db_config['port']}/{db_config['database']}")
            return True
            
        except Exception as e:
            Logger.error(f"数据库连接初始化失败: {e}")
            self._db_manager = None
            return False
    
    def get_db_manager(self) -> Optional[MySqlDatabaseManager]:
        """获取数据库管理器实例"""
        return self._db_manager
    
    def is_initialized(self) -> bool:
        """检查数据库是否已初始化"""
        return self._db_manager is not None
    
    def close(self) -> None:
        """关闭数据库连接"""
        # MySqlDatabaseManager不需要显式关闭，因为它使用上下文管理器
        # 这里只是提供一个空实现以满足接口要求
        pass
    
    # 业务方法封装
    def get_region(self, area_id: str) -> Optional[str]:
        """获取区域名称"""
        if not self.is_initialized():
            Logger.warning("数据库未初始化，无法查询区域信息")
            return None
        try:
            return self._db_manager.get_region(area_id)
        except Exception as e:
            Logger.error(f"查询区域失败: {e}")
            return None
    
    def get_doctor(self, area_name: str) -> Optional[str]:
        """获取医生信息"""
        if not self.is_initialized():
            Logger.warning("数据库未初始化，无法查询医生信息")
            return None
        try:
            return self._db_manager.get_doctor(area_name)
        except Exception as e:
            Logger.error(f"查询医生失败: {e}")
            return None
    
    def get_abo_hr(self, physical_id: str) -> tuple:
        """获取血型信息"""
        if not self.is_initialized():
            Logger.warning("数据库未初始化，无法查询血型信息")
            return None, None
        try:
            return self._db_manager.get_abo_hr(physical_id)
        except Exception as e:
            Logger.error(f"查询血型失败: {e}")
            return None, None
    
    def update_tag(self, table_name: str, key_field: str, key_value: str, tag: str) -> bool:
        """更新标签"""
        if not self.is_initialized():
            Logger.warning("数据库未初始化，无法更新标签")
            return False
        try:
            affected_rows = self._db_manager.update_tag(table_name, key_field, key_value, tag)
            return affected_rows > 0
        except Exception as e:
            Logger.error(f"更新标签失败: {e}")
            return False

    def get_referral_reason(self, idcard: str, date: str, disease_type: str) -> Optional[str]:
        """获取转诊原因"""
        if not self.is_initialized():
            Logger.warning("数据库未初始化，无法查询转诊原因")
            return None
        try:
            return self._db_manager.get_referral_reason(idcard, date, disease_type)
        except Exception as e:
            Logger.error(f"查询转诊原因失败: {e}")
            return None


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    return db_manager