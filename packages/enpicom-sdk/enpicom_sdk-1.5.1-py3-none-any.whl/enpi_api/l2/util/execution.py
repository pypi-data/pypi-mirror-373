import concurrent.futures
from collections.abc import Sequence
from typing import TypeVar

from enpi_api.l2.types.execution import Execution

ExecutionType = TypeVar("ExecutionType")


def wait(execution: Execution[ExecutionType]) -> ExecutionType:
    """Wait for a single execution to complete.

    You should generally use the `.wait()` on a returned execution instead.

    Args:
        execution (Execution[ExecutionType]): The execution to wait for.

    Returns:
        ExecutionType: The result of the execution.
    """
    return execution.wait()


def wait_all_parallel(executions: Sequence[Execution[ExecutionType]]) -> list[ExecutionType]:
    """Wait for all executions to complete in parallel.

    Args:
        executions (Sequence[Execution[ExecutionType]]): The executions to wait for.

    Returns:
        list[ExecutionType]: The results of the executions.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(wait, executions))
