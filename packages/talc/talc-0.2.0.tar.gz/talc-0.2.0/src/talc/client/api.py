import os
import typing
from typing import Callable, Literal

import httpx
import pydantic

from talc.client.shared import (
    GetExtractionJobResult,
    StartExtractionJobRequest,
    StartExtractionJobResult,
    UploadedFileId,
    ExecutionPlanUploadResult,
    ExecutionPlanUploadRequest,
)

AUTH_TOKEN = os.getenv("TALC_AUTH")
SERVICE_ENDPOINT = os.getenv("TALC_ENDPOINT")

_TResponse = typing.TypeVar("_TResponse")


async def get_extraction_job(
    job_id: str,
) -> GetExtractionJobResult:
    return await make_api_request(
        GetExtractionJobResult,
        method="GET",
        path=f"/extractor/jobs/{job_id}",
    )


async def start_extraction_job(
    scenario: pydantic.BaseModel,
    data_file_id: UploadedFileId,
) -> StartExtractionJobResult:
    body = StartExtractionJobRequest(
        scenario=scenario,
        data=data_file_id,
    )
    return await make_api_request(
        StartExtractionJobResult,
        method="POST",
        path="/extractor/jobs",
        body=body,
    )


async def get_extraction_job_output(
    job_id: str,
    sink: Callable[[str], None] = lambda chunk: print(chunk, end="", flush=True),
    format: Literal["json", "csv"] = "json",
) -> None:
    async with httpx.AsyncClient() as client:
        response = await _make_api_request_raw(
            client,
            method="GET",
            path=f"/extractor/jobs/{job_id}/output?format={format}",
        )
        # stream the response directly to stdout
        async for chunk in response.aiter_text():
            sink(chunk)


async def make_api_request(
    response_model: type[_TResponse],
    path: str,
    *,
    method: Literal["GET", "PUT", "POST", "DELETE"] = "GET",
    body: pydantic.BaseModel | None = None,
) -> _TResponse:
    async with httpx.AsyncClient() as client:
        response = await _make_api_request_raw(
            client,
            method=method,
            body=body,
            path=path,
        )

        return (
            pydantic.RootModel[response_model]
            .model_validate_json(response.text, strict=True)
            .root
        )


async def _make_api_request_raw(
    client: httpx.AsyncClient,
    *,
    path: str,
    method: Literal["GET", "PUT", "POST", "DELETE"] = "GET",
    body: pydantic.BaseModel | None = None,
) -> httpx.Response:
    if not AUTH_TOKEN:
        raise ValueError("TALC_AUTH environment variable is not set.")

    if not SERVICE_ENDPOINT:
        raise ValueError("TALC_ENDPOINT environment variable is not set.")

    request_uri = f"{SERVICE_ENDPOINT.rstrip('/')}/{path.lstrip('/')}"

    headers: dict[str, str] = {
        "Authorization": AUTH_TOKEN,
        "Accept": "application/json",
        "User-Agent": "talc-client/1.0",
    }
    if method.upper() == "GET":
        response = await client.get(request_uri, headers=headers)
    elif method.upper() == "POST":
        headers["Content-Type"] = "application/json"
        if body is None:
            raise ValueError("Body must be provided for POST requests.")
        response = await client.post(
            request_uri,
            headers=headers,
            content=body.model_dump_json().encode("utf-8"),
        )
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    if response.status_code != 200:
        raise httpx.HTTPStatusError(
            f"Request failed with status code {response.status_code}: {response.text}",
            request=response.request,
            response=response,
        )

    return response


async def upload_execution_plan(
    plan_typescript: str,
) -> ExecutionPlanUploadResult:
    body = ExecutionPlanUploadRequest(plan_typescript=plan_typescript)
    return await make_api_request(
        ExecutionPlanUploadResult,
        method="POST",
        path="/plans/upload",
        body=body,
    )
