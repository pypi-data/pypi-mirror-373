import asyncio
import json
import logging
import os
import re
import uuid
from collections import deque
from typing import Any, Callable, Deque, Dict, Optional

import websockets

from xiaozhi_sdk.config import INPUT_SERVER_AUDIO_SAMPLE_RATE
from xiaozhi_sdk.iot import OtaDevice
from xiaozhi_sdk.mcp import McpTool
from xiaozhi_sdk.utils import get_wav_info, read_audio_file, setup_opus

setup_opus()
from xiaozhi_sdk.opus import AudioOpus

logger = logging.getLogger("xiaozhi_sdk")


class XiaoZhiWebsocket(McpTool):

    def __init__(
        self,
        message_handler_callback: Optional[Callable] = None,
        url: Optional[str] = None,
        ota_url: Optional[str] = None,
        audio_sample_rate: int = 16000,
        audio_channels: int = 1,
        wake_word: str = "",
    ):
        super().__init__()
        self.url = url
        self.ota_url = ota_url
        self.audio_channels = audio_channels
        self.audio_opus = AudioOpus(audio_sample_rate, audio_channels)
        self.wake_word = wake_word

        # 客户端标识
        self.client_id = str(uuid.uuid4())
        self.mac_addr: Optional[str] = None
        self.aec = False
        self.websocket_token = ""

        # 回调函数
        self.message_handler_callback = message_handler_callback

        # 连接状态
        self.hello_received = asyncio.Event()
        self.session_id = ""
        self.websocket = None
        self.message_handler_task: Optional[asyncio.Task] = None

        # 输出音频
        self.output_audio_queue: Deque[bytes] = deque()
        self.is_playing: bool = False

        # OTA设备
        self.ota: Optional[OtaDevice] = None
        self.iot_task: Optional[asyncio.Task] = None
        self.wait_device_activated: bool = False

        # mcp工具
        self.mcp_tool_dict = {}

    async def _send_hello(self, aec: bool) -> None:
        """发送hello消息"""
        hello_message = {
            "type": "hello",
            "version": 1,
            "features": {"mcp": True, "aec": aec},
            "transport": "websocket",
            "audio_params": {
                "format": "opus",
                "sample_rate": 16000,
                "channels": 1,
                "frame_duration": 60,
            },
        }
        await self.websocket.send(json.dumps(hello_message))
        await asyncio.wait_for(self.hello_received.wait(), timeout=10.0)

    async def _start_listen(self) -> None:
        """开始监听"""
        listen_message = {"session_id": self.session_id, "type": "listen", "state": "start", "mode": "realtime"}
        await self.websocket.send(json.dumps(listen_message))

    async def is_activate(self, ota_info):
        """是否激活"""
        if ota_info.get("activation"):
            return False

        return True

    async def _activate_iot_device(self, license_key: str, ota_info: Dict[str, Any]) -> None:
        """激活IoT设备"""
        if not self.ota:
            return

        challenge = ota_info["activation"]["challenge"]
        await asyncio.sleep(3)
        self.wait_device_activated = True
        for _ in range(10):
            if await self.ota.check_activate(challenge, license_key):
                self.wait_device_activated = False
                break
            await asyncio.sleep(3)

    async def _send_demo_audio(self) -> None:
        """发送演示音频"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        wav_path = os.path.join(current_dir, "../file/audio/greet.wav")
        framerate, channels = get_wav_info(wav_path)
        audio_opus = AudioOpus(framerate, channels)

        for pcm_data in read_audio_file(wav_path):
            opus_data = await audio_opus.pcm_to_opus(pcm_data)
            await self.websocket.send(opus_data)
        await self.send_silence_audio()

    async def send_wake_word(self, wake_word: str) -> None:
        """发送唤醒词"""
        await self.websocket.send(
            json.dumps({"session_id": self.session_id, "type": "listen", "state": "detect", "text": wake_word})
        )

    async def send_silence_audio(self, duration_seconds: float = 1.2) -> None:
        """发送静音音频"""
        frames_count = int(duration_seconds * 1000 / 60)
        pcm_frame = b"\x00\x00" * int(INPUT_SERVER_AUDIO_SAMPLE_RATE / 1000 * 60)

        for _ in range(frames_count):
            await self.send_audio(pcm_frame)

    async def _handle_websocket_message(self, message: Any) -> None:
        """处理接受到的WebSocket消息"""

        # audio data
        if isinstance(message, bytes):
            pcm_array = await self.audio_opus.opus_to_pcm(message)
            self.output_audio_queue.extend(pcm_array)
            return

        # json message
        data = json.loads(message)
        message_type = data["type"]
        if message_type == "hello":
            self.hello_received.set()
            self.session_id = data["session_id"]
        elif message_type == "mcp":
            await self.mcp(data)
        elif self.message_handler_callback:
            if data["type"] == "tts":
                if data["state"] == "sentence_start":
                    self.is_playing = True
                    # self.output_audio_queue.clear()
                else:
                    self.is_playing = False

            await self.message_handler_callback(data)

    async def _message_handler(self) -> None:
        """消息处理器"""
        try:
            async for message in self.websocket:
                await self._handle_websocket_message(message)
        except websockets.ConnectionClosed:
            if self.message_handler_callback:
                await self.message_handler_callback(
                    {"type": "websocket", "state": "close", "source": "sdk.message_handler"}
                )
                logger.debug("[websocket] close")

    async def set_mcp_tool(self, mcp_tool_list) -> None:
        """设置MCP工具"""
        for mcp_tool in mcp_tool_list:
            self.mcp_tool_dict[mcp_tool["name"]] = mcp_tool

    async def connect_websocket(self, websocket_token):
        """连接websocket"""
        headers = {
            "Authorization": "Bearer {}".format(websocket_token),
            "Protocol-Version": "1",
            "Device-Id": self.mac_addr,
            "Client-Id": self.client_id,
        }
        try:
            self.websocket = await websockets.connect(uri=self.url, additional_headers=headers)
        except websockets.exceptions.InvalidMessage as e:
            logger.error("[websocket] 连接失败，请检查网络连接或设备状态。当前链接地址: %s, 错误信息：%s", self.url, e)
            return
        self.message_handler_task = asyncio.create_task(self._message_handler())

        await self._send_hello(self.aec)
        await self._start_listen()
        logger.debug("[websocket] Connection successful")
        await asyncio.sleep(0.5)

    async def init_connection(
        self, mac_addr: str, aec: bool = False, serial_number: str = "", license_key: str = ""
    ) -> None:
        """初始化连接"""
        mac_pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
        if not re.match(mac_pattern, mac_addr):
            raise ValueError(f"无效的MAC地址格式: {mac_addr}。正确格式应为 XX:XX:XX:XX:XX:XX")

        self.mac_addr = mac_addr.lower()
        self.aec = aec

        self.ota = OtaDevice(self.mac_addr, self.client_id, self.ota_url, serial_number)
        ota_info = await self.ota.activate_device()
        ws_url = ota_info.get("websocket", {}).get("url")
        self.url = self.url or ws_url

        if not self.url:
            logger.warning("[websocket] 未找到websocket链接地址")
            return

        if "tenclass.net" not in self.url and "xiaozhi.me" not in self.url:
            logger.warning("[websocket] 检测到非官方服务器，当前链接地址: %s", self.url)

        self.websocket_token = ota_info["websocket"]["token"]
        await self.connect_websocket(self.websocket_token)

        if not await self.is_activate(ota_info):
            self.iot_task = asyncio.create_task(self._activate_iot_device(license_key, ota_info))
            logger.debug("[IOT] 设备未激活")

        if self.wake_word:
            await self.send_wake_word(self.wake_word)

    async def send_audio(self, pcm: bytes) -> None:
        """发送音频数据"""
        if not self.websocket:
            return

        state = self.websocket.state
        if state == websockets.protocol.State.OPEN:
            opus_data = await self.audio_opus.pcm_to_opus(pcm)
            await self.websocket.send(opus_data)
        elif state in [websockets.protocol.State.CLOSED, websockets.protocol.State.CLOSING]:
            if self.wait_device_activated:
                logger.debug("[websocket] Server actively disconnected, reconnecting...")
                await self.connect_websocket(self.websocket_token)
            elif self.message_handler_callback:
                await self.message_handler_callback({"type": "websocket", "state": "close", "source": "sdk.send_audio"})
                self.websocket = None
                logger.debug("[websocket] Server actively disconnected")

            await asyncio.sleep(0.5)
        else:
            await asyncio.sleep(0.1)

    async def close(self) -> None:
        """关闭连接"""
        if self.message_handler_task and not self.message_handler_task.done():
            self.message_handler_task.cancel()
            try:
                await self.message_handler_task
            except asyncio.CancelledError:
                pass

        if self.iot_task:
            self.iot_task.cancel()

        if self.websocket:
            await self.websocket.close()
