from typing import Literal
from pydantic import BaseModel
from nonebot import get_plugin_config
from nonebot.log import logger

class Config(BaseModel):
    bafortune_api: Literal["wr","lolicon","local","none","custom"] = "none"
    bafortune_jrys_titles: list[str] = ["凶", "稳", "顺", "大顺", "小吉", "吉", "大吉", "运"]
    bafortune_jrys_messages: list[str] = [
        "长夜再暗，火种仍在，转机终会到来。",
        "微光不灭，步步向前，黎明就在眼前。",
        "心怀希冀，顺流而行，好事悄然靠近。",
        "逆境翻篇，机遇迎面，惊喜不期而至。",
        "小吉随身，难题化易，幸运与你并肩。",
        "吉星高照，所行皆坦，所愿皆如愿。",
        "福泽深厚，大吉加身，一路花开有声。",
        "七星同耀，奇迹频现，今日万事皆成。"
    ]
    bafortune_allow_refresh_jrys: bool = False
    bafortune_jrys_extra_message: str = ""
    bafortune_auto_refresh_jrys: bool = True
    bafortune_proxy: str = ""
    bafortune_i_sure_not_to_use_image: bool = False

config = get_plugin_config(Config)
api = config.bafortune_api
jrys_extra_message = config.bafortune_jrys_extra_message
proxy = config.bafortune_proxy
allow_refresh_jrys = config.bafortune_allow_refresh_jrys
auto_refresh_jrys = config.bafortune_auto_refresh_jrys
i_sure_not_to_use_image = config.bafortune_i_sure_not_to_use_image

messages = {
    "title": config.bafortune_jrys_titles,
    "data": config.bafortune_jrys_messages,
    "extra_message": config.bafortune_jrys_extra_message
}

if api == "none":
    if not i_sure_not_to_use_image:
        # 即不确认不用图片，也不设置api
        msg = """
蔚蓝档案今日运势
        
未选择图片API！（图片获取方式）
⚠⚠⚠本次插件将只会发送文字，不会发送图片！⚠⚠⚠
（配置项 bafortune_api）

要么：
    从三种方式中选择一个
    - wr：插件作者本人自己的蔚蓝档案图片API
    - lolicon：lolicon api
    - local：本地图片（需要配置路径）
    bafortune_api=你选择的api

要么：
    确认不用图片，只发送文字（配置项 bafortune_i_sure_not_to_use_image=true）

若有能力者需要使用自己的api，可修改文件 api.py 中的 get_image_custom_api 函数，并配置 bafortune_api 为 custom。

详细请看插件主页：
https://github.com/captain-wangrun-cn/nonebot-plugin-bafortune
"""
        logger.warning(msg)
