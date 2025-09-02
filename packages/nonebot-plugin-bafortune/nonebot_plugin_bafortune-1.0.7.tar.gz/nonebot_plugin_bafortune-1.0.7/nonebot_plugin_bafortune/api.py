from nonebot.log import logger
from nonebot_plugin_localstore import get_plugin_data_dir
import json
import glob
import re
import httpx
import random
from .config import proxy

proxies = {"http://": proxy, "https://": proxy} if proxy else None
local_images = []
data_dir = get_plugin_data_dir() / "images"
if not data_dir.exists():
    data_dir.mkdir(parents=True)

def make_httpx_client(**kwargs) -> httpx.AsyncClient:
    """创建 httpx.AsyncClient 对象，并适配不同httpx版本的代理参数"""

    def _version_tuple(v: str):
        # 把 "0.28.1" 转成 (0, 28, 1)
        return tuple(map(int, re.findall(r"\d+", v)))
    
    if _version_tuple(httpx.__version__) < (0, 28, 0):
        kwargs.setdefault("proxies", proxies)
    else:
        kwargs.setdefault("proxy", proxies)
    return httpx.AsyncClient(**kwargs)


async def refresh_local_image_list():
    global local_images, data_dir

    """刷新本地图片列表"""
    images = glob.glob(str(data_dir / "*"))
    if images and images != local_images:
        local_images = images
        logger.info(f"刷新本地图片列表成功，总共有{len(local_images)}张图片")

async def url2base64(url):
    async with make_httpx_client() as client:
        response = await client.get(url, timeout=20.0)  # 增加超时
        response.raise_for_status()  # 确保请求成功
    return response.content

async def get_image_wr_api() -> str | None:
    global proxies

    """获取 WR API 的图片"""

    async with make_httpx_client(verify=False) as client:
        for i in range(3):
            try:
                response = await client.get("https://api.wstudio.work/baimg/baimg")
                data = json.loads(response.text)
                if response.status_code == 200:
                    return data["url"]
                logger.warning(f"获取图片失败，正在重试")
            except Exception as e:
                logger.warning(f"获取图片失败: {e}，正在重试")
        return None
                
async def get_image_lolicon_api() -> str | None:
    global proxies

    """获取 Lolicon API 的图片"""

    async with make_httpx_client() as client:
        for i in range(3):
            try:
                response = await client.get("https://api.lolicon.app/setu/v2?tag=BlueArchive&r18=0")
                data = json.loads(response.text)
                if response.status_code == 200 and not data["error"]:
                    return data["data"][0]["urls"]["original"]
                logger.warning(f"获取图片失败，正在重试")
            except Exception as e:
                logger.warning(f"获取图片失败: {e}，正在重试")
        return None
    
async def get_image_local() -> bytes | None:
    global data_dir

    """获取本地图片"""
    if not local_images:
        await refresh_local_image_list()
    if local_images:
        with open(data_dir / random.choice(local_images), "rb") as f:
            return f.read()
    return None

async def get_image_custom_api() -> str | bytes | None:
    """
    获取自定义 API 的图片
    在此处自己编写你的代码，最终需要返回一个图片url或图片二进制数据
    使用make_httpx_client()方法可获取httpx.AsyncClient对象，并使用其发送请求
    """
    return None
