from pydantic import BaseModel, Field
from nonebot import get_driver

class Config(BaseModel):
    time_card_nickname_prefix: str = Field(default="梦&专属机器人", description="时间昵称前缀")
    time_card_nickname_suffix: str = Field(default="", description="时间昵称后缀")
    time_card_time_format: str = Field(default="%Y-%m-%d %H:%M", description="时间显示格式")
    time_card_enabled_by_default: bool = Field(default=True, description="新群默认开启状态")
    time_card_update_interval: int = Field(default=60, description="更新间隔（秒）")

# 初始化配置（兼容所有 Nonebot 版本）
config = Config(**get_driver().config.dict())