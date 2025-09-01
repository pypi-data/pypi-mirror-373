import re
import difflib
from typing import Optional
from unidecode import unidecode
from nonebot.adapters.onebot.v11 import Message


def clean_message_content(content: str) -> str:
    """清理消息内容，去除控制字符"""
    if not content:
        return ""

    # 使用正则表达式去除控制字符
    content = re.sub(
        r'[\x00-\x1F\x7F-\x9F\u202A\u202B\u202C\u200B-\u200F\u2060\uFEFF]+',
        '',
        content
    )

    # 使用 unidecode 进行字符转换
    try:
        content = unidecode(content)
    except Exception:
        # 如果转换失败，保持原内容
        pass

    return content.strip()


def is_similar(str1: str, str2: str, threshold: float = 0.8) -> bool:
    """检查两个字符串是否相似"""
    if not str1 or not str2:
        return False

    if str1 == str2:
        return True

    # 使用 difflib 计算相似度
    similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
    return similarity >= threshold


def extract_message_content(message: Message, enable_image_check: bool = True) -> Optional[str]:
    """提取消息内容"""
    if not message:
        return None

    content_parts = []

    for segment in message:
        if segment.type == "text":
            text_content = clean_message_content(segment.data.get("text", ""))
            if text_content:
                content_parts.append(text_content)

        elif segment.type == "image" and enable_image_check:
            # 处理图片消息
            image_url = segment.data.get("url", "")
            image_file = segment.data.get("file", "")

            # 优先使用 file 字段作为图片标识
            image_id = image_file if image_file else image_url
            if image_id:
                content_parts.append(f"[图片:{image_id}]")

        elif segment.type == "face":
            # 处理表情
            face_id = segment.data.get("id", "")
            if face_id:
                content_parts.append(f"[表情:{face_id}]")

        elif segment.type == "at":
            # 处理@消息 - 但不影响复读检测
            pass

        # 可以添加更多类型的处理
        elif segment.type in ["reply", "forward"]:
            # 跳过回复和转发消息的特殊标记
            pass

    result = " ".join(content_parts).strip() if content_parts else None

    # 如果没有提取到任何内容，但消息不为空，可能是纯 @ 或其他特殊消息
    if not result and len(message) > 0:
        # 对于纯文本但被清理为空的情况，返回 None
        return None

    return result


def should_check_group(group_id: int, group_mode: str, group_list: list) -> bool:
    """检查是否应该在该群启用复读检测"""
    if group_mode == "whitelist":
        return group_id in group_list
    elif group_mode == "blacklist":
        return group_id not in group_list
    else:
        # 默认启用
        return True


def calculate_ban_duration(
        base_duration: int,
        repeat_count: int,
        ban_count: int
) -> int:
    """计算禁言时长"""
    # 禁言时长 = 基础时长 × 复读次数 × 被禁言次数
    duration = base_duration * max(1, repeat_count) * max(1, ban_count)

    # 限制最大禁言时长（30天）
    max_duration = 30 * 24 * 60 * 60  # 30天
    return min(duration, max_duration)