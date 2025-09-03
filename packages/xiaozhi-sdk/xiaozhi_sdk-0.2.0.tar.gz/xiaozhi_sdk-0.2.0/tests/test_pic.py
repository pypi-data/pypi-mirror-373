import asyncio

import aiohttp


async def explain_image():
    url = "http://api.xiaozhi.me/vision/explain"
    question = "这个图片里有什么？"
    image_path = "./file/image/leijun.jpg"

    boundary = "----ESP32_CAMERA_BOUNDARY"
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        # 不设置Transfer-Encoding，aiohttp自动处理
    }

    with open(image_path, "rb") as f:
        img_data = f.read()

    # 手动构造multipart body
    body = bytearray()

    # question字段
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="question"\r\n\r\n')
    body.extend(question.encode("utf-8"))
    body.extend(b"\r\n")

    # 文件字段头
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="file"; filename="camera.jpg"\r\n')
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(img_data)
    body.extend(b"\r\n")

    # multipart结束
    body.extend(f"--{boundary}--\r\n".encode())

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=body, headers=headers) as resp:
            print(f"Status: {resp.status}")
            text = await resp.text()
            print("Response:", text)


if __name__ == "__main__":
    asyncio.run(explain_image())
