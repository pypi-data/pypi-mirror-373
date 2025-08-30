from nonebot import on_command, get_driver, on_notice
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, ActionFailed, GroupIncreaseNoticeEvent
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.config import Config
from datetime import datetime
import asyncio
from typing import Dict, Optional

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_time_card",
    description="自动更新机器人在群聊中的昵称并显示实时时间，支持超级管理员开关控制与热重载，所有配置可通过.env文件自定义，错误信息直接反馈至群聊",
    usage="1. 基础功能：插件加载后自动生效，机器人昵称默认格式为「梦&专属机器人 年-月-日 时:分」\n2. 超级管理员命令：\n   - 发送「开关时间昵称」：切换当前群的时间昵称功能（开启/关闭）\n   - 发送「重载时间昵称」：重载插件配置与定时任务（修改.env后生效）\n3. 配置说明：在.env文件中可自定义昵称前缀、后缀、时间格式、更新间隔等参数",
    type="application",
    homepage="https://github.com/MengdeUser/nonebot-plugin-time-card",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# -------------------------- 配置项（支持.env文件修改）--------------------------
class TimeCardConfig(Config):
    time_card_nickname_prefix: str = "梦&专属机器人"  # 时间前昵称
    time_card_nickname_suffix: str = ""              # 时间后昵称
    time_card_time_format: str = "%Y-%m-%d %H:%M"    # 时间格式（年-月-日 时:分）
    time_card_enabled_by_default: bool = True        # 新群默认是否开启功能
    time_card_update_interval: int = 60              # 时间更新间隔（秒）

# 加载配置（优先读取.env文件）
config = TimeCardConfig.parse_obj(get_driver().config)

# -------------------------- 全局变量 --------------------------
# 存储每个群的功能开关状态（key:群号，value:是否开启）
group_enabled: Dict[int, bool] = {}
# 存储定时任务对象（用于重载时停止旧任务）
timer_task_obj: Optional[asyncio.Task] = None

# -------------------------- 工具函数 --------------------------
def get_current_time() -> str:
    """获取当前时间字符串（按配置格式）"""
    return datetime.now().strftime(config.time_card_time_format)

async def update_group_nickname(bot: Bot, group_id: int) -> None:
    """更新单个群的机器人昵称"""
    try:
        # 构建最终昵称：前缀 + 时间 + 后缀
        new_nickname = f"{config.time_card_nickname_prefix} {get_current_time()}{config.time_card_nickname_suffix}"
        # 调用OneBot API修改群昵称
        await bot.set_group_card(
            group_id=group_id,
            user_id=int(bot.self_id),
            card=new_nickname
        )
    except ActionFailed as e:
        # 错误信息发送到对应群聊（不打印终端）
        await bot.send_group_msg(
            group_id=group_id,
            message=f"【时间昵称】修改失败：权限不足或昵称过长（{str(e)}）"
        )
    except Exception as e:
        await bot.send_group_msg(
            group_id=group_id,
            message=f"【时间昵称】更新错误：{str(e)}"
        )

async def run_timer_task(bot: Bot) -> None:
    """定时任务：循环更新所有开启群的昵称"""
    global timer_task_obj
    while True:
        try:
            # 获取机器人加入的所有群
            groups = await bot.get_group_list()
            for group in groups:
                group_id = group["group_id"]
                # 仅更新开启功能的群
                if group_enabled.get(group_id, config.time_card_enabled_by_default):
                    await update_group_nickname(bot, group_id)
        except Exception:
            # 捕获所有错误（不打印终端）
            pass
        # 等待配置的更新间隔
        await asyncio.sleep(config.time_card_update_interval)

def stop_old_timer_task() -> None:
    """停止旧的定时任务（用于重载插件）"""
    global timer_task_obj
    if timer_task_obj and not timer_task_obj.done():
        timer_task_obj.cancel()

# -------------------------- 初始化与事件监听 --------------------------
@get_driver().on_startup
async def startup_init() -> None:
    """机器人启动时初始化"""
    global timer_task_obj
    # 获取第一个OneBot机器人实例
    bots = get_driver().bots
    if not bots:
        return
    
    bot = next(iter(bots.values()))
    # 验证是否为OneBot v11机器人
    if not isinstance(bot, Bot):
        return
    
    # 初始化所有群的开关状态（默认按配置）
    try:
        groups = await bot.get_group_list()
        for group in groups:
            group_id = group["group_id"]
            group_enabled[group_id] = config.time_card_enabled_by_default
    except Exception:
        pass
    
    # 启动定时任务
    timer_task_obj = asyncio.create_task(run_timer_task(bot))

# 监听机器人入群事件（新群自动初始化开关状态）
group_increase_handler = on_notice()
@group_increase_handler.handle()
async def handle_group_increase(bot: Bot, event: GroupIncreaseNoticeEvent) -> None:
    """机器人加入新群时初始化"""
    # 仅处理机器人自身入群事件
    if event.user_id != int(bot.self_id):
        return
    
    group_id = event.group_id
    # 新群默认按配置开启/关闭
    group_enabled[group_id] = config.time_card_enabled_by_default
    # 若默认开启，立即更新一次昵称
    if config.time_card_enabled_by_default:
        await update_group_nickname(bot, group_id)

# -------------------------- 超级管理员命令 --------------------------
# 1. 开关时间昵称功能
toggle_cmd = on_command(
    "开关时间昵称",
    permission=SUPERUSER,
    priority=10,
    block=True
)
@toggle_cmd.handle()
async def handle_toggle(bot: Bot, event: GroupMessageEvent) -> None:
    """切换当前群的功能状态"""
    group_id = event.group_id
    # 切换状态（无记录时按默认值反向）
    current_state = group_enabled.get(group_id, config.time_card_enabled_by_default)
    new_state = not current_state
    group_enabled[group_id] = new_state
    
    if new_state:
        # 开启：立即更新一次昵称
        await update_group_nickname(bot, group_id)
        await toggle_cmd.finish(f"【时间昵称】已开启（每分钟自动更新）")
    else:
        await toggle_cmd.finish(f"【时间昵称】已关闭")

# 2. 重载插件（无需重启Nonebot）
reload_cmd = on_command(
    "重载时间昵称",
    permission=SUPERUSER,
    priority=10,
    block=True
)
@reload_cmd.handle()
async def handle_reload(bot: Bot) -> None:
    """重载插件配置与定时任务"""
    global timer_task_obj
    try:
        # 1. 停止旧的定时任务
        stop_old_timer_task()
        # 2. 重新加载配置（支持.env文件修改后生效）
        config = TimeCardConfig.parse_obj(get_driver().config)
        # 3. 重启定时任务
        timer_task_obj = asyncio.create_task(run_timer_task(bot))
        # 4. 立即更新所有开启群的昵称
        groups = await bot.get_group_list()
        for group in groups:
            group_id = group["group_id"]
            if group_enabled.get(group_id, config.time_card_enabled_by_default):
                await update_group_nickname(bot, group_id)
        await reload_cmd.finish(f"【时间昵称】插件已重载（配置与定时任务已更新）")
    except Exception as e:
        await reload_cmd.finish(f"【时间昵称】重载失败：{str(e)}")