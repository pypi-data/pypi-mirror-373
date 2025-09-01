from nonebot import get_plugin_config, get_driver
from nonebot.plugin import PluginMetadata
from nonebot import logger

from .config import Config
from .database import create_database
from .checker import initialize_checker

# 获取插件配置
plugin_config = get_plugin_config(Config)
# 创建数据库实例
database = create_database()


__plugin_meta__ = PluginMetadata(
    name="禁止复读",
    description="智能检测群聊中的复读行为，并对最后一位复读的成员进行禁言。支持文本、图片及混合消息的相似度检测。",
    usage="""
▶️ 插件加载后自动生效，无需命令。

**📖 工作原理**
插件会记录群聊中的消息，当检测到连续N条（可配置）相同或高度相似的消息时，将对最后一位发送该消息的群成员执行禁言操作。

**✨ 功能特性**
- **智能检测**: 不仅限于完全相同的消息，支持通过文本相似度算法识别“高仿”复读。
- **图片支持**: 能够检测并处理图片复读。
- **动态禁言**: 禁言时长会根据用户的复读次数累积增加。
- **灵活控制**: 可通过白名单/黑名单模式指定插件生效的群聊。
- **高度可配**: 可自定义触发复读的次数、禁言时长、相似度阈值等。

**⚙️ 配置项**
所有配置项都以 `repeat_checker_` 开头，请在 `.env.*` 文件中进行设置：

- `repeat_checker_repeat_threshold`:
  - **说明**: 触发禁言的最小复读次数。
  - **默认值**: `2`

- `repeat_checker_silence_duration`:
  - **说明**: 基础禁言时长（单位：秒）。
  - **默认值**: `3600`

- `repeat_checker_similarity_threshold`:
  - **说明**: 文本相似度阈值，用于判断是否为复读（范围 0.0-1.0）。
  - **默认值**: `0.8`

- `repeat_checker_enable_image_check`:
  - **说明**: 是否启用图片复读检测。
  - **默认值**: `True`

- `repeat_checker_group_mode`:
  - **说明**: 群组控制模式，`"blacklist"` (黑名单) 或 `"whitelist"` (白名单)。
  - **默认值**: `"blacklist"`

- `repeat_checker_group_list`:
  - **说明**: 群组ID列表，与 `group_mode` 配合使用。
  - **示例**: `[123456, 654321]`

- `repeat_checker_debug`:
  - **说明**: 是否开启调试日志，方便排查问题。
  - **默认值**: `False`
""",
    type="application",
    homepage="https://github.com/SuperWaterGod/nonebot-plugin-repeat-checker",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "SuperWaterGod",
        "license": "AGPL-3.0",
        "version": "1.2.5",
    },
)

# 获取驱动器，用于初始化
driver = get_driver()


# 在 NoneBot 启动时初始化插件
@driver.on_startup
async def startup():
    # 初始化数据库
    await database.init_database()
    # 初始化检测器
    initialize_checker(database, plugin_config)
    logger.info("复读检测插件初始化完成")


__all__ = ["plugin_config", "database"]
