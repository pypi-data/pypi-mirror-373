from typing import Callable, Generic, TypeVar

from pydantic import BaseModel

from enpi_api.l2.types.task import TaskState

Result = TypeVar("Result")


class Execution(BaseModel, Generic[Result]):  # type: ignore[misc]
    """An asynchronous execution.

    Various operations in the API will return an `Execution` object, so that multiple operations can be executed concurrently.
    The `wait` method can be called to wait for the operation to complete and return the result.

    There is also the `enpi_api.l2.util.execution.wait_all_parallel` function that can be used to wait for multiple operations to complete.

    At the end of your script, all `Execution` objects should be waited on to ensure that all operations have completed before the script exits.
    If this is **NOT** done, some operations might not finish executing.

    Example:

        For example, the `enpi_api.l2.client.api.collection_api.CollectionApi.create_collection_from_csv` method starts a Job, so
        it returns an `Execution` object. If you want to use the result of that operation later in the script, or you
        want to be sure it is completed before exiting your script, it should be awaited.

        ```python
        with EnpiApiClient() as client:

            # Some api functions return async executions instead of results
            execution = client.collection_api.create_collection_from_csv(
                import_file_path,
            )

            # An execution has to be awaited to get the result
            collection: CollectionMetadata = execution.wait()

            # `.wait()` can be used already on the api function call
            collection = client.collection_api.create_collection_from_csv(
                import_file_path,
            ).wait()
        ```
    """

    wait: Callable[..., Result]  # type: ignore[misc]
    check_execution_state: Callable[..., TaskState]  # type: ignore[misc]
