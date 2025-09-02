from nonebot_plugin_localstore import get_plugin_data_dir
import json

data_dir = get_plugin_data_dir() / "data"
if not data_dir.exists():
    data_dir.mkdir(parents=True)

def write_data(uid, data):
    """写入用户数据"""
    with open(data_dir / f"{uid}.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(data))

def read_data(uid) -> dict:
    """读取用户数据"""
    if (data_dir / f"{uid}.json").exists():
        with open(data_dir / f"{uid}.json", "r", encoding="utf-8") as f:
            return json.loads(f.read())
    return {}

def delete_all_jrys_data():
    """删除所有用户数据"""
    for file in data_dir.glob("*.json"):
        file.unlink()

def delete_jrys_data(uid):
    """删除指定用户数据"""
    if (data_dir / f"{uid}.json").exists():
        (data_dir / f"{uid}.json").unlink()
