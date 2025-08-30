from pydantic import BaseModel, Field  # 改用 Pydantic 基础模型
from nonebot import get_driver

# 插件配置类（继承自 Pydantic BaseModel，而非 Nonebot BaseConfig）
class Config(BaseModel):
    """time_card 插件配置类，支持从 .env 文件读取配置"""

    # 1. 时间昵称前缀（默认：梦&专属机器人）
    time_card_nickname_prefix: str = Field(
        default="梦&专属机器人",
        description="时间昵称的前缀内容，显示在时间前面"
    )

    # 2. 时间昵称后缀（默认：空字符串）
    time_card_nickname_suffix: str = Field(
        default="",
        description="时间昵称的后缀内容，显示在时间后面（可留空）"
    )

    # 3. 时间显示格式（默认：年-月-日 时:分）
    time_card_time_format: str = Field(
        default="%Y-%m-%d %H:%M",
        description="时间格式化字符串（遵循 Python datetime 格式规范）"
    )

    # 4. 新群默认是否开启功能（默认：开启）
    time_card_enabled_by_default: bool = Field(
        default=True,
        description="机器人新加入群聊时，是否默认开启时间昵称功能"
    )

    # 5. 时间更新间隔（单位：秒，默认：60秒）
    time_card_update_interval: int = Field(
        default=60,
        description="时间昵称的自动更新间隔（建议 ≥30 秒，避免频繁调用API）"
    )

# 初始化配置实例（从 Nonebot 驱动中读取 .env 配置，逻辑不变）
config = Config(**get_driver().config.dict())