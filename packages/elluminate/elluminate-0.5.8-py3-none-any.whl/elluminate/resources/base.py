from __future__ import annotations

import asyncio
import math
import time
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Tuple, Type, TypeVar

from pydantic import BaseModel
from tqdm import tqdm

from elluminate.schemas.base import BatchCreateStatus, TResult

if TYPE_CHECKING:
    from elluminate.client import Client


T = TypeVar("T", bound=BaseModel)


class BaseResource:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._aget = client._aget
        self._apost = client._apost
        self._aput = client._aput
        self._adelete = client._adelete
        self._semaphore = client._semaphore

    async def _paginate(
        self,
        path: str,
        model: Type[T],
        params: Dict[str, Any] | None = None,
        resource_name: str = "",
        min_pages_to_show_progress: int = 10,
    ) -> list[T]:
        """Helper that handles pagination given a request function.

        Args:
            path (str): API endpoint path relative to the project route prefix
            model (Type[T]): Pydantic model to validate the response against
            params (Dict[str, Any] | None): Additional query parameters for the request
            resource_name (str): Name of the resource being fetched (for progress bar)
            min_pages_to_show_progress (int): Minimum number of pages to show progress bar

        Returns:
            list[T]: Combined list of all items across all pages

        """

        async def fetch_page(page_number: int) -> Tuple[List[T], int]:
            page_params = {**(params or {}), "page": page_number}
            async with self._semaphore:
                response = await self._aget(path, params=page_params)

            data = response.json()
            return [model.model_validate(item) for item in data["items"]], data["count"]

        # Fetch first page
        all_items, total_count = await fetch_page(1)

        if len(all_items) == total_count:
            return all_items

        # Calculate pagination details
        items_per_page = len(all_items)
        total_pages = math.ceil(total_count / items_per_page)

        # Configure progress bar
        should_show_progress = total_pages > min_pages_to_show_progress and resource_name
        remaining_pages = range(2, total_pages + 1)
        if should_show_progress:
            remaining_pages = tqdm(remaining_pages, desc=f"Getting {resource_name}")

        # Fetch remaining pages
        for page in remaining_pages:
            page_items, _ = await fetch_page(page)
            all_items.extend(page_items)

        return all_items

    async def _abatch_create(
        self,
        path: str,
        batch_request: BaseModel,
        batch_response_type: Type[BatchCreateStatus[TResult]],
        timeout: float | None = None,
        polling_interval: float = 3.0,
    ) -> list[TResult]:
        """Generic batch create operation that waits for completion.

        Args:
            path (str): API endpoint path
            batch_request (BaseModel): Batch request object containing items and options
            batch_response_type (Type[BatchCreateStatus[TResult]]): Type of the batch response
            timeout (float | None): Optional timeout in seconds
            polling_interval (float): Time between status checks

        Returns:
            List of created items

        Raises:
            TimeoutError: If operation times out
            RuntimeError: If operation fails

        """
        # Initiate batch operation
        response = await self._apost(f"{path}", json=batch_request.model_dump())
        task_id = response.json()

        # No task was started by the backend
        if task_id is None:
            return []

        # Poll for completion
        start_time = time.time()
        while timeout is None or time.time() - start_time < timeout:
            status_response = await self._aget(f"{path}/{task_id}")
            status = batch_response_type.model_validate(status_response.json())

            if status.status == "FAILURE":
                raise RuntimeError(f"Batch creation failed: {status.error_msg}")
            elif status.status == "SUCCESS":
                if status.result is None:
                    raise RuntimeError("Batch creation succeeded but no results returned")
                return status.result

            await asyncio.sleep(polling_interval)

        raise TimeoutError(f"Batch operation timed out after {timeout} seconds")

    async def _abatch_create_stream(
        self,
        path: str,
        batch_request: BaseModel,
        batch_response_type: Type[BatchCreateStatus[TResult]],
        timeout: float | None = None,
    ) -> AsyncGenerator[BatchCreateStatus[TResult], None]:
        """Generic batch create operation that streams status updates.

        Args:
            path (str): API endpoint path
            batch_request (BaseModel): Batch request object containing items and options
            batch_response_type (Type[BatchCreateStatus[TResult]]): Type of the batch response
            timeout (float | None): Optional timeout in seconds

        Yields:
            Status objects with updates on batch operation progress

        Raises:
            TimeoutError: If operation times out

        """
        # Initiate batch operation
        response = await self._apost(f"{path}", json=batch_request.model_dump())
        task_id = response.json()

        # No task was started by the backend
        if task_id is None:
            return

        # Stream status updates using the existing _aget_stream method
        async for status in self._aget_stream(f"{path}/{task_id}/stream", batch_response_type, timeout):
            yield status

    async def _aget_stream(
        self,
        path: str,
        model: Type[T],
        timeout: float | None = None,
    ) -> AsyncGenerator[T, None]:
        """Stream Server-Sent Events from an endpoint.

        Args:
            path (str): API endpoint path relative to the project route prefix
            model (Type[T]): Pydantic model to validate each SSE message against
            timeout (float | None): Optional timeout in seconds

        Yields:
            T: Validated objects from each SSE message

        Raises:
            TimeoutError: If the operation times out
            RuntimeError: If the request fails

        """
        start_time = time.time()

        async with self._client.async_session.stream(
            "GET",
            f"{self._client.project_route_prefix}/{path}",
        ) as response:
            response.raise_for_status()

            async for data in response.aiter_text():
                if not data.startswith("data:") or not data.endswith("\n\n"):
                    raise RuntimeError(f"Malformed streaming data: {data}")

                # Remove the starting "data:" element and any trailing newlines
                data = data[5:]
                data = data.rstrip("\n")

                # Check timeout
                if timeout is not None and time.time() - start_time >= timeout:
                    raise TimeoutError("Stream operation timed out")

                # Parse SSE data
                yield model.model_validate_json(data)
