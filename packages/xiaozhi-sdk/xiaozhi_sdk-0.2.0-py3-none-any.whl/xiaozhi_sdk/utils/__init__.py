import ctypes.util
import os
import platform
import wave


def get_wav_info(file_path):
    with wave.open(file_path, "rb") as wav_file:
        return wav_file.getframerate(), wav_file.getnchannels()


def read_audio_file(file_path):
    """
    读取音频文件并通过yield返回PCM流

    Args:
        file_path (str): 音频文件路径

    Yields:
        bytes: PCM音频数据块
    """
    with wave.open(file_path, "rb") as wav_file:
        while True:
            pcm = wav_file.readframes(960)  # 每次读取960帧（60ms的音频数据）
            if not pcm:
                break
            yield pcm


def setup_opus():

    def fake_find_library(name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if name == "opus":
            system = platform.system().lower()
            machine = platform.machine().lower()

            # 检测架构
            if machine in ["x86_64", "amd64", "x64"]:
                arch = "x64"
            elif machine in ["arm64", "aarch64"]:
                arch = "arm64"
            else:
                # 默认使用x64作为回退
                arch = "x64"

            if system == "darwin":  # macOS
                return f"{current_dir}/../../file/opus/macos-{arch}-libopus.dylib"
            elif system == "windows":  # Windows
                return f"{current_dir}/../../file/opus/windows-opus.dll"
            elif system == "linux":  # Linux
                return f"{current_dir}/../../file/opus/linux-{arch}-libopus.so"
            else:
                # 默认情况，尝试系统查找
                return ctypes.util.find_library(name)

    ctypes.util.find_library = fake_find_library
