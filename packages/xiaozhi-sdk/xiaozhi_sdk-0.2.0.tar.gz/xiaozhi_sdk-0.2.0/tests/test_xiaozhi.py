import asyncio
import os
import sys
import time

import numpy as np
import pytest
import sounddevice as sd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk import XiaoZhiWebsocket
from xiaozhi_sdk.utils import read_audio_file


async def assistant_audio_play(audio_queue, wait_time=5):
    # 创建一个持续播放的流
    stream = sd.OutputStream(samplerate=16000, channels=1, dtype=np.int16)
    stream.start()
    last_time = int(time.time())
    while True:
        if not audio_queue:
            await asyncio.sleep(0.01)
            if last_time and time.time() - last_time > wait_time:
                break

            continue

        pcm_data = audio_queue.popleft()

        # 将字节数据转换为 numpy int16 数组
        audio_array = pcm_data

        stream.write(audio_array)
        last_time = time.time()

    stream.stop()
    stream.close()


def mcp_tool_func():
    def mcp_take_photo(data) -> tuple[bytes, bool]:
        with open("./file/image/leijun.jpg", "rb") as f:
            return f.read(), False

    def mcp_get_device_status(data) -> tuple[dict, bool]:
        data = {
            "audio_speaker": {"volume": 80},
            "screen": {"brightness": 75, "theme": "light"},
            "network": {"type": "wifi", "ssid": "wifi名称", "signal": "strong"},
        }
        return data, False

    def mcp_set_volume(data) -> tuple[dict, bool]:
        return {}, False

    from xiaozhi_sdk.utils.mcp_tool import take_photo, get_device_status, set_volume

    take_photo["tool_func"] = mcp_take_photo
    get_device_status["tool_func"] = mcp_get_device_status
    set_volume["tool_func"] = mcp_set_volume

    return [take_photo, get_device_status, set_volume]


async def message_handler_callback(message):
    print("message received:", message)
    if message["type"] == "music":
        print("music:", message["text"])


MAC_ADDR = "00:22:44:66:88:00"

ota_url = None
URL = None


# URL = None


@pytest.mark.asyncio
async def test_main():
    xiaozhi = XiaoZhiWebsocket(message_handler_callback, url=URL, ota_url=ota_url)

    await xiaozhi.set_mcp_tool(mcp_tool_func())
    await xiaozhi.init_connection(MAC_ADDR)

    # # say hellow
    for pcm in read_audio_file("./file/audio/say_hello.wav"):
        await xiaozhi.send_audio(pcm)
    await xiaozhi.send_silence_audio()
    await assistant_audio_play(xiaozhi.output_audio_queue)

    # say take photo
    for pcm in read_audio_file("./file/audio/take_photo.wav"):
        await xiaozhi.send_audio(pcm)
    await xiaozhi.send_silence_audio()
    await assistant_audio_play(xiaozhi.output_audio_queue, 5)

    # play music
    # for pcm in read_audio_file("./file/audio/play_music.wav"):
    #     await xiaozhi.send_audio(pcm)
    # await xiaozhi.send_silence_audio()
    # await assistant_audio_play(xiaozhi.output_audio_queue, 500)

    await xiaozhi.close()
