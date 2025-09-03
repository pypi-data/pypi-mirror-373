import asyncio
import hashlib
from pathlib import Path
from typing import NewType

import aiofiles
import aiofiles.os
import httpx

from talc.client.api import make_api_request
from talc.client.shared import (
    UploadedFileId,
    UploadFinishRequest,
    UploadFinishResult,
    UploadInitRequest,
    UploadInitResult,
    UploadInitResult_Cached,
    UploadInitResult_New,
)


async def upload_file(local_path: Path) -> UploadedFileId:
    file_hash, file_size = await asyncio.gather(
        _get_file_sha256(local_path),
        _get_file_size(local_path),
    )

    file_name = local_path.name

    request = UploadInitRequest(
        file_name=file_name,
        file_size_bytes=file_size,
        file_sha256=file_hash,
    )

    upload_init_result: UploadInitResult = await make_api_request(
        UploadInitResult,
        "/upload/init",
        method="POST",
        body=request,
    )

    match upload_init_result:
        case UploadInitResult_Cached():
            return upload_init_result.uploaded_file_id

        case UploadInitResult_New():
            return await _actually_upload_file(local_path, upload_init_result)


async def _get_file_sha256(local_path: Path) -> str:
    sha256 = hashlib.sha256()

    async with aiofiles.open(local_path, "rb") as f:
        while chunk := await f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


async def _get_file_size(local_path: Path) -> int:
    stat = await aiofiles.os.stat(local_path)
    return stat.st_size


async def _actually_upload_file(
    local_path: Path,
    upload_init: UploadInitResult_New,
) -> UploadedFileId:

    async with asyncio.TaskGroup() as tg:
        tasks = []
        for upload_part in upload_init.upload_parts:
            tasks.append(
                tg.create_task(_actually_upload_file_part(local_path, upload_part))
            )

        parts = await asyncio.gather(*tasks)

    upload_finish_request = UploadFinishRequest(
        file_upload_request_id=upload_init.file_upload_request_id,
        parts=parts,
    )
    upload_finish_result = await make_api_request(
        UploadFinishResult,
        "/upload/finish",
        method="POST",
        body=upload_finish_request,
    )

    return upload_finish_result.uploaded_file_id


async def _actually_upload_file_part(
    local_path: Path,
    upload_part: UploadInitResult_New.UploadPart,
) -> UploadFinishRequest.UploadPart:
    async with aiofiles.open(local_path, "rb") as f:
        await f.seek(upload_part.byte_range[0])

        data = await f.read(upload_part.byte_range[1] - upload_part.byte_range[0])

        async with httpx.AsyncClient() as client:
            response = await client.put(
                upload_part.upload_url,
                content=data,
                follow_redirects=True,
            )
            response.raise_for_status()

            return UploadFinishRequest.UploadPart(
                part_number=upload_part.part_number,
                response_headers=dict(response.headers.items()),
            )
