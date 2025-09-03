import asyncio
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk.iot import OtaDevice


async def iot_main():
    serial_number = ""
    license_key = ""
    mac_address = "00:22:44:66:88:14"
    ota_url = "http://localhost:3080/api/ota"
    ota_url = None
    ota = OtaDevice(mac_addr=mac_address, client_id=str(uuid.uuid4()), serial_number=serial_number, ota_url=ota_url)
    res = await ota.activate_device()
    print(json.dumps(res["mqtt"]))

    # if not res.get("activation"):
    #     return
    # await ota.check_activate(res["activation"]["challenge"], license_key)


if __name__ == "__main__":
    asyncio.run(iot_main())
