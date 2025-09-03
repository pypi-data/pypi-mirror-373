import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk import XiaoZhiWebsocket


MAC_ADDR = "00:22:44:66:88:00"
ota_url = None
URL = None


@pytest.mark.asyncio
async def test_main():
    is_end = asyncio.Event()
    async def message_handler_callback(message):
        if message.get("state") == "stop":
            is_end.set()
        print("message received:", message)

    xiaozhi = XiaoZhiWebsocket(message_handler_callback, url=URL, ota_url=ota_url)
    await xiaozhi.init_connection(MAC_ADDR)

    await xiaozhi.send_wake_word("你是")

    await asyncio.wait_for(is_end.wait(), timeout=20.0)
    await xiaozhi.close()
