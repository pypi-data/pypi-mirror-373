# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_bafortune']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.27.0,<0.28.0',
 'nonebot-adapter-onebot>=2.0.0,<3.0.0',
 'nonebot-plugin-alconna>=0.46.3',
 'nonebot-plugin-localstore>=0.7.3,<0.8.0',
 'nonebot-plugin-uninfo>=0.6.1',
 'nonebot2>=2.2.0,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-bafortune',
    'version': '1.0.7',
    'description': '蔚蓝档案今日运势插件, BlueArchive fortune plugin',
    'long_description': '<div align="center">\n  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>\n  <img src="https://github.com/captain-wangrun-cn/wr-nonebot-plugin-template/blob/resources/wr_avatar.jpg" width="180">\n  <br>\n  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>\n</div>\n\n<div align="center">\n\n# nonebot-plugin-bafortune\n\n_✨ 蔚蓝档案今日运势插件 ✨_\n\n\n<a href="./LICENSE">\n    <img src="https://img.shields.io/github/license/captain-wangrun-cn/nonebot-plugin-bafortune.svg" alt="license">\n</a>\n<a href="https://pypi.python.org/pypi/nonebot-plugin-bafortune">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-bafortune.svg" alt="pypi">\n</a>\n<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">\n\n</div>\n\n## 📖 介绍\n\n《蔚蓝档案》今日运势插件，支持多平台，高自定义\n\n## 💿 安装\n\n<details open>\n<summary>使用 nb-cli 安装</summary>\n在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装\n\n    nb plugin install nonebot-plugin-bafortune\n\n</details>\n\n<details>\n<summary>使用包管理器安装</summary>\n在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令\n\n<details>\n<summary>pip</summary>\n\n    pip install nonebot-plugin-bafortune\n</details>\n\n\n打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入\n\n    plugins = ["nonebot_plugin_bafortune"]\n\n</details>\n\n## ⚙️ 配置\n\n### 必填配置\n在 nonebot2 项目的`.env`文件中添加下表中的必填配置\n| 配置项          | 类型   | 必填 | 默认值 | 说明                  |\n|:------------:|:----:|:---:|:---:|:-------------------:|\n| bafortune_api | str | <font color="red">是</font>  | "none"  | 图片API，可选：`wr` `lolicon` `local` `custom` `none` <br>详细请看下面 |\n\n- `wr`是插件作者自己的蔚蓝档案图片api\n- `lolicon`是lolicon api\n- `local`是本地图片，其路径可在本插件安装后使用`nb localstore`指令查看，请将图片存放在`data`路径中的`image`文件夹内，可看：[localstore](https://github.com/nonebot/plugin-localstore)\n- `custom`为自定义api，需自行编辑`config.py`文件中的`get_image_custom_api`函数\n- `none`为不发送图片，<font color="red">注意：此选项同时需要配置`bafortune_i_sure_not_to_use_image = true`</font>\n<font color="red"><strong>如果你是小白，直接填`bafortune_api = "wr"`或`bafortune_api = "lolicon"`即可</strong></font>\n\n### 选填配置\n| 配置项          | 类型   | 必填 | 默认值 | 说明                  |\n|:------------:|:----:|:---:|:---:|:-------------------:|\n| bafortune_jrys_titles | list[str] | 否  | ["凶", "稳", "顺", "大顺", "小吉", "吉", "大吉", "运"]  | 今日运势标题，总共有8个，对应7颗⭐ |\n| bafortune_jrys_messages | list[str] | 否  | ["长夜再暗，火种仍在，转机终会到来。","微光不灭，步步向前，黎明就在眼前。","心怀希冀，顺流而行，好事悄然靠近。","逆境翻篇，机遇迎面，惊喜不期而至。","小吉随身，难题化易，幸运与你并肩。","吉星高照，所行皆坦，所愿皆如愿。","福泽深厚，大吉加身，一路花开有声。","七星同耀，奇迹频现，今日万事皆成。"]  | 今日运势文案，总共有8个 |\n| bafortune_allow_refresh_jrys | bool | 否  | false  | 是否允许所有人刷新自己的今日运势，否为只允许超级管理员 |\n| bafortune_jrys_extra_message | str | 否  | ""  | 今日运势文案后附加的额外信息 |\n| bafortune_auto_refresh_jrys | bool | 否  | true  | 是否每日刷新今日运势 |\n| bafortune_proxy | str | 否  | ""  | 代理（魔法）地址，对所有api有效，一般clash等软件默认地址为`http://127.0.0.1:7890` |\n| bafortune_i_sure_not_to_use_image | bool | 否  | false  | 我·确·认·不·想·用·图·片❤ |\n\n## 🎉 使用\n### 指令表\n| 指令 | 权限 | 需要@ | 范围 | 说明 |\n|:-----:|:----:|:----:|:----:|:----:|\n| 今日运势 | 所有人 | 否 | 私聊、群聊 | 直接发送即可 |\n| /刷新今日运势 | 超级管理员/所有人（看配置） | 否 | 私聊、群聊 | 刷新自己的今日运势 |\n| /刷新全局今日运势 | 超级管理员 | 否 | 私聊、群聊 | 刷新所有人的今日运势 |\n| /刷新今日运势图片列表 | 超级管理员 | 否 | 私聊、群聊 | 重新加载本地图片列表，仅对选择了本地图片的有效 |\n\n请将斜杠`/`改为你配置的命令起始符\n\n### 效果图\n<img src="imgs/image.png">\n\n## 📃 更新日志\n### 1.0.7（2025.09.02）\n- 🧋插件发布\n',
    'author': 'WR',
    'author_email': 'wangrun114514@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/captain-wangrun-cn/nonebot-plugin-bafortune',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
