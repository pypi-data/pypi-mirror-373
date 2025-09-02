from concurrent import futures
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.prompt import PromptBase
from threedi_api_client.openapi.models import Download

from threedi_cmd.console import console

CHUNK_SIZE = 16 * 1024

progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
    console=console,
)


class PathPrompt(PromptBase[Path]):
    """A prompt that returns an pathlib.Path"""

    response_type = Path
    validate_error_message = "[prompt.invalid]Please enter a valid pathlib.Path"


def download_worker(task_id: TaskID, url: str, file_path: Path) -> None:
    with requests.get(url, stream=True) as r:
        with open(file_path, "wb") as f:
            progress.start_task(task_id)
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
                progress.update(task_id, advance=len(chunk))


def download_files(downloads: Iterable[Download], output_path: Path) -> bool:
    jobs = []
    success = True
    with progress:
        with futures.ThreadPoolExecutor(max_workers=4) as pool:
            for download in downloads:
                url = urlparse(download.get_url)
                file_name = Path(url.path).name
                file_path = output_path / file_name
                task_id = progress.add_task(
                    "download",
                    filename=file_name,
                    start=False,
                    total=download.size,
                )
                jobs.append(
                    pool.submit(download_worker, task_id, download.get_url, file_path)
                )
        for job in futures.as_completed(jobs):
            try:
                job.result()
            except requests.RequestException as err:
                progress.console.print(err, style="error")
                success = False
    return success
