import os
import time
from pathlib import Path
from typing import Generator, Sequence
from urllib.parse import urlparse

from loguru import logger
from typing_extensions import assert_never

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.api_error import ApiError
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.file import FederatedCredentials, File, FileId, FileStatus, OnCollisionAction
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.tag import Tag, TagId
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionTaskId
from enpi_api.l2.util.file import download_file, unique_temp_dir, upload_file_to_s3
from enpi_api.l2.util.tag import tags_to_api_payload


class NameEmpty(Exception):
    """Thrown when the name of a file is empty, which is not allowed."""

    def __init__(self) -> None:
        """@private"""
        super().__init__("Name cannot be empty")


class S3UploadFailed(Exception):
    """Indicates that the upload to S3 failed."""

    def __init__(self, file_path: str | Path, error: Exception):
        """@private"""
        super().__init__(f"Failed to upload file `{file_path}` to S3, error: {error}")


class FileApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_files(self) -> Generator[File, None, None]:
        """Get a generator through all available files in the platform.

        Returns:
            Generator[enpi_api.l2.types.file.File, None, None]: A generator through all files in the platform.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                for file in enpi_client.file_api.get_files():
                    print(file)
            ```
        """

        logger.info("Getting a generator through all files")

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        # Fetch the first page, there is always a first page, it may be empty
        try:
            get_files_response = file_api_instance.get_files()
        except openapi_client.ApiException as e:
            raise ApiError(e)

        # `files` and `cursor` get overwritten in the loop below when fetching a new page
        files = get_files_response.files
        cursor = get_files_response.cursor

        while True:
            for file in files:
                yield File.from_raw(file)

            # Check if we need to fetch a next page
            if cursor is None:
                logger.debug("No more pages of files")
                return  # No more pages

            # We have a cursor, so we need to get a next page
            logger.debug("Fetching next page of files")
            try:
                get_files_response = file_api_instance.get_files(cursor=cursor)
            except openapi_client.ApiException as e:
                raise ApiError(e)
            files = get_files_response.files
            cursor = get_files_response.cursor

    def get_file_by_id(self, file_id: FileId) -> File:
        """Get a single file by its ID.

        Args:
            file_id (enpi_api.l2.types.file.FileId): The ID of the file to get.

        Returns:
            enpi_api.l2.types.file.File: The file, with all its metadata.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                example_file_id = FileId("00000000-0000-0000-0000-000000000000")
                file: File = enpi_client.file_api.get_file_by_id(file_id=example_file_id)
            ```
        """

        logger.info(f"Getting file with ID `{file_id}`")

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        try:
            get_file_response = file_api_instance.get_file(file_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        file = File.from_raw(get_file_response.file)

        return file

    def delete_file_by_id(self, file_id: FileId) -> None:
        """Delete a single file by its ID.

        This will remove the file from the ENPICOM Platform.

        Args:
            file_id (enpi_api.l2.types.file.FileId): The ID of the file to delete.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                example_file_id = FileId("00000000-0000-0000-0000-000000000000")
                enpi_client.file_api.delete_file_by_id(file_id=example_file_id))
            ```
        """

        logger.info(f"Deleting file with ID `{file_id}`")

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        try:
            file_api_instance.delete_file(file_id=str(file_id))
        except openapi_client.ApiException as e:
            raise ApiError(e)

        logger.info(f"File with ID `{file_id}` successfully deleted")

    def upload_file(
        self,
        file_path: str | Path,
        tags: Sequence[Tag] = (),
        on_collision: OnCollisionAction = OnCollisionAction.ERROR,
    ) -> Execution[File]:
        """Upload a file to the platform.

        Args:
            file_path (str | Path): The path to the file to upload.
            tags (Sequence[enpi_api.l2.types.tag.Tag]): The tags to add to the file.
            on_collision (enpi_api.l2.types.file.OnCollisionAction): The action to take when uploading a file with the same name as an existing file.

        Returns:
            enpi_api.l2.types.execution.Execution[enpi_api.l2.types.file.File]: An awaitable that returns the uploaded file
              or an existing one if the `OnCollisionAction` is set to `SKIP`.

        Raises:
            enpi_api.l2.client.api.file_api.NameEmpty: If the name of the file is empty.
            enpi_api.l2.client.api.file_api.S3UploadFailed: If the upload to S3 failed.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                file: File = enpi_client.file_api.upload_file(file_path="path/to/file.txt").wait()
            ```
        """

        logger.info(f"Uploading file with path `{file_path}`")

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        # Uploading a file is a two-step process:
        # 1. Request an S3 temporary credentials used for upload
        logger.debug("Requesting temporary upload credentials.")

        name = os.path.basename(file_path)
        name = name.strip()
        if not name:
            raise NameEmpty()

        upload_file_request = openapi_client.UploadFileRequest(name=name, tags=tags_to_api_payload(tags), on_collision=on_collision)

        try:
            upload_file_response = file_api_instance.upload_file(upload_file_request)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        file_id = FileId(upload_file_response.id)

        # In the event that the file already exists, and we chose to SKIP, then we can return the existing file
        if upload_file_response.credentials is None:
            logger.info(f"File with name `{name}` already exists, and `on_collision` is set to `SKIP`")
            return Execution(wait=lambda: self.get_file_by_id(file_id), check_execution_state=lambda: TaskState.SUCCEEDED)

        s3_federated_credentials = FederatedCredentials.model_validate(
            upload_file_response.credentials,
            from_attributes=True,
        )

        # 2. Upload the file by using temporary credentials and boto3 client
        try:
            upload_file_to_s3(file_path, s3_federated_credentials)
        except Exception as err:
            raise S3UploadFailed(file_path, err)

        def wait() -> File:
            # A file is not immediately usable after uploading, it needs to be processed first
            # So before you can use a file you need to wait for it to be processed
            self.wait_for_file_to_be_processed(file_id)

            logger.success(f"File uploaded with ID `{file_id}`")

            return self.get_file_by_id(file_id)

        return Execution(wait=wait, check_execution_state=lambda: TaskState.SUCCEEDED)

    def download_file_by_id(
        self,
        file_id: FileId,
        output_directory: str | Path | None = None,
        name: str | None = None,
    ) -> Path:
        """Download a single file by its ID into the specified directory.

        Download a file from the platform to your local machine. The file will be saved in the specified directory with
        the name of the file as it was in the ENPICOM Platform. Alternatively you can overwrite the name by providing one
        yourself as the `name` argument.

        Args:
            file_id (enpi_api.l2.types.file.FileId): The ID of the file to download.
            output_directory (str | Path): The directory to save the file to. If left empty, a temporary directory will be used.
            name (str | None): The name of the file. If not provided, a name will be generated.

        Returns:
            Path: The path to the downloaded file.

        Raises:
            enpi_api.l2.client.api.file_api.NameEmpty: If the name of the file is empty.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                my_directory = f"/path/to/files"
                example_file_id = FileId("00000000-0000-0000-0000-000000000000")

                # Assume the file has the name `my_data.fastq`
                full_file_path = enpi_client.file_api.download_file_by_id(
                    file_id=example_file_id,
                    directory=my_directory
                )
                # `full_file_path` will now be `/path/to/files/my_data.fastq`
            ```
        """

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        try:
            download_file_response = file_api_instance.download_file(file_id=str(file_id))
        except openapi_client.ApiException as e:
            raise ApiError(e)

        # If no name is provided, we parse the URL to get the file name
        if name is None:
            parsed_url = urlparse(download_file_response.download_url)
            name = Path(parsed_url.path).name

        if not name or name == "":
            raise NameEmpty()

        # Ensure that the directory exists
        if output_directory is None:
            output_directory = unique_temp_dir()

        os.makedirs(output_directory, exist_ok=True)

        full_path = os.path.join(output_directory, name)

        logger.info(f"Downloading file with ID `{file_id}` to `{full_path}`")
        downloaded_file_path = download_file(download_file_response.download_url, full_path)
        logger.success(f"File with ID `{file_id}` successfully downloaded to `{downloaded_file_path}`")

        return downloaded_file_path

    def download_export_by_workflow_execution_task_id(
        self, task_id: WorkflowExecutionTaskId, output_directory: str | Path | None = None, name: str | None = None
    ) -> Path:
        """Download a single file by its job ID to the specified directory.

        Download an export from a job to your local machine. The export will be saved in the specified directory with
        the name of the file as it was in the job. Alternatively you can overwrite the name by providing one
        yourself as the `name` argument.

        Args:
            workflow_execution_id (enpi_api.l2.types.workflow.WorkflowExecutionId): The ID of the workflow execution to download an export from.
            output_directory (str | Path | None): The directory to save the file to. If none is provided, a temporary
              directory will be used.
            name (str | None): The name of the file. If not provided, a name will be generated.

        Returns:
            Path: The path to the downloaded file.

        Raises:
            enpi_api.l2.client.api.file_api.NameEmpty: If the name of the file is empty.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                my_directory = f"/path/to/files"
                example_task_id = TaskId(1234)

                # Assume the file has the name `my_data.fastq`
                full_file_path = enpi_client.file_api.download_export_by_workflow_execution_task_id(
                    task_id=example_task_id,
                    directory=my_directory
                )
                # `full_file_path` will now be `/path/to/files/my_data.fastq`
            ```
        """

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        try:
            download_file_response = file_api_instance.download_export(job_id=task_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        # If no name is provided, we parse the URL to get the file name
        if name is None:
            parsed_url = urlparse(download_file_response.download_url)
            name = Path(parsed_url.path).name

        if not name or name == "":
            raise NameEmpty()

        # Ensure that the directory exists
        if output_directory is None:
            output_directory = unique_temp_dir()

        os.makedirs(output_directory, exist_ok=True)

        full_path = os.path.join(output_directory, name)

        logger.info(f"Downloading export from task with ID `{task_id}` to `{full_path}`")
        downloaded_file_path = download_file(download_file_response.download_url, full_path)
        logger.success(f"Export from task with ID `{task_id}` successfully downloaded to `{downloaded_file_path}`")

        return downloaded_file_path

    def update_tags(self, file_id: FileId, tags: list[Tag]) -> None:
        """Update the tags of a file.

        Adds and updates the given tags to the file. If a tag is already present on the file, the value will be
        overwritten with the given value for the same tag.

        Args:
            file_id (enpi_api.l2.types.file.FileId): The ID of the file to update.
            tags (list[enpi_api.l2.types.tag.Tag]): The tags that will be updated or added if they are not already present.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                enpi_client.file_api.update_tags(
                    file_id=FileId("00000000-0000-0000-0000-000000000000"),
                    tags=[
                        Tag(id=TagId(FileTags.CampaignId), value="my new value"),
                        Tag(id=TagId(FileTags.ProjectId), value="another value")
                    ]
                )
            ```
        """

        logger.info(f"Updating tags for file with ID `{file_id}`")

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        update_file_tags_request = openapi_client.UpdateTagsRequest(tags=tags_to_api_payload(tags))

        try:
            file_api_instance.update_tags(file_id=str(file_id), update_tags_request=update_file_tags_request)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        logger.success(f"Tags updated for file with ID `{file_id}`")

    def remove_tags(self, file_id: FileId, tags: list[TagId]) -> None:
        """Remove the specified tags from a file.

        Args:
            file_id (enpi_api.l2.types.file.FileId): The ID of the file to update.
            tags (List[enpi_api.l2.types.tag.TagId]): The tags that will be removed from the file.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                enpi_client.file_api.remove_tags(
                    file_id=FileId("00000000-0000-0000-0000-000000000000"),
                    tags=[TagId(FileTags.CampaignId), TagId(FileTags.ProjectId)]
                )
            ```
        """

        logger.info(f"Removing tags: {tags} from file with ID `{file_id}`")

        file_api_instance = openapi_client.FileApi(self._inner_api_client)

        delete_tags_request = openapi_client.DeleteTagsRequest(tags=[int(x) for x in tags])

        try:
            file_api_instance.delete_tags(file_id=str(file_id), delete_tags_request=delete_tags_request)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        logger.success(f"Tags removed from file with ID `{file_id}`")

    def wait_for_file_to_be_processed(self, file_id: FileId) -> None:
        """Wait for a file to be processed.

        Files are not immediately usable after uploading, they need to be processed first. This convenience method
        waits for a file to be processed.

        Args:
            file_id (enpi_api.l2.types.file.FileId): The ID of the file to wait for.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with EnpiApiClient() as enpi_client:
                enpi_client.file_api.wait_for_file_to_be_processed(file_id=FileId("00000000-0000-0000-0000-000000000000"))
            ```
        """

        logger.info(f"Waiting for file with ID `{file_id}` to be processed")

        poll_interval_seconds = 1

        # We do not know how long it will take for a file to be processed, so we poll the file until it is processed
        while True:
            file = self.get_file_by_id(file_id)

            if file.status == FileStatus.PROCESSED:
                logger.success(f"File with ID `{file_id}` has been processed")
                return
            elif file.status == FileStatus.PROCESSING:
                logger.debug(f"File with ID `{file_id}` is still being processed. Waiting for {poll_interval_seconds} seconds")
                time.sleep(poll_interval_seconds)
            else:
                assert_never(file.status)
