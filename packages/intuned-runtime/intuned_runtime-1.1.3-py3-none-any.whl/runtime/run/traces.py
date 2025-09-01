import os
from os import environ
from typing import Optional

import requests

from ..errors import TraceNotFoundError


def get_trace_file_path(run_id: str, attempt_number: Optional[str] = "") -> str:
    file_name = f'{run_id}{attempt_number if attempt_number is not None else ""}'
    traces_dir = environ.get("TRACES_DIRECTORY", "")
    return os.path.join(traces_dir, f"{file_name}.zip")


def upload_trace(run_id: str, attempt_number: Optional[str], trace_signed_url: str):
    trace_file_path = get_trace_file_path(run_id, attempt_number)

    if not os.path.exists(trace_file_path):
        raise TraceNotFoundError()

    file_size = os.path.getsize(trace_file_path)

    with open(trace_file_path, "rb") as trace_file:
        upload_trace_res = requests.put(trace_signed_url, headers={"Content-Length": str(file_size)}, data=trace_file)

        return upload_trace_res


def delete_trace(run_id: str, attempt_number: Optional[str]):
    trace_file_path = get_trace_file_path(run_id, attempt_number)

    if not os.path.exists(trace_file_path):
        raise TraceNotFoundError()

    os.remove(trace_file_path)
