import tempfile
from pathlib import Path

import pandas as pd
from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.client.api.file_api import FileApi
from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.types.api_error import ApiErrorContext
from enpi_api.l2.types.basket import Basket, BasketExportFormat, BasketId, FastaExportConfig
from enpi_api.l2.types.clone import CloneId
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.sequence import SequenceId
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class BasketApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_baskets(self) -> list[Basket]:
        """Get all Baskets that belong to the user or were
        shared to them by other users.

        Returns:
            list[enpi_api.l2.types.basket.Basket]: Available Baskets.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get all available Baskets.
            ```python
            with EnpiApiClient() as enpi_client:
                baskets = enpi_client.basket_api.get_baskets()
                print(baskets)
            ```
        """

        logger.info("Getting all available Baskets...")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        with ApiErrorContext():
            get_baskets_response = basket_api_instance.get_baskets()

        logger.success(f"Successfully got {len(get_baskets_response.baskets)} Baskets.")

        return [Basket.from_raw(basket) for basket in get_baskets_response.baskets]

    def get_basket(self, basket_id: BasketId) -> Basket:
        """Get a single Basket matched with the provided Basket ID.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket to get.

        Returns:
            enpi_api.l2.types.basket.Basket: Basket matching the provided ID.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get a single Basket.
            ```python
            with EnpiApiClient() as enpi_client:
                id = BasketId(id)
                basket = enpi_client.basket_api.get_basket(id)
                print(basket)
            ```
        """

        logger.info(f"Getting Basket with ID: '{basket_id}'...")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        with ApiErrorContext():
            get_basket_response = basket_api_instance.get_basket(basket_id)

        logger.success(f"Successfully got Basket with ID: '{basket_id}'.")

        return Basket.from_raw(get_basket_response.basket)

    def create_basket(self, name: str, shared: bool = True) -> Basket:
        """Create a new Basket.

        Args:
            name (str): The name of the new Basket.
            shared (bool): Determines if the new Basket will be shared to other users in the organization.
                By default, all Baskets created via this function are being shared to other users.

        Returns:
            enpi_api.l2.types.basket.Basket: Newly created Basket.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Create a new Basket.
            ```python
            with EnpiApiClient() as enpi_client:
                name = "New Basket"
                basket = enpi_client.basket_api.create_basket(name)
                print(basket)
            ```
        """

        logger.info(f"Creating a new {'shared' if shared else 'private'} Basket with name: '{name}'...")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        payload = openapi_client.CreateBasketRequestBody(name=name, shared=shared)

        with ApiErrorContext():
            create_basket_response = basket_api_instance.create_basket(payload)

        logger.success(f"Successfully created a new Basket named: '{name}'.")

        return Basket.from_raw(create_basket_response.basket)

    def update_basket(
        self,
        basket_id: BasketId,
        name: str | None = None,
        shared: bool | None = None,
    ) -> None:
        """Update properties of a Basket matched with the provided Basket ID.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket to be updated.
            name (str | None): New name for the Basket. If no value is provided, Basket's name won't be changed.
            shared (bool | None): Determines if a Basket will be shared to other users in the organization.
                If no value is provided, Basket's shared status won't be changed.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Update an existing Basket.
            ```python
            with EnpiApiClient() as enpi_client:
                id = BasketId(id)
                new_name = "Basket (renamed)"
                is_basket_shared = True
                enpi_client.basket_api.update_basket(id, new_name, is_basket_shared)
            ```
        """

        logger.info(f"Updating Basket with ID: '{basket_id}'...")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        payload = openapi_client.UpdateBasketRequestBody(name=name, shared=shared)

        with ApiErrorContext():
            basket_api_instance.update_basket(basket_id, payload)

        logger.success(f"Successfully updated Basket with ID: '{basket_id}'.")

    def delete_basket(self, basket_id: BasketId) -> None:
        """Delete a Basket matched with the provided Basket ID.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket to be deleted.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Delete a Basket.
            ```python
            with EnpiApiClient() as enpi_client:
                id = BasketId(id)
                enpi_client.basket_api.delete_basket(id)
            ```
        """

        logger.info(f"Deleting Basket with ID: '{basket_id}'...")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        with ApiErrorContext():
            basket_api_instance.delete_basket(basket_id)

        logger.info(f"Successfully deleted Basket with ID:'{basket_id}'.")

    def add_clones_to_basket(
        self,
        basket_id: BasketId,
        clone_ids: list[CloneId] | None = None,
        sequence_ids: list[SequenceId] | None = None,
    ) -> Execution[None]:
        """Resolve clones matched with provided clone and sequence IDs,
        then add them into the target Basket.

        > This functionality uses clone resolving.\n
        > Clone resolving uses passed clone and sequence IDs in order to resolve clones.
        > For each clone, a maximum of one *big* chain and one *small* chain sequence will be picked, resulting in a
        maximum of two sequences per clone.
        > Sequences matched with passed sequence IDs have priority over internally resolved sequences, meaning that if
        possible, they will be picked as sequences for the resolved clones.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket to add clones to.
            clone_ids (list[enpi_api.l2.types.clone.CloneId]): Clone IDs based on which clones will be resolved and added into the target Basket.
            sequence_ids (list[enpi_api.l2.types.sequence.SequenceId]): Sequence IDs based on which clones will be resolved and added into
            the target Basket. If clone resolving based on clone IDs and sequence IDs results in the same, "overlapping" clones (with the same clone IDs)
            but potentially different sequences within, clones resolved with use of sequence IDs will be picked over the ones resolved with clone IDs.

        Returns:
            enpi_api.l2.types.execution.Execution[None]: An awaitable execution.

        Raises:
            ValueError: If the provided clone and/or sequence ID arrays are empty or invalid.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Insert clones into a Basket.
            ```python
            with EnpiApiClient() as enpi_client:
                basket_id = BasketId(1)
                clone_ids = [
                    CloneId(id) for id in [
                        "d0c6982d-34cd-47cd-b465-a603dec0530c",
                        "1c19fcbc-ec84-4baa-a641-42058df18303",
                    ]
                ]
                sequence_ids = [SequenceId(id) for id in [100, 101, 102]]
                enpi_client.basket_api.add_clones_to_basket(basket_id, clone_ids, sequence_ids).wait()
            ```
        """

        logger.info(f"Adding clones to Basket with ID: '{basket_id}'...")

        # Check if we got any ids to work with
        if (clone_ids is None or len(clone_ids) == 0) and (sequence_ids is None or len(sequence_ids) == 0):
            raise ValueError("Both clone and sequence IDs arrays are null, at least one of them needs to contain proper values.")

        # Validate if ID types are right
        if clone_ids is not None and not all([isinstance(id, str) for id in clone_ids]):
            raise ValueError("Some of the passed clone IDs are not strings.")
        elif sequence_ids is not None and not all([isinstance(id, int) for id in sequence_ids]):
            raise ValueError("Some of the passed sequence IDs are not integers.")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        payload = openapi_client.AddClonesRequestBody(
            clone_ids=None if clone_ids is None else [str(id) for id in clone_ids],
            sequence_ids=None if sequence_ids is None else [int(id) for id in sequence_ids],
        )

        with ApiErrorContext():
            add_clones_response = basket_api_instance.add_clones(basket_id, payload)
            assert add_clones_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(add_clones_response.workflow_execution_id)
            waitable = WorkflowExecutionTaskWaitable[None](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_BASKET_ADD_CLONES, on_complete=None
            )

        return Execution(wait=waitable.wait, check_execution_state=waitable.check_execution_state)

    def remove_clones_from_basket(self, basket_id: BasketId, clone_ids: list[CloneId]) -> Execution[None]:
        """Remove clones matches with provided clone IDs from the target Basket.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket from which clones will be removed.
            clone_ids (list[enpi_api.l2.types.clone.CloneId]): IDs of clones that will be removed from target Basket.

        Returns:
            enpi_api.l2.types.execution.Execution[None]: An awaitable execution.

        Raises:
            ValueError: If the provided clone IDs array is invalid.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Remove clones from a Basket.
            ```python
            with EnpiApiClient() as enpi_client:
                basket_id = BasketId(1)
                clone_ids = [
                    CloneId(id) for id in [
                        "d0c6982d-34cd-47cd-b465-a603dec0530c",
                        "1c19fcbc-ec84-4baa-a641-42058df18303",
                    ]
                ]
                enpi_client.basket_api.remove_clones_from_basket(basket_id, clone_ids).wait()
            ```
        """

        n_of_clone_ids = len(clone_ids)
        logger.info(f"Removing {n_of_clone_ids} clone{'' if n_of_clone_ids == 1 else 's'} from Basket with id: '{basket_id}'")

        # Check if we got any ids to work with
        if len(clone_ids) == 0:
            raise ValueError("Provided clone IDs array is empty.")

        # Validate if ID types are right
        if not all([isinstance(id, str) for id in clone_ids]):
            raise ValueError("Some of the passed clone IDs are not strings.")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        payload = openapi_client.RemoveClonesRequestBody(
            clone_ids=[str(id) for id in clone_ids],
        )

        with ApiErrorContext():
            remove_clones_response = basket_api_instance.remove_clones(basket_id, payload)
            assert remove_clones_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(remove_clones_response.workflow_execution_id)

            waitable = WorkflowExecutionTaskWaitable[None](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_BASKET_REMOVE_CLONES, on_complete=None
            )

        return Execution(wait=waitable.wait, check_execution_state=waitable.check_execution_state)

    def export_basket_clones_as_tsv(
        self,
        basket_id: BasketId,
        output_directory: Path | str | None = None,
    ) -> Execution[Path]:
        """Start a Basket clones export in a TSV format, download the result file and return a path to it.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket from which clones will be exported.
            output_directory (Path | str | None): Path to the directory in which the downloaded file will be stored.
                If not provided, a temporary directory will be created.

        Returns:
            enpi_api.l2.types.execution.Execution[Path]: An awaitable execution that returns the local file path to the
              exported file when awaited.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Export Basket clones into a TSV file.
            ```python
            with EnpiApiClient() as enpi_client:
                id = BasketId(1)
                export_dir = os.path.join(os.path.dirname(__file__), "example_dir")
                path = enpi_client.basket_api.export_basket_clones_as_tsv(id, export_dir).wait()
                print(path)
            ```
        """

        logger.info(f"Exporting clones from Basket with ID: '{basket_id}' into a TSV file...")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        payload = openapi_client.StartClonesExportRequestBody(
            openapi_client.StartTsvClonesExportRequestBody(
                format=BasketExportFormat.TSV,
            )
        )

        with ApiErrorContext():
            data = basket_api_instance.start_clones_export(basket_id, payload)
            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(data.workflow_execution_id)

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> Path:
                with ApiErrorContext():
                    file_api = FileApi(self._inner_api_client, self._log_level)
                    file_path = file_api.download_export_by_workflow_execution_task_id(task_id=task_id, output_directory=output_directory)
                    logger.success(f"Successfully exported clones from Basket with ID: '{basket_id}' into a TSV file: '{file_path}'.")
                    return file_path

            waitable = WorkflowExecutionTaskWaitable[Path](
                workflow_execution_id=workflow_execution_id, on_complete=on_complete, task_template_name=WorkflowTaskTemplateName.ENPI_APP_BASKET_EXPORT
            )

            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)

    def export_basket_clones_as_df(self, basket_id: BasketId) -> Execution[pd.DataFrame]:
        """Start a Basket clones export in a TSV format, download the result and return
            the data from it in a DataFrame object.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket from which clones will be exported.

        Returns:
            enpi_api.l2.types.execution.Execution[pd.DataFrame]: An awaitable execution that returns a pandas DataFrame
              object containing the exported data when awaited.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Export Basket clones into a DataFrame.
            ```python
            with EnpiApiClient() as client:
                id = BasketId(1)
                df = client.basket_api.export_basket_clones_as_df(id).wait()
                print(df)
            ```
        """

        logger.info(f"Exporting clones from Basket with ID: '{basket_id}' into a DataFrame...")

        with tempfile.TemporaryDirectory() as temp_dir:
            execution = self.export_basket_clones_as_tsv(basket_id, temp_dir)

            def wait() -> pd.DataFrame:
                tmp_file_path = execution.wait()
                df = pd.read_csv(tmp_file_path, delimiter="\t")

                logger.success(f"Successfully exported clones from Basket with ID: '{basket_id}' into a DataFrame.")

                return df

            return Execution(wait=wait, check_execution_state=execution.check_execution_state)

    def export_basket_clones_as_fasta(
        self,
        basket_id: BasketId,
        fasta_config: FastaExportConfig,
        output_directory: Path | str | None = None,
    ) -> Execution[Path]:
        """Start a Basket clones export in a FASTA format, download the result and return the filepath to the file.

        Args:
            basket_id (enpi_api.l2.types.basket.BasketId): ID of a Basket from which clones will be exported.
            fasta_config (enpi_api.l2.types.basket.FastaExportConfig): Configuration of the Basket FASTA export, determining the
                shape of FASTA file headers and sequences. The enpi_api.l2.types.basket.fasta_config function is the prefered way of
                a configuration object creation.
            output_directory (Path | str | None): Path to a directory in which the downloaded file will be stored.
                If not provided, a temporary directory will be created.

        Returns:
            enpi_api.l2.types.execution.Execution[Path]: An awaitable that returns information about clones added to the
              Basket when awaited.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Export Basket clones into a FASTA file.
            ```python
            with EnpiApiClient() as client:
                id = BasketId(1)
                export_dir = os.path.join(os.path.dirname(__file__), "example_dir")
                path = client.basket_api.export_basket_clones_as_fasta(
                    basket_id,
                    fasta_config(
                        include_unique_clone_id_header=True,
                        include_unique_sequence_id_header=True,
                        include_chain_header=True,
                        header_tag_keys=[
                            "Full Sequence Amino Acids",
                            "Organism",
                        ],
                        sequences=[
                            FastaSequence(
                                chain=Chain.HEAVY,
                                tag_key=FastaExportSequenceKey.CDR3_AMINO_ACIDS,
                            ),
                            FastaSequence(
                                chain=Chain.KAPPA,
                                tag_key=FastaExportSequenceKey.CDR3_AMINO_ACIDS,
                            ),
                        ],
                    ),
                    output_directory=export_dir,
                ).wait()
                print(path)
            ```
        """

        logger.info(f"Exporting clones from Basket with ID: '{basket_id}' into a FASTA file...")

        basket_api_instance = openapi_client.BasketApi(self._inner_api_client)

        payload = openapi_client.StartClonesExportRequestBody(
            openapi_client.StartFastaClonesExportRequestBody(
                format=BasketExportFormat.FASTA,
                fasta_config=fasta_config.to_api_payload(),
            )
        )

        with ApiErrorContext():
            data = basket_api_instance.start_clones_export(basket_id, payload)
            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(data.workflow_execution_id)

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> Path:
                file_api = FileApi(self._inner_api_client, self._log_level)
                file_path = file_api.download_export_by_workflow_execution_task_id(task_id=task_id, output_directory=output_directory)

                logger.success(f"Successfully exported clones from Basket with ID: '{basket_id}' into a FASTA file: '{file_path}'.")
                return file_path

            waitable = WorkflowExecutionTaskWaitable(
                workflow_execution_id=workflow_execution_id, on_complete=on_complete, task_template_name=WorkflowTaskTemplateName.ENPI_APP_BASKET_EXPORT_FASTA
            )

            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)
