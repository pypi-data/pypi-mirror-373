from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require
require("nonebot_plugin_localstore")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")

from nonebot.permission import SUPERUSER
from . import config, api, data
import random
import time

from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.uniseg import Image, At, UniMessage
from nonebot_plugin_uninfo import UniSession, Session

__plugin_meta__ = PluginMetadata(
    name="蔚蓝档案今日运势",
    description="《蔚蓝档案》今日运势插件，支持多平台",
    usage="直接发送 今日运势",
    type="application",
    homepage="https://github.com/captain-wangrun-cn/nonebot-plugin-bafortune",
    config=config.Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
)

def get_date() -> str:
    """获取当日日期"""
    return time.strftime("%Y-%m-%d", time.localtime())

reload_image_list = on_alconna("刷新今日运势图片列表", use_cmd_start=True, permission=SUPERUSER)
@reload_image_list.handle()
async def _():
    await api.refresh_local_image_list()
    await reload_image_list.finish("已刷新本地今日运势图片列表！")

refresh_jrys = on_alconna("刷新全局今日运势", use_cmd_start=True, permission=SUPERUSER)
@refresh_jrys.handle()
async def _():
    data.delete_all_jrys_data()
    await refresh_jrys.finish("已刷新全局今日运势！")

perm = None
if not config.allow_refresh_jrys:
    perm = SUPERUSER
refresh_jrys_self = on_alconna("刷新今日运势", use_cmd_start=True, permission=perm)
@refresh_jrys_self.handle()
async def _(session: Session = UniSession()):
    uid = session.user.id
    data.delete_jrys_data(uid)
    await refresh_jrys_self.finish(f"已刷新你的今日运势！")

bafortune = on_alconna("今日运势", aliases={"jrys","ba运势","bajrys","ba今日运势","蔚蓝档案今日运势"})
@bafortune.handle()
async def _(session: Session = UniSession()):
    uid = session.user.id
    fortune_data = data.read_data(uid)

    if (fortune_data and fortune_data.get("date", "") == get_date()) or (fortune_data and not config.auto_refresh_jrys):
        # 有数据且数据是今天的 或 有数据且关闭自动刷新
        star_num = fortune_data.get("star",0)
    else:
        # 定义星数及其对应的权重，星数越高权重越低
        weights = [0.1, 0.15, 0.2, 0.25, 0.15, 0.12, 0.07, 0.005]
        # 使用 random.choices 根据权重选择一个星数
        star_num = random.choices(range(8), weights=weights, k=1)[0]
        data.write_data(uid, {"star": star_num, "date": get_date()})

    # 组成星星字符串
    star = ["☆","☆","☆","☆","☆","☆","☆"]
    for i in range(star_num):
        star[i] = "★"
    star = "".join(star)

    # 获取图片
    image = None
    if config.api == "wr":
        image_url = await api.get_image_wr_api()
        if image_url:
            image = Image(raw=await api.url2base64(image_url))
    elif config.api == "lolicon":
        image_url = await api.get_image_lolicon_api()
        if image_url:
            image = Image(raw=await api.url2base64(image_url))

    if config.api == "local":
        image_data = await api.get_image_local()
        image = Image(raw=image_data)
    elif config.api == "custom":
        custom_image = await api.get_image_custom_api()
        if isinstance(custom_image, bytes):
            image = Image(raw=custom_image)
        elif isinstance(custom_image, str):
            image = Image(url=custom_image)
        else:
            image = None

    jrys_msg = f"{config.messages['title'][star_num]}\n{config.messages['data'][star_num]}\n{star}"
    if config.jrys_extra_message:
        jrys_msg += f"\n{config.jrys_extra_message}"
    msg = UniMessage(At("user", uid) + f"的今日运势：\n\n{jrys_msg}\n")
    if not config.i_sure_not_to_use_image and image:
        msg += UniMessage(image)

    await bafortune.send(await msg.export())
