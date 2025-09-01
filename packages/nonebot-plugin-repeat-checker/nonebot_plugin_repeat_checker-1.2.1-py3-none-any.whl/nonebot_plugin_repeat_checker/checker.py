from nonebot import on_message, logger
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from .utils import (
    extract_message_content,
    is_similar,
    should_check_group,
    calculate_ban_duration
)


class RepeatChecker:
    """复读检测器"""

    def __init__(self, database, config):
        self.database = database
        self.config = config

    async def check_repeat_message(self, bot: Bot, event: GroupMessageEvent):
        """检查复读消息"""
        group_id = str(event.group_id)
        user_id = str(event.user_id)

        if self.config.repeat_checker_debug:
            logger.info(f"接收到群消息: 群 {group_id}, 用户 {user_id}, 原始消息: {event.message}")

        # 检查是否应该在该群启用检测
        if not should_check_group(
                event.group_id,
                self.config.repeat_checker_group_mode,
                self.config.repeat_checker_group_list
        ):
            if self.config.repeat_checker_debug:
                logger.info(f"群 {group_id} 不在检测范围内，跳过")
            return

        # 提取消息内容
        message_content = extract_message_content(
            event.message,
            self.config.repeat_checker_enable_image_check
        )

        if not message_content:
            if self.config.repeat_checker_debug:
                logger.info(f"群 {group_id} 消息内容为空，跳过处理")
            return

        if self.config.repeat_checker_debug:
            logger.info(f"群 {group_id} 用户 {user_id} 处理后消息: '{message_content}'")

        # 获取群组信息
        group_info = await self.database.get_group_info(group_id)

        if not group_info:
            # 初始化群组信息 - 第一条消息算作出现1次
            await self.database.update_group_info(
                group_id,
                last_message_content=message_content,
                last_repeater_id=None,
                repeat_count=1
            )
            if self.config.repeat_checker_debug:
                logger.info(f"初始化群 {group_id} 信息，首次消息: '{message_content}'")
            return

        # 检查是否为相似消息
        last_content = group_info.get("last_message_content", "")
        current_repeat_count = group_info.get("repeat_count", 0)
        last_repeater_id = group_info.get("last_repeater_id")

        if self.config.repeat_checker_debug:
            logger.info(f"群 {group_id} 对比消息:")
            logger.info(f"  上次内容: '{last_content}'")
            logger.info(f"  当前内容: '{message_content}'")
            logger.info(f"  当前复读次数: {current_repeat_count}")
            logger.info(f"  上次复读者: {last_repeater_id}")

        is_repeat = is_similar(
            message_content,
            last_content,
            self.config.repeat_checker_similarity_threshold
        )

        if self.config.repeat_checker_debug:
            logger.info(f"群 {group_id} 相似度检测结果: {is_repeat}")

        if is_repeat:
            # 是复读消息 - 增加计数
            new_count = current_repeat_count + 1
            await self.database.update_group_info(
                group_id,
                last_message_content=last_content,  # 保持原内容
                last_repeater_id=user_id,
                repeat_count=new_count
            )

            if self.config.repeat_checker_debug:
                logger.info(f"群 {group_id} 检测到复读，次数: {new_count}，复读者: {user_id}")

        else:
            # 不是复读消息 - 先检查是否需要禁言，然后重置
            if self.config.repeat_checker_debug:
                logger.info(f"群 {group_id} 复读结束，检查是否需要禁言")
                logger.info(f"  复读次数: {current_repeat_count}, 阈值: {self.config.repeat_checker_repeat_threshold}")
                logger.info(f"  最后复读者: {last_repeater_id}")

            if (current_repeat_count >= self.config.repeat_checker_repeat_threshold
                    and last_repeater_id):

                if self.config.repeat_checker_debug:
                    logger.info(f"群 {group_id} 满足禁言条件，准备禁言用户 {last_repeater_id}")

                await self._ban_user(bot, group_id, last_repeater_id, current_repeat_count)
            else:
                if self.config.repeat_checker_debug:
                    if current_repeat_count < self.config.repeat_checker_repeat_threshold:
                        logger.info(f"群 {group_id} 复读次数不足，无需禁言")
                    elif not last_repeater_id:
                        logger.info(f"群 {group_id} 无最后复读者，无需禁言")

            # 重置群组信息为新消息
            await self.database.reset_group_repeat_info(group_id, user_id, message_content)

            if self.config.repeat_checker_debug:
                logger.info(f"群 {group_id} 重置复读信息，新消息: '{message_content}'")

    async def _ban_user(self, bot: Bot, group_id: str, user_id: str, repeat_count: int):
        """禁言用户"""
        try:
            # 增加用户禁言次数
            ban_count = await self.database.increment_user_ban_count(group_id, user_id)

            # 计算禁言时长
            ban_duration = calculate_ban_duration(
                self.config.repeat_checker_silence_duration,
                repeat_count,
                ban_count
            )

            # 执行禁言
            await bot.set_group_ban(
                group_id=int(group_id),
                user_id=int(user_id),
                duration=ban_duration
            )

            if self.config.repeat_checker_debug:
                logger.info(
                    f"禁言用户成功: 群 {group_id}, 用户 {user_id}, "
                    f"复读次数 {repeat_count}, 累计禁言次数 {ban_count}, "
                    f"禁言时长 {ban_duration}秒"
                )

        except ActionFailed as e:
            logger.warning(f"禁言用户失败: 群 {group_id}, 用户 {user_id}, 错误: {e}")
        except Exception as e:
            logger.error(f"禁言用户异常: 群 {group_id}, 用户 {user_id}, 错误: {e}")


# 全局变量，将在模块导入后初始化
checker = None


def initialize_checker(database, config):
    """初始化检测器"""
    global checker
    checker = RepeatChecker(database, config)


# 注册消息处理器 - 只处理群消息
repeat_checker = on_message(
    priority=10,
    block=False
)


@repeat_checker.handle()
async def handle_repeat_check(bot: Bot, event: GroupMessageEvent):
    """处理复读检测 - 只处理群消息"""
    # 确保只处理群消息
    if not isinstance(event, GroupMessageEvent):
        return

    if checker is None:
        logger.warning("检测器未初始化，跳过处理")
        return
    await checker.check_repeat_message(bot, event)
