import hashlib
import hmac
import json
import logging
from typing import Any, Dict, Optional

import aiohttp

from xiaozhi_sdk import __version__
from xiaozhi_sdk.config import OTA_URL

# 常量定义
BOARD_TYPE = "xiaozhi-sdk-box"
USER_AGENT = "xiaozhi-sdk/{}".format(__version__)
BOARD_NAME = "xiaozhi-sdk"

logger = logging.getLogger("xiaozhi_sdk")


class OtaDevice:
    """
    OTA设备管理类

    用于处理设备的激活和挑战验证操作。

    Attributes:
        ota_url (str): OTA服务器URL
        mac_addr (str): 设备MAC地址
        client_id (str): 客户端ID
        serial_number (str): 设备序列号
    """

    def __init__(self, mac_addr: str, client_id: str, ota_url: Optional[str] = None, serial_number: str = "") -> None:
        self.ota_url = ota_url or OTA_URL
        self.ota_url = self.ota_url.rstrip("/")

        self.mac_addr = mac_addr
        self.client_id = client_id
        self.serial_number = serial_number

    def _get_base_headers(self) -> Dict[str, str]:
        return {
            "user-agent": USER_AGENT,
            "Device-Id": self.mac_addr,
            "Client-Id": self.client_id,
            "Content-Type": "application/json",
        }

    async def activate_device(self) -> Dict[str, Any]:
        headers = self._get_base_headers()
        headers["serial-number"] = self.serial_number

        payload = {
            "application": {"version": __version__},
            "board": {
                "type": BOARD_TYPE,
                "name": BOARD_NAME,
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.ota_url + "/", headers=headers, data=json.dumps(payload)) as response:
                if response.status != 200:
                    err_text = await response.text()
                    raise Exception(err_text)
                response.raise_for_status()
                return await response.json()

    async def check_activate(self, challenge: str, license_key: str = "") -> bool:
        url = f"{self.ota_url}/activate"

        headers = self._get_base_headers()

        hmac_instance = hmac.new(license_key.encode(), challenge.encode(), hashlib.sha256)
        hmac_result = hmac_instance.hexdigest()

        payload = {"serial_number": self.serial_number, "challenge": challenge, "hmac": hmac_result}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
                is_ok = response.status == 200
                if not is_ok:
                    logger.debug("[IOT] wait for activate device...")
                return is_ok
