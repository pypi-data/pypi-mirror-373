from typing import Optional

from ...types._api_version import ApiVersion
from ...types.api.store import File, GetFileResponse, GetFilesResponse
from .._request_handler import AsyncRequestHandler
from .base_store import BaseStore


class AsyncStore(BaseStore):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def upload_file(
        self,
        store_connector_id: str,
        project_id: str,
        file_path: str,
        folder_id: Optional[str] = None,
        pending_ingestion: bool = True,
        correlation_id: Optional[str] = None,
    ) -> File:
        """
        Upload a file to the Airia store asynchronously.

        This method uploads a file to the specified store connector and project,
        with optional folder organization and ingestion settings.

        Args:
            store_connector_id: The unique identifier of the store connector (GUID format)
            project_id: The unique identifier of the project (GUID format)
            file_path: Path to the file on disk
            folder_id: Optional folder identifier for organizing the file (GUID format)
            pending_ingestion: Whether the file should be marked as pending ingestion. Default is True.
            correlation_id: Optional correlation ID for request tracing

        Returns:
            File: object containing details about the uploaded file.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The store_connector_id doesn't exist (404)
                - The project_id doesn't exist (404)
                - The folder_id is invalid (400)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)
            ValueError: If required parameters are missing or invalid

        Example:
            ```python
            import asyncio
            from airia import AiriaAsyncClient

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Upload file
                uploaded_file = await client.store.upload_file(
                    store_connector_id="your_store_connector_id",
                    project_id="your_project_id",
                    file_path="document.pdf"
                )

                # Upload with folder organization
                uploaded_file = await client.store.upload_file(
                    store_connector_id="your_store_connector_id",
                    project_id="your_project_id",
                    file_path="document.pdf",
                    folder_id="your_folder_id"
                )

            asyncio.run(main())
            ```
        """
        request_data = self._pre_upload_file(
            store_connector_id=store_connector_id,
            project_id=project_id,
            file_path=file_path,
            folder_id=folder_id,
            pending_ingestion=pending_ingestion,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )

        try:
            response = await self._request_handler.make_request_multipart(
                "POST", request_data
            )
            return File(**response)
        finally:
            request_data.files["File"][1].close()

    async def update_file(
        self,
        store_connector_id: str,
        store_file_id: str,
        project_id: str,
        file_path: str,
        pending_ingestion: bool = True,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Update an existing file in the Airia store asynchronously.

        This method updates an existing file in the specified store connector and project,
        with optional ingestion settings.

        Args:
            store_connector_id: The unique identifier of the store connector (GUID format)
            store_file_id: The unique identifier of the file to update (GUID format)
            project_id: The unique identifier of the project (GUID format)
            file_path: Path to the file on disk
            pending_ingestion: Whether the file should be marked as pending ingestion. Default is True.
            correlation_id: Optional correlation ID for request tracing

        Returns:
            The File ID of the updated file.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The store_connector_id doesn't exist (404)
                - The store_file_id doesn't exist (404)
                - The project_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)
            ValueError: If required parameters are missing or invalid

        Example:
            ```python
            import asyncio
            from airia import AiriaAsyncClient

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Update existing file
                updated_file_id = await client.store.update_file(
                    store_connector_id="your_store_connector_id",
                    store_file_id="your_store_file_id",
                    project_id="your_project_id",
                    file_path="document.pdf"
                )

            asyncio.run(main())
            ```
        """
        request_data = self._pre_update_file(
            store_connector_id=store_connector_id,
            store_file_id=store_file_id,
            project_id=project_id,
            file_path=file_path,
            pending_ingestion=pending_ingestion,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )

        try:
            response = await self._request_handler.make_request_multipart(
                "PUT", request_data
            )
            return response["fileId"]
        finally:
            request_data.files["File"][1].close()

    async def get_file(
        self,
        project_id: str,
        file_id: str,
        correlation_id: Optional[str] = None,
    ) -> GetFileResponse:
        """
        Retrieve a file from the Airia store asynchronously.

        This method retrieves file information, download URL, and preview information
        for a specific file in the given project.

        Args:
            project_id: The unique identifier of the project (GUID format)
            file_id: The unique identifier of the file (GUID format)
            correlation_id: Optional correlation ID for request tracing

        Returns:
            GetFileResponse: File information including metadata, download info, and preview info

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The project_id doesn't exist (404)
                - The file_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)
            ValueError: If required parameters are missing or invalid

        Example:
            ```python
            import asyncio
            from airia import AiriaAsyncClient

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Get file information
                file_info = await client.store.get_file(
                    project_id="your_project_id",
                    file_id="your_file_id"
                )

                # Access file metadata
                if file_info.file:
                    print(f"File name: {file_info.file.name}")
                    print(f"File size: {file_info.file.size}")
                    print(f"Status: {file_info.file.status}")

                # Access download URL
                if file_info.downloadInfo:
                    print(f"Download URL: {file_info.downloadInfo.url}")

                # Access preview information
                if file_info.previewInfo:
                    print(f"Preview URL: {file_info.previewInfo.previewUrl}")

            asyncio.run(main())
            ```

        Note:
            The response includes three optional components:
            - file: File metadata and processing status
            - downloadInfo: Direct download URL for the file
            - previewInfo: Preview URL and connector information
        """
        request_data = self._pre_get_file(
            project_id=project_id,
            file_id=file_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )

        response = await self._request_handler.make_request(
            "GET", request_data, return_json=True
        )

        return GetFileResponse(**response)

    async def get_files(
        self,
        project_id: str,
        store_connector_id: str,
        correlation_id: Optional[str] = None,
    ) -> GetFilesResponse:
        """
        Retrieve all files from a store connector in the Airia store asynchronously.

        This method retrieves information about all files in the specified store connector
        and project, including file metadata, download URLs, and processing status.

        Args:
            project_id: The unique identifier of the project (GUID format)
            store_connector_id: The unique identifier of the store connector (GUID format)
            correlation_id: Optional correlation ID for request tracing

        Returns:
            GetFilesResponse: List of files with metadata, download info, and total count

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The project_id doesn't exist (404)
                - The store_connector_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)
            ValueError: If required parameters are missing or invalid

        Example:
            ```python
            import asyncio
            from airia import AiriaAsyncClient

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Get all files from a store connector
                files_response = await client.store.get_files(
                    project_id="your_project_id",
                    store_connector_id="your_store_connector_id"
                )

                # Access files list
                if files_response.files:
                    for file in files_response.files:
                        print(f"File: {file.name}, Status: {file.status}, Size: {file.size}")

                # Access download URLs
                if files_response.downloadInfos:
                    for download_info in files_response.downloadInfos:
                        print(f"File ID: {download_info.fileId}, URL: {download_info.url}")

                # Access total count
                print(f"Total files: {files_response.totalCount}")

            asyncio.run(main())
            ```

        Note:
            The response includes:
            - files: List of file metadata and processing status
            - downloadInfos: List of direct download URLs for files
            - totalCount: Total number of files in the store connector
        """
        request_data = self._pre_get_files(
            project_id=project_id,
            store_connector_id=store_connector_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )

        response = await self._request_handler.make_request(
            "GET", request_data, return_json=True
        )

        return GetFilesResponse(**response)

    async def delete_file(
        self,
        project_id: str,
        file_id: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Delete a file from the Airia store asynchronously.

        This method deletes a specific file from the given project.

        Args:
            project_id: The unique identifier of the project (GUID format)
            file_id: The unique identifier of the file to delete (GUID format)
            correlation_id: Optional correlation ID for request tracing

        Returns:
            None

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The project_id doesn't exist (404)
                - The file_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)
            ValueError: If required parameters are missing or invalid

        Example:
            ```python
            import asyncio
            from airia import AiriaAsyncClient

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Delete a file
                await client.store.delete_file(
                    project_id="your_project_id",
                    file_id="your_file_id"
                )

            asyncio.run(main())
            ```
        """
        request_data = self._pre_delete_file(
            project_id=project_id,
            file_id=file_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )

        await self._request_handler.make_request(
            "DELETE", request_data, return_json=False
        )
