import json
import re
from typing import Any, AsyncGenerator, AsyncIterator, Iterator, Union

import httpx

from seekrai.seekrflow_response import SeekrFlowResponse


DATA_LINE_PATTERN = re.compile(r"\A(data:)?\s*(.*?)\s*(\[DONE\])?\s*\Z")


def parse_data_line(line: str) -> str:
    parse = re.fullmatch(DATA_LINE_PATTERN, line)
    if parse:
        return parse.group(2)
    else:
        # This should never happen. Basically everything matches the regex.
        raise ValueError(f"Line did not match expected format: {line}")


def parse_stream(chunks: Iterator[str]) -> Iterator[Any]:
    buffer = []
    for chunk in chunks:
        if chunk == "data: [DONE]":
            break
        content = parse_data_line(chunk)

        if content:
            buffer.append(content)
        else:
            yield json.loads("\n".join(buffer))
            buffer = []

    if buffer:
        yield json.loads("\n".join(buffer))


async def parse_stream_async(chunks: AsyncIterator[str]) -> AsyncIterator[Any]:
    buffer = []
    async for chunk in chunks:
        content = parse_data_line(chunk)

        if content:
            buffer.append(content)
        else:
            yield json.loads("\n".join(buffer))
            buffer = []

    if buffer:
        yield json.loads("\n".join(buffer))


def parse_plain_content(content: bytes) -> dict[str, Any]:
    return {"message": content.decode("utf-8")}


def parse_complete_content(content: bytes) -> Any:
    return json.loads(parse_data_line(content.decode("utf-8")))


def parse_raw_response(
    response: httpx.Response, stream: bool
) -> Union[SeekrFlowResponse, Iterator[SeekrFlowResponse]]:
    headers = dict(response.headers.items())
    content_type = headers.get("content-type", "")

    if stream and "text/event-stream" in content_type:
        stream_content = parse_stream(response.iter_lines())
        return (SeekrFlowResponse(msg, headers) for msg in stream_content)

    elif "text/plain" in content_type:
        content = parse_plain_content(response.content)

    else:
        content = parse_complete_content(response.content)

    return SeekrFlowResponse(content, headers)


async def parse_raw_response_async(
    response: httpx.Response, stream: bool
) -> Union[SeekrFlowResponse, AsyncGenerator[SeekrFlowResponse, None]]:
    headers = dict(response.headers.items())
    content_type = headers.get("content-type", "")

    if stream and "text/event-stream" in content_type:

        async def generate_parse_stream() -> AsyncGenerator[SeekrFlowResponse, None]:
            async for msg in parse_stream_async(response.aiter_lines()):
                yield SeekrFlowResponse(msg, headers)

        return generate_parse_stream()

    elif "text/plain" in content_type:
        content = parse_plain_content(response.read())

    else:
        content = parse_complete_content(response.read())

    return SeekrFlowResponse(content, headers)
