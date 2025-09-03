import io
import random

import aiohttp
import numpy as np


async def async_search_custom_music(data) -> tuple[dict, bool]:
    search_url = f"https://music-api.gdstudio.xyz/api.php?types=search&name={data['music_name']}&count=100&pages=1"

    # 为搜索请求设置 10 秒超时
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(search_url) as response:
            response_json = await response.json()

    music_list = []
    first_music_list = []
    other_music_list1 = []
    other_music_list2 = []
    for line in response_json:
        if data.get("author_name") and data["author_name"] in line["artist"][0]:
            first_music_list.append(line)
        elif data.get("author_name") and (data["author_name"] in line["artist"] or data["author_name"] in line["name"]):
            other_music_list1.append(line)
        else:
            other_music_list2.append(line)

    if len(first_music_list) <= 10:
        music_list = first_music_list
        random.shuffle(other_music_list2)
        music_list = music_list + other_music_list1[: 20 - len(music_list)]
        music_list = music_list + other_music_list2[: 20 - len(music_list)]

    # print(data)
    # print("找到音乐，数量：", len(first_music_list), len(music_list))

    if not music_list:
        return {}, False
    return {"message": "已找到歌曲", "music_list": music_list}, False


async def _get_random_music_info(id_list: list) -> dict:
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        random.shuffle(id_list)

        for music_id in id_list:
            url = f"https://music-api.gdstudio.xyz/api.php?types=url&id={music_id}&br=128"
            async with session.get(url) as response:
                res_json = await response.json()
            if res_json.get("url"):
                break

    return res_json


async def async_mcp_play_music(data) -> tuple[list, bool]:
    try:
        from pydub import AudioSegment
    except ImportError:
        return [], True

    id_list = data["id_list"]
    res_json = await _get_random_music_info(id_list)

    if not res_json:
        return [], False

    pcm_list = []
    buffer = io.BytesIO()
    # 为下载音乐文件设置 60 秒超时（音乐文件可能比较大）
    download_timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=download_timeout) as session:
        async with session.get(res_json["url"]) as resp:
            async for chunk in resp.content.iter_chunked(1024):
                buffer.write(chunk)

    buffer.seek(0)
    audio = AudioSegment.from_mp3(buffer)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 2 bytes = 16 bits
    pcm_data = audio.raw_data

    chunk_size = 960 * 2
    for i in range(0, len(pcm_data), chunk_size):
        chunk = pcm_data[i : i + chunk_size]

        if chunk:  # 确保不添加空块
            chunk = np.frombuffer(chunk, dtype=np.int16)
            pcm_list.extend(chunk)

    return pcm_list, False


search_custom_music = {
    "name": "search_custom_music",
    "description": "Search music and get music IDs. Use this tool when the user asks to search or play music. This tool returns a list of music with their IDs, which are required for playing music. Args:\n  `music_name`: The name of the music to search\n  `author_name`: The name of the music author (optional)",
    "inputSchema": {
        "type": "object",
        "properties": {"music_name": {"type": "string"}, "author_name": {"type": "string"}},
        "required": ["music_name"],
    },
    "tool_func": async_search_custom_music,
    "is_async": True,
}

play_custom_music = {
    "name": "play_custom_music",
    "description": "Play music using music IDs. IMPORTANT: You must call `search_custom_music` first to get the music IDs before using this tool. Use this tool after getting music IDs from search results. Args:\n  `id_list`: The id list of the music to play (obtained from search_custom_music results). The list must contain more than 2 music IDs, and the system will randomly select one to play.\n  `music_name`: The name of the music (obtained from search_custom_music results)",
    "inputSchema": {
        "type": "object",
        "properties": {
            "music_name": {"type": "string"},
            "id_list": {"type": "array", "items": {"type": "string"}, "minItems": 3},
        },
        "required": ["music_name", "id_list"],
    },
    "tool_func": async_mcp_play_music,
    "is_async": True,
}

stop_music = {
    "name": "stop_music",
    "description": "Stop playing music.",
    "inputSchema": {"type": "object", "properties": {}},
    "tool_func": None,
}

get_device_status = {
    "name": "get_device_status",
    "description": "Provides the real-time information of the device, including the current status of the audio speaker, screen, battery, network, etc.\nUse this tool for: \n1. Answering questions about current condition (e.g. what is the current volume of the audio speaker?)\n2. As the first step to control the device (e.g. turn up / down the volume of the audio speaker, etc.)",
    "inputSchema": {"type": "object", "properties": {}},
    "tool_func": None,
}

set_volume = {
    "name": "set_volume",
    "description": "Set the volume of the audio speaker. If the current volume is unknown, you must call `get_device_status` tool first and then call this tool.",
    "inputSchema": {
        "type": "object",
        "properties": {"volume": {"type": "integer", "minimum": 0, "maximum": 100}},
        "required": ["volume"],
    },
    "tool_func": None,
}

set_brightness = {
    "name": "set_brightness",
    "description": "Set the brightness of the screen.",
    "inputSchema": {
        "type": "object",
        "properties": {"brightness": {"type": "integer", "minimum": 0, "maximum": 100}},
        "required": ["brightness"],
    },
    "tool_func": None,
}

set_theme = {
    "name": "set_theme",
    "description": "Set the theme of the screen. The theme can be `light` or `dark`.",
    "inputSchema": {"type": "object", "properties": {"theme": {"type": "string"}}, "required": ["theme"]},
    "tool_func": None,
}

take_photo = {
    "name": "take_photo",
    "description": "Use this tool when the user asks you to look at something, take a picture, or solve a problem based on what is captured.\nArgs:\n`question`: A clear question or task you want to ask about the captured photo (e.g., identify objects, read text, explain content, or solve a math/logic problem).\nReturn:\n  A JSON object that provides the photo information, including answers, explanations, or problem-solving results if applicable.",
    "inputSchema": {
        "type": "object",
        "properties": {"question": {"type": "string"}},
        "required": ["question"],
    },
    "tool_func": None,
}

open_tab = {
    "name": "open_tab",
    "description": "Open a web page in the browser. 小智后台：https://xiaozhi.me",
    "inputSchema": {
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"],
    },
    "tool_func": None,
}
