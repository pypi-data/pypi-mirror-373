import math

import av
import numpy as np
import opuslib

from xiaozhi_sdk.config import INPUT_SERVER_AUDIO_SAMPLE_RATE


class AudioOpus:

    def __init__(self, sample_rate, channels):
        self.sample_rate = sample_rate
        self.channels = channels

        # 创建 Opus 编码器
        self.opus_encoder = opuslib.Encoder(
            fs=sample_rate, channels=channels, application=opuslib.APPLICATION_VOIP  # 采样率  # 单声道  # 语音应用
        )

        # 创建 Opus 解码器
        self.opus_decoder = opuslib.Decoder(
            fs=INPUT_SERVER_AUDIO_SAMPLE_RATE,  # 采样率
            channels=1,  # 单声道
        )

        self.resampler = av.AudioResampler(format="s16", layout="mono", rate=sample_rate)

    async def pcm_to_opus(self, pcm):
        pcm_array = np.frombuffer(pcm, dtype=np.int16)
        pcm_bytes = pcm_array.tobytes()
        return self.opus_encoder.encode(pcm_bytes, 960)

    @staticmethod
    def to_n_960(samples) -> np.ndarray:
        n = math.ceil(samples.shape[0] / 960)
        arr_padded = np.pad(samples, (0, 960 * n - samples.shape[0]), mode="constant", constant_values=0)
        return arr_padded.reshape(n, 960)

    async def change_sample_rate(self, pcm_array) -> np.ndarray:
        if self.sample_rate == INPUT_SERVER_AUDIO_SAMPLE_RATE:
            return self.to_n_960(pcm_array)

        frame = av.AudioFrame.from_ndarray(np.array(pcm_array).reshape(1, -1), format="s16", layout="mono")
        frame.sample_rate = INPUT_SERVER_AUDIO_SAMPLE_RATE  # Assuming input is 16kHz
        resampled_frames = self.resampler.resample(frame)
        samples = resampled_frames[0].to_ndarray().flatten()
        new_frame = av.AudioFrame.from_ndarray(
            samples.reshape(1, -1),
            format="s16",
            layout="mono",
        )
        new_frame.sample_rate = self.sample_rate
        new_samples = new_frame.to_ndarray().flatten()
        return self.to_n_960(new_samples)

    async def opus_to_pcm(self, opus) -> np.ndarray:
        pcm_data = self.opus_decoder.decode(opus, 960)
        pcm_array = np.frombuffer(pcm_data, dtype=np.int16)
        samples = await self.change_sample_rate(pcm_array)
        return samples
