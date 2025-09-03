import asyncio
import copy
import json
import logging
import time
from typing import Any, Dict

import numpy as np
import requests

from xiaozhi_sdk.utils.mcp_tool import _get_random_music_info

logger = logging.getLogger("xiaozhi_sdk")

mcp_initialize_payload: Dict[str, Any] = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "", "version": "0.0.1"},
    },
}

mcp_tools_payload: Dict[str, Any] = {
    "jsonrpc": "2.0",
    "id": 2,
    "result": {"tools": []},
}


class McpTool(object):

    def __init__(self):
        self.session_id = ""
        self.explain_url = ""
        self.explain_token = ""
        self.websocket = None
        self.mcp_tool_dict = {}
        self.is_playing = False
        self.message_handler_callback = None

    def get_mcp_json(self, payload: dict):
        return json.dumps({"session_id": self.session_id, "type": "mcp", "payload": payload})

    def _build_response(self, request_id: str, content: str, is_error: bool = False):
        return self.get_mcp_json(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": content}],
                    "isError": is_error,
                },
            }
        )

    async def analyze_image(self, img_byte: bytes, question: str = "这张图片里有什么？"):
        headers = {"Authorization": f"Bearer {self.explain_token}"}
        files = {"file": ("camera.jpg", img_byte, "image/jpeg")}
        payload = {"question": question}
        init_time = time.time()
        try:
            response = requests.post(self.explain_url, files=files, data=payload, headers=headers, timeout=8)
            res_json = response.json()
        except Exception as e:
            logger.error("[MCP] 图片解析 error: %s", e)
            return "网络异常", True
        if res_json.get("error"):
            return res_json, True
        logger.debug("[MCP] 图片解析耗时：%s", time.time() - init_time)
        return res_json, False

    async def play_custom_music(self, tool_func, arguments):
        pcm_array, is_error = await tool_func(arguments)
        while True:
            if not self.is_playing:
                break
            await asyncio.sleep(0.1)
        pcm_array = await self.audio_opus.change_sample_rate(np.array(pcm_array))
        self.output_audio_queue.extend(pcm_array)

    async def mcp_tool_call(self, mcp_json: dict):
        tool_name = mcp_json["params"]["name"]
        mcp_tool = self.mcp_tool_dict[tool_name]
        arguments = mcp_json["params"]["arguments"]
        try:
            if tool_name == "play_custom_music":
                # v1 返回 url
                music_info = await _get_random_music_info(arguments["id_list"])
                if not music_info.get("url"):
                    tool_res, is_error = {"message": "播放失败"}, True
                else:
                    tool_res, is_error = {"message": "正在为你播放: {}".format(arguments["music_name"])}, False
                    data = {
                        "type": "music",
                        "state": "start",
                        "url": music_info["url"],
                        "text": arguments["music_name"],
                        "source": "sdk.mcp_music_tool",
                    }
                    await self.message_handler_callback(data)

                # v2 音频放到输出
                # asyncio.create_task(self.play_custom_music(tool_func, arguments))

            elif mcp_tool.get("is_async"):
                tool_res, is_error = await mcp_tool["tool_func"](arguments)
            else:
                tool_res, is_error = mcp_tool["tool_func"](arguments)
        except Exception as e:
            logger.error("[MCP] tool_name: %s, error: %s", tool_name, e)
            return self._build_response(mcp_json["id"], "工具调用失败", True)

        if is_error:
            logger.error("[MCP] tool_name: %s, error: %s", tool_name, tool_res)
            return self._build_response(mcp_json["id"], "工具调用失败, {}".format(tool_res), True)

        if tool_name == "take_photo":
            tool_res, is_error = await self.analyze_image(tool_res, mcp_json["params"]["arguments"]["question"])

        content = json.dumps(tool_res, ensure_ascii=False)
        return self._build_response(mcp_json["id"], content, is_error)

    async def mcp(self, data: dict):
        payload = data["payload"]
        method = payload["method"]

        if method == "initialize":
            self.explain_url = payload["params"]["capabilities"]["vision"]["url"]
            # self.explain_url = "http://82.157.143.133:8000/vision/explain"
            self.explain_token = payload["params"]["capabilities"]["vision"]["token"]

            mcp_initialize_payload["id"] = payload["id"]
            await self.websocket.send(self.get_mcp_json(mcp_initialize_payload))

        elif method == "notifications/initialized":
            # print("\nMCP 工具初始化")
            pass

        elif method == "notifications/cancelled":
            logger.error("[MCP] 工具加载失败")

        elif method == "tools/list":
            mcp_tools_payload["id"] = payload["id"]
            tool_name_list = []
            mcp_tool_dict = copy.deepcopy(self.mcp_tool_dict)
            for _, mcp_tool in mcp_tool_dict.items():
                tool_name_list.append(mcp_tool["name"])
                tool_func = mcp_tool.pop("tool_func", None)
                if not tool_func:
                    logger.error("[MCP] Tool %s has no tool_func", mcp_tool["name"])
                    return
                mcp_tool.pop("is_async", None)
                mcp_tools_payload["result"]["tools"].append(mcp_tool)

            await self.websocket.send(self.get_mcp_json(mcp_tools_payload))
            logger.debug("[MCP] 加载成功，当前可用工具列表为：%s", tool_name_list)

        elif method == "tools/call":
            tool_name = payload["params"]["name"]

            if not self.mcp_tool_dict.get(tool_name):
                logger.warning("[MCP] Tool not found: %s", tool_name)
                return

            mcp_res = await self.mcp_tool_call(payload)
            await self.websocket.send(mcp_res)
            logger.debug("[MCP] Tool %s called", tool_name)
        else:
            logger.warning("[MCP] unknown method %s: %s", method, payload)
