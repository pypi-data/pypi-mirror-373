# 小智SDK (XiaoZhi SDK)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-xiaozhi--sdk-blue.svg)](https://pypi.org/project/xiaozhi-sdk/)

基于虾哥的 [小智esp32 websocket 通讯协议](https://github.com/78/xiaozhi-esp32/blob/main/docs/websocket.md) 实现的 Python SDK。

一个用于连接和控制小智设备的 Python SDK。支持以下功能：
- 实时音频通信
- MCP 工具集成
- 设备管理与控制

---

## 📦 安装

```bash
pip install xiaozhi-sdk
```

---

## 🚀 快速开始

### 1. 终端使用

最简单的方式是通过终端直接连接设备：

#### 查看帮助信息

```bash
python -m xiaozhi_sdk --help
```

#### 连接设备（需要提供 MAC 地址）

```bash
python -m xiaozhi_sdk 00:22:44:66:88:00
```

### 2. 编程使用 (高阶用法)
参考 [examples](examples/) 文件中的示例代码，可以快速开始使用 SDK。


---

## ✅ 运行测试

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
uv run pytest
```


---

## 🫡 致敬

- 🫡 虾哥的 [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) 项目
