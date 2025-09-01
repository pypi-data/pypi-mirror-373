<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-repeat-checker

_✨ 适用于 NoneBot2 的群复读检测与禁言插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/SuperWaterGod/nonebot-plugin-repeat-checker.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-repeat-checker">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-repeat-checker.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

智能检测群聊中的复读行为，并对最后一位复读的成员进行禁言。支持文本、图片及混合消息的相似度检测。

## 📖 介绍

功能介绍

- 📦 开箱即用，轻松集成到 NoneBot2 项目中

- 🚫 自动检测复读行为并禁言最后复读者

- 🖼️ 支持文本和图片消息的复读检测

- 🧹 智能消息清理，处理特殊字符和控制字符

- 💾 Sqlite轻量化数据存储


## 💿 安装
> [!IMPORTANT]
> 必须安装依赖包
> ```bash
>   pip install aiosqlite unidecode
> ```

<details open>
<summary>手动安装</summary>

1. 将整个 `nonebot-plugin-repeat-checker` 文件夹放置到你的 NoneBot2 项目的 `plugins` 目录下

2. 重启你的 NoneBot2 机器人

</details>

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-repeat-checker

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-repeat-checker
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-repeat-checker
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-repeat-checker
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-repeat-checker
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_repeat_checker"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的配置项

或者在 `config.py` 中可以调整以下配置：


| 配置项 | 必填 | 默认值 | 说明 |
|--------|----|--------|------|
| `repeat_checker_silence_duration` | 否  | 3600 | 基础禁言时长（秒） |
| `repeat_checker_similarity_threshold` |  否 | 0.8 | 消息相似度阈值（0-1） |
| `repeat_checker_repeat_threshold` |  否 | 2 | 触发禁言的最小复读次数 |
| `repeat_checker_enable_image_check` |  否 | True | 是否启用图片复读检测 |
| `repeat_checker_debug` |  否 | False | 是否启用调试模式 |
| `repeat_checker_group_mode` |  否 | "blacklist" | 群组控制模式（whitelist/blacklist） |
| `repeat_checker_group_list` |  否  | [] | 白名单/黑名单群号列表 |消息相似度阈值（0-1） |


## 目录结构

```
./nonebot_plugin_repeat_checker/
├── __init__.py            # 主入口文件
├── config.py              # 配置管理
├── database.py            # 数据存储管理
├── checker.py             # 消息处理
├── utils.py               # 工具函数
└── README.md              # 说明文档
```


## 使用说明

### 群组控制

插件支持白名单/黑名单模式来控制在哪些群组启用功能：

- **blacklist模式（默认）**：除了在黑名单中的群组外，其他所有群组都启用复读检测
- **whitelist模式**：只有在白名单中的群组才启用复读检测

配置示例：
```python
# 黑名单模式：禁用群组123456和789012的复读检测
repeat_checker_group_mode = "blacklist"
repeat_checker_group_list = [123456, 789012]

# 白名单模式：只在群组111111和222222启用复读检测
repeat_checker_group_mode = "whitelist" 
repeat_checker_group_list = [111111, 222222]
```

### 自动功能

插件会自动监控群聊消息，当检测到复读行为时：

1. **检测条件**：当连续消息相似度达到阈值时认为是复读
2. **触发禁言**：复读次数达到设定值且有新的不同消息时，禁言最后一个复读者
3. **禁言时长**：`基础时长 × 复读次数 × 该用户历史被禁言次数`


## 工作原理

1. **消息处理**：
   - 清理控制字符和特殊符号
   - 使用 `unidecode` 转换特殊字符
   - 对图片消息提取标识符

2. **相似度检测**：
   - 使用 `difflib.SequenceMatcher` 计算消息相似度
   - 可配置相似度阈值

3. **禁言逻辑**：
   - 记录每个群组的复读状态
   - 累计用户的被禁言次数
   - 动态计算禁言时长

4. **数据存储**：
   - 使用 SQLite 数据库持久化数据
   - 线程安全的数据库操作
   - 自动创建数据目录和表结构

5. **群组控制**：
   - 支持白名单/黑名单模式
   - 灵活控制插件在不同群组的启用状态

## 数据库结构

### group_repeat_info 表
- `group_id`: 群组ID（主键）
- `last_message_content`: 最后一条消息内容
- `last_repeater_id`: 最后复读者ID
- `repeat_count`: 当前复读次数
- `created_at`: 创建时间
- `updated_at`: 更新时间

### user_ban_count 表
- `group_id`: 群组ID（主键）
- `user_id`: 用户ID（主键）
- `ban_count`: 禁言次数
- `created_at`: 创建时间
- `updated_at`: 更新时间


## 注意事项

1. **权限要求**：机器人需要有群管理员权限才能执行禁言操作
2. **数据安全**：插件会自动处理数据库读写错误，使用事务确保数据一致性
3. **性能考虑**：使用SQLite数据库和线程锁保证并发安全
4. **群组控制**：合理配置群组白名单/黑名单，避免在不需要的群组启用功能

## 更新日志

### v1.2.0
- 使用 `localstore` 插件
- 删除非必要驱动器依赖

### v1.1.0
- 按照Nonebot2插件规范修改

### v1.0.0
- 重构为标准 NoneBot2 插件结构
- 使用Sqlite数据库存储数据
- 支持图片复读检测
- 添加群组白名单/黑名单功能
- 优化消息处理逻辑

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个插件！

## 许可证

本项目使用 AGPL-3.0 许可证。