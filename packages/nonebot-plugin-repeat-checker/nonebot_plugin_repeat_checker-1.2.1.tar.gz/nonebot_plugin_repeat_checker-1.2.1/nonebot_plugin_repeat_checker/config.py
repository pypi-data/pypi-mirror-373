from typing import List, Literal
from pydantic import BaseModel


class Config(BaseModel):
    # 基础禁言时长（秒）
    repeat_checker_silence_duration: int = 3600  # 60 * 60

    # 相似度阈值
    repeat_checker_similarity_threshold: float = 0.8

    # 最小复读次数（达到此次数才会触发禁言）
    repeat_checker_repeat_threshold: int = 2

    # 是否启用图片复读检测
    repeat_checker_enable_image_check: bool = True

    # 是否启用调试日志
    repeat_checker_debug: bool = False

    # 禁止复读模式的群组控制策略（whitelist/blacklist）
    repeat_checker_group_mode: Literal["whitelist", "blacklist"] = "blacklist"

    # 白名单/黑名单群号列表
    repeat_checker_group_list: List[int] = []
