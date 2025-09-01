import json
from typing import Iterator, Type, TypeVar

import requests
from dacite import Config, from_dict
from qwak.exceptions.qwak_decode_exception import QwakDecodeException
from qwak.exceptions.qwak_external_exception import QwakExternalException
from qwak.llmops.generation.streaming import Stream

_SSEvent = TypeVar("_SSEvent")


class BaseSSEDecoder(Stream[_SSEvent]):
    _response: requests.Response
    _iterator: Iterator[_SSEvent]

    def __init__(self, response: requests.Response, parse_to: Type[_SSEvent]):
        if response.encoding is None:
            response.encoding = "utf-8"

        self._parse_to = parse_to

        self._response = response
        self._iterator = self.__decode(response=response)

    def _is_chunk_empty(self, chunk: str) -> bool:
        return not chunk or chunk == "" or chunk.startswith(":") or chunk == ":"

    def _raise_on_chunk_error(self, chunk: str):
        is_error: bool = False
        try:
            maybe_error = json.loads(chunk)
            if "error" in maybe_error:
                is_error = True
        except Exception:  # nosec
            pass

        if chunk.strip().startswith("error"):
            is_error = True

        if is_error:
            raise QwakExternalException(message=chunk)

    def __decode(self, response: requests.Response) -> Iterator[_SSEvent]:
        chunk: str
        for chunk in response.iter_lines(chunk_size=None, decode_unicode=True):
            if self._is_chunk_empty(chunk=chunk):
                continue

            self._raise_on_chunk_error(chunk=chunk)

            try:
                if chunk.strip().startswith("[DONE]"):
                    break

                _, _, content = chunk.partition(":")

                if content.strip().startswith("[DONE]"):
                    break

                yield self._parse_event(event=content)
            except Exception as e:
                raise QwakDecodeException(f"Failed to decode event: {chunk}") from e

    def __iter__(self) -> Iterator[_SSEvent]:
        for chunk in self._iterator:
            yield chunk

    def __next__(self) -> _SSEvent:
        return self._iterator.__next__()

    def _parse_event(self, event: str) -> _SSEvent:
        return from_dict(
            data_class=self._parse_to,
            data=json.loads(event),
            config=Config(check_types=False),
        )
