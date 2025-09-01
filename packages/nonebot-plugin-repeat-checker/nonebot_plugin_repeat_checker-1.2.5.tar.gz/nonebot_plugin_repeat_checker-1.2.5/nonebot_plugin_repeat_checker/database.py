import aiosqlite
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from nonebot import logger, get_plugin_config, require
require("nonebot_plugin_localstore")
from nonebot_plugin_localstore import get_plugin_data_dir

from .config import Config


class RepeatDatabase:
    """复读检测数据库操作类"""

    def __init__(self, config: Config):
        self.config = config
        self.db_path = get_plugin_data_dir() / "data.db"
        self._ensure_db_dir()

    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        if self.config.repeat_checker_debug:
            logger.info(f"数据库路径: {self.db_path}")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def init_database(self):
        """初始化数据库表结构"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS group_repeat_info (
                    group_id TEXT PRIMARY KEY,
                    last_message_content TEXT,
                    last_repeater_id TEXT,
                    repeat_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_ban_count (
                    group_id TEXT,
                    user_id TEXT,
                    ban_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (group_id, user_id)
                )
            ''')

            await db.commit()

            if self.config.repeat_checker_debug:
                logger.info("数据库初始化完成")

    @asynccontextmanager
    async def get_db_connection(self):
        """获取数据库连接的异步上下文管理器"""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            yield conn

    async def get_group_info(self, group_id: str) -> Optional[Dict[str, Any]]:
        """获取群组复读信息"""
        async with self.get_db_connection() as conn:
            cursor = await conn.execute(
                'SELECT * FROM group_repeat_info WHERE group_id = ?',
                (group_id,)
            )
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def update_group_info(self, group_id: str, **kwargs):
        """更新群组复读信息"""
        async with self.get_db_connection() as conn:
            await conn.execute(
                '''INSERT OR REPLACE INTO group_repeat_info 
                   (group_id, last_message_content, last_repeater_id, repeat_count, updated_at) 
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                (group_id,
                 kwargs.get('last_message_content'),
                 kwargs.get('last_repeater_id'),
                 kwargs.get('repeat_count', 0))
            )
            await conn.commit()

    async def get_user_ban_count(self, group_id: str, user_id: str) -> int:
        """获取用户禁言次数"""
        async with self.get_db_connection() as conn:
            cursor = await conn.execute(
                'SELECT ban_count FROM user_ban_count WHERE group_id = ? AND user_id = ?',
                (group_id, user_id)
            )
            row = await cursor.fetchone()
            return row['ban_count'] if row else 0

    async def increment_user_ban_count(self, group_id: str, user_id: str) -> int:
        """增加用户禁言次数"""
        async with self.get_db_connection() as conn:
            await conn.execute(
                '''INSERT OR REPLACE INTO user_ban_count 
                   (group_id, user_id, ban_count, updated_at) 
                   VALUES (?, ?, COALESCE((SELECT ban_count FROM user_ban_count WHERE group_id = ? AND user_id = ?), 0) + 1, CURRENT_TIMESTAMP)''',
                (group_id, user_id, group_id, user_id)
            )
            await conn.commit()

            # 获取更新后的次数
            cursor = await conn.execute(
                'SELECT ban_count FROM user_ban_count WHERE group_id = ? AND user_id = ?',
                (group_id, user_id)
            )
            row = await cursor.fetchone()
            return row['ban_count'] if row else 1

    async def reset_group_repeat_info(self, group_id: str, user_id: str, new_content: str):
        """重置群组复读信息"""
        await self.update_group_info(
            group_id,
            last_message_content=new_content,
            last_repeater_id=user_id,
            repeat_count=0
        )


# 创建数据库实例的工厂函数
def create_database() -> RepeatDatabase:
    """创建数据库实例"""
    config = get_plugin_config(Config)
    return RepeatDatabase(config)
