import datetime
from nonebot import CommandGroup, export, logger
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.adapters.cqhttp.permission import GROUP
from omega_miya.utils.Omega_plugin_utils import init_export, init_permission_state
from .utils import maybe, sp,  sp_event
from .oldalmanac import old_almanac


# Custom plugin usage text
__plugin_name__ = '求签'
__plugin_usage__ = r'''【求签】
求签, 求运势, 包括且不限于抽卡、吃饭、睡懒觉、DD
每个人每天求同一个东西的结果是一样的啦!
不要不信邪重新抽啦!
仅限群聊使用

**Permission**
Command & Lv.10
or AuthNode

**AuthNode**
basic

**Usage**
/求签 [所求之事]
/DD老黄历'''

# 声明本插件可配置的权限节点
__plugin_auth_node__ = [
    'basic'
]

# Init plugin export
init_export(export(), __plugin_name__, __plugin_usage__, __plugin_auth_node__)

# 注册事件响应器
Maybe = CommandGroup(
    'maybe',
    # 使用run_preprocessor拦截权限管理, 在default_state初始化所需权限
    state=init_permission_state(
        name='maybe',
        command=True,
        level=10,
        auth_node='basic'),
    permission=GROUP,
    priority=10,
    block=True)

luck = Maybe.command('luck', aliases={'求签'})


# 修改默认参数处理
@luck.args_parser
async def parse(bot: Bot, event: GroupMessageEvent, state: T_State):
    args = str(event.get_plaintext()).strip().lower().split()
    if not args:
        await luck.reject('你似乎没有发送有效的参数呢QAQ, 请重新发送:')
    state[state["_current_key"]] = args[0]
    if state[state["_current_key"]] == '取消':
        await luck.finish('操作已取消')


@luck.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent, state: T_State):
    args = str(event.get_plaintext()).strip().lower().split()
    if not args:
        pass
    elif args and len(args) == 1:
        state['draw'] = args[0]
    else:
        await luck.finish('参数错误QAQ')


@luck.got('draw', prompt='你想问什么事呢?')
async def handle_luck(bot: Bot, event: GroupMessageEvent, state: T_State):
    user_id = event.user_id
    _draw = state['draw']
    # 求签者昵称, 优先使用群昵称
    draw_user = event.sender.card
    if not draw_user:
        draw_user = event.sender.nickname

    # 判断特殊事件
    if _draw in sp.keys():
        draw_result = sp_event(_draw)
    else:
        draw_result = maybe(draw=_draw, user_id=user_id)

    # 向用户发送结果
    today = datetime.date.today().strftime('%Y年%m月%d日')
    msg = f'今天是{today}\n{draw_user}{draw_result}'
    await luck.finish(msg)


almanac = Maybe.command('almanac', aliases={'DD老黄历', 'dd老黄历'})


@almanac.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent, state: T_State):
    args = str(event.get_plaintext()).strip().lower().split()
    if not args:
        pass
    else:
        await almanac.finish('参数错误QAQ')

    user_id = event.user_id

    # 求签者昵称, 优先使用群昵称
    draw_user = event.sender.card
    if not draw_user:
        draw_user = event.sender.nickname

    draw_result = old_almanac(user_id=user_id)

    # 向用户发送结果
    today = datetime.date.today().strftime('%Y年%m月%d日')
    msg = f"今天是{today}\n{draw_user}今日:\n{'='*12}\n{draw_result}"
    await almanac.finish(msg)
