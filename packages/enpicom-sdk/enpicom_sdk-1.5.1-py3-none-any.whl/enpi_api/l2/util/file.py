"""@private
Nothing in this module is useful for customers to invoke directly, hide it from the docs.
"""

import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Callable

import requests
from loguru import logger
from tqdm import tqdm

from enpi_api.l2.types.file import FederatedCredentials
from enpi_api.l2.util.aws import get_s3_client

ChunkIndex = int


def download_file(
    url: str,
    target_file_path: str | Path,
    map_chunk_fn: Callable[[bytes, ChunkIndex], bytes] | None = None,
    chunk_size: int = 32768,
    show_progress: bool = True,
) -> Path:
    """Download a file from a URL to a target file path.

    Args:
        url (str): The URL to download the file from.
        target_file_path (str | Path): The path to save the downloaded file to, this should include the
          filename as well.
        map_chunk_fn (Callable[[bytes, ChunkIndex], bytes] | None): A function that can be used to modify the downloaded
          content. It will be called on every chunk, with the chunk bytes and the index of the chunk. It should return
          the chunk or modified chunk. Defaults to None.
        chunk_size (int): The size of the chunks to download the file in. Defaults to 8192.
        show_progress (bool): Whether to show a progress bar while downloading the file. Defaults to True.

    Returns:
        Path: The path to the downloaded file.

    Example:

        ```python
        path = download_file("https://example.com/file.txt", "/tmp/file.txt")
        ```
    """
    logger.info(f"Downloading file '{url}', to '{target_file_path}'...")

    # Make sure the target directory exists
    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        def __download(_response: requests.Response, _chunk_size: int, on_chunk_lambda: Callable[[], bool | None] | None = None) -> None:
            with open(target_file_path, "wb") as file_handle:
                chunk_index = 0

                for chunk in response.iter_content(chunk_size=chunk_size):
                    if map_chunk_fn is not None:
                        chunk = map_chunk_fn(chunk, chunk_index)

                    file_handle.write(chunk)
                    if on_chunk_lambda is not None:
                        on_chunk_lambda()
                    chunk_index += 1

        if show_progress:
            total_bytes = None
            if "Content-Length" in response.headers:
                total_bytes = int(response.headers["Content-Length"])

            with tqdm(total=total_bytes, unit="B", unit_scale=True) as progress_bar:
                __download(response, chunk_size, lambda: progress_bar.update(chunk_size))
        else:
            __download(response, chunk_size)

    logger.success(f"File downloaded to '{target_file_path}'")

    return Path(target_file_path)


def upload_file_to_s3(file_path: str | Path, s3_federated_credentials: FederatedCredentials) -> None:
    """Upload a file to a S3 bucket using federated credentials.

    Args:
        file_path (str | Path): The path to the file to upload.
        s3_federated_credentials (FederatedCredentials): Temporary credentials used for the upload.
    """

    get_s3_client(s3_federated_credentials).upload_file(str(file_path), s3_federated_credentials.bucket, s3_federated_credentials.key)


class InvalidImportFileHeadersType(Exception):
    def __init__(self) -> None:
        self.message = "All import file headers need to be either tag-ids or tag-keys, mixing those types is not allowed."
        super().__init__(self.message)


def verify_headers_uniformity(headers: list[str]) -> None:
    """Verifies passed headers type uniformity: we allow headers in both tag-key and tag-id forms,
    but we allow only one header form at the time, so no mixing is allowed. This function checks
    if the passed headers are either all able to be parsed into numbers (meaning they're all tag ids)
    or if the opposite is true (meaning all of them are tag keys).

    Args:
        headers (list[str]): Headers that are meant to be verified.

    Raises:
        InvalidImportFileHeadersType
    """
    if not (all([str(header).isnumeric() for header in headers]) or not any([str(header).isnumeric() for header in headers])):
        raise InvalidImportFileHeadersType()


def download_and_unzip_archive(url: str, file_dir: str | Path) -> list[Path]:
    """Downloads archive from `url` and extracts it into `file_dir`

    Args:
        url (str): Url from which the archive is downloaded.
        file_dir (Path): path to the directory into which archive will be extracted.

    Returns:
        list[Path]: list of file names after extraction (including `file_dir`)
    """
    with tempfile.NamedTemporaryFile() as temp_file:
        download_file(url, temp_file.name)

        with zipfile.ZipFile(temp_file.name, "r") as archive:
            names = archive.namelist()

            archive.extractall(file_dir)

    return [Path(os.path.join(file_dir, name)) for name in names]


def extract_basket_export_filename(url: str) -> str:
    """Extracts TSV or FASTA export filename from a pre-signed AWS download URL.

    Args:
        url (str): AWS download URL of a basket export result.

    Returns:
        str: Basket export result filename.
    """
    match = re.search(r"[a-zA-Z0-9_-]+\.(tsv|fasta)", url)
    if match is None:
        raise RuntimeError(f"Could not extract filename from pre-signed URL: {url}")

    return match.group()


def unique_temp_dir() -> Path:
    return Path(tempfile.mkdtemp())
