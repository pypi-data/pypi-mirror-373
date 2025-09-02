import json
import os
from os import PathLike
from pathlib import Path
from typing import IO, Tuple, Generator

from duowen_agent.utils.core_utils import record_time, async_record_time
from openai import OpenAI, AsyncOpenAI


class OpenAIAudioSpeed:
    def __init__(
        self,
        base_url: str,
        model: str,
        voice: str,
        api_key: str = None,
        timeout: int = 120,
        extra_headers: dict = None,
        **kwargs,
    ):
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", None)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "xxx")
        self.model = model
        self.voice = voice
        self.timeout = timeout
        self.extra_headers = extra_headers
        self.kwargs = kwargs

    @property
    def sync_client(self) -> OpenAI:
        return OpenAI(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    @property
    def async_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    @record_time()
    def speech(self, input: str, **kwargs) -> bytes:
        return self.sync_client.audio.speech.create(
            **self._build_params(input, **kwargs)
        ).content

    @record_time()
    def speech_for_stream(
        self, input: str, chunk_size: int = 1024, **kwargs
    ) -> Generator[bytes, None, None]:
        with self.sync_client.audio.speech.with_streaming_response.create(
            **self._build_params(input, **kwargs)
        ) as resp:
            for data in resp.iter_bytes(chunk_size):
                yield data

    @async_record_time()
    async def aspeech(self, input: str, **kwargs) -> bytes:
        resp = await self.async_client.audio.speech.create(
            **self._build_params(input, **kwargs)
        )
        return resp.content

    def _build_params(self, input: str, **kwargs):
        params_key = {
            "input",
            "model",
            "voice",
            "instructions",
            "response_format",
            "speed",
            "extra_headers",
            "extra_query",
            "extra_body",
            "timeout",
        }
        return {
            k: v
            for k, v in (
                {
                    "extra_headers": self.extra_headers,
                    "input": input.strip(),
                    "voice": self.voice,
                    "timeout": self.timeout,
                    "model": self.model,
                }
                | self.kwargs
                | kwargs
            ).items()
            if k in params_key and v
        }


class OpenAIAudioTranscriptions:
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = None,
        timeout: int = 120,
        # 'FunAudioLLM/SenseVoiceSmall' 模型只支持 json ， text 格式无效
        response_format: str = "json",
        extra_headers: dict = None,
        **kwargs,
    ):
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", None)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "xxx")
        self.model = model
        self.timeout = timeout
        self.response_format = response_format
        self.extra_headers = extra_headers
        self.kwargs = kwargs

    @property
    def sync_client(self) -> OpenAI:
        return OpenAI(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    @property
    def async_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    @async_record_time()
    async def atranscriptions(self, file: bytes, **kwargs) -> str:
        if not isinstance(file, bytes):
            raise TypeError(f"异步模式只支持传入bytes类型")

        file = ("audio.mp3", file)
        response = await self.async_client.audio.transcriptions.create(
            **self._build_params(file, **kwargs)
        )
        return json.dumps({"text": response.text}, ensure_ascii=False)

    @record_time()
    def transcriptions(
        self, file: str | IO[bytes] | bytes | PathLike[str], **kwargs
    ) -> str:
        if isinstance(file, str):
            file = Path(file)
            if not file.is_file():
                raise FileNotFoundError(f"{file} is not a file")

        if isinstance(file, bytes):
            file = ("audio.mp3", file)
        return json.dumps(
            {
                "text": self.sync_client.audio.transcriptions.create(
                    **self._build_params(file, **kwargs)
                ).text
            },
            ensure_ascii=False,
        )

    @record_time()
    def transcriptions_for_stream(
        self,
        file: str | IO[bytes] | bytes | PathLike[str],
        chunk_size: int = 10,
        **kwargs,
    ) -> Generator[str, None, None]:
        if isinstance(file, str):
            file = Path(file)
            if not file.is_file():
                raise FileNotFoundError(f"{file} is not a file")

        if isinstance(file, bytes):
            file = ("audio.mp3", file)

        with self.sync_client.audio.transcriptions.with_streaming_response.create(
            **self._build_params(file, **kwargs)
        ) as resp:
            for data in resp.iter_text(chunk_size):
                yield data

    def _build_params(
        self,
        file: str | IO[bytes] | bytes | PathLike[str] | Tuple[str, bytes],
        **kwargs,
    ):
        params_key = {
            "file",
            "model",
            "include",
            "language",
            "prompt",
            "response_format",
            "stream",
            "temperature",
            "timestamp_granularities",
            "extra_headers",
            "extra_query",
            "extra_body",
            "timeout",
        }
        return {
            k: v
            for k, v in (
                {
                    "extra_headers": self.extra_headers,
                    "response_format": self.response_format,
                    "file": file,
                    "timeout": self.timeout,
                    "model": self.model,
                }
                | self.kwargs
                | kwargs
            ).items()
            if k in params_key and v
        }
