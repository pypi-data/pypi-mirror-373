import asyncio
import json
import logging
import uuid
from io import BytesIO
from typing import List

from ms_utils.communication_utils import MicroServiceWs, S3BucketClient
from ms_utils.logging_lib import Logger

logger = Logger.setup_logger(__name__, level=logging.INFO)  # logging.DEBUG
logger.propagate = False


async def send_encoding_job(
    chunks: List[str],
    websocket: MicroServiceWs,
    bucket_manager: S3BucketClient,
    bucket_name: str,
    reference_id: str,
    job_id: str,
    user_id: str = None,
    original_filename: str = None,
    collection_name: str = None,
    active_task: dict = {},
    model_name: str = "BAAI/bge-m3",
    normalize: bool = False,
    content_only: bool = True,
    timeout: int | None = None,  # in seconds
) -> List[List[float]]:
    await _send_chunks(
        chunks,
        websocket,
        bucket_manager,
        bucket_name,
        reference_id,
        job_id,
        user_id,
        original_filename,
        collection_name,
        model_name,
        normalize,
        content_only,
    )

    if timeout:
        for i in range(timeout):
            if (
                active_task["type"] == "running"
                and not active_task["response"]
            ):
                await asyncio.sleep(1)
                logger.debug(f"Waiting for response for {i + 1} seconds")
            break
    else:
        while active_task["type"] == "running" and not active_task["response"]:
            await asyncio.sleep(1)

    if active_task["type"] == "error":
        active_task["type"] = "running"
        active_task["response"] = None
        raise Exception("Encoding job sent an error.")
    elif active_task["type"] == "ok":
        result_file = active_task["response"]
        consumption = active_task["consumption"]
        file = bucket_manager.download_file(
            bucket_name=bucket_name,
            object_name=result_file,
        )
        bucket_manager.delete_file(
            bucket_name=bucket_name,
            object_name=result_file,
        )
        file.seek(0)
        return json.load(file), consumption
    else:
        raise Exception("Recieved unknown response type in incoming message.")


async def _send_chunks(
    chunks: List,
    websocket: MicroServiceWs,
    bucket_manager: S3BucketClient,
    bucket_name: str,
    reference_id: str,
    job_id: str,
    user_id: str,
    original_filename: str,
    collection_name: str,
    model_name: str,
    normalize: bool,
    content_only: bool,
):
    buffer = BytesIO(json.dumps(chunks).encode("utf-8"))
    filename = f"encoder/{uuid.uuid4()}.json"
    if not bucket_manager.upload_file(
        file=buffer,
        bucket_name=bucket_name,
        object_name=filename,
    ):
        raise Exception("Failed to upload chunks file to S3 Bucket.")

    try:
        await websocket.send_task_to_ms(
            "workers_manager",
            reference_id,
            job_id,
            {
                "job_type": "inference",
                "job_task": "text-to-embeddings",
                "content_only": content_only,
                "params": {
                    "model": model_name,
                    "input": None,
                    "bucket_name": bucket_name,
                    "object_name": filename,
                    "normalize": normalize,
                    "user_id": user_id,
                    "original_filename": original_filename,
                    "collection_name": collection_name,
                },
            },
        )
    except Exception as e:
        logger.error(f"An error occurred while sending task to ms : {e}")
        raise


def download_data(
    bucket_manager: S3BucketClient,
    bucket_name: str,
    object_name: str,
) -> dict:
    buffered_data = bucket_manager.download_file(bucket_name, object_name)
    buffered_data.seek(0)
    extracted_data = json.load(buffered_data)

    # delete remote intermediate data
    bucket_manager.delete_file(
        bucket_name=bucket_name,
        object_name=object_name,
    )

    return extracted_data
