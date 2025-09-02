import os
from mimetypes import guess_type
from typing import Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BaseStore:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_upload_file(
        self,
        store_connector_id: str,
        project_id: str,
        file_path: str,
        folder_id: Optional[str] = None,
        pending_ingestion: bool = True,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for file upload endpoint.

        This internal method constructs the URL for file upload requests
        and prepares the multipart form data payload.

        Args:
            store_connector_id: ID of the store connector
            project_id: ID of the project
            file_path: Path to the file on disk
            folder_id: Optional folder ID
            pending_ingestion: Whether the file is pending ingestion
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the file upload endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self._request_handler.base_url, f"{api_version}/Store/UploadFile")

        payload = {
            "StoreConnectorId": store_connector_id,
            "ProjectId": project_id,
            "PendingIngestion": str(pending_ingestion).lower(),
            "FolderId": folder_id or "",
        }
        files = {
            "File": (
                os.path.basename(file_path),
                open(file_path, "rb"),
                guess_type(file_path)[0],
            )
        }

        request_data = self._request_handler.prepare_request(
            url, payload=payload, files=files, correlation_id=correlation_id
        )

        return request_data

    def _pre_update_file(
        self,
        store_connector_id: str,
        store_file_id: str,
        project_id: str,
        file_path: str,
        pending_ingestion: bool = True,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for file update endpoint.

        This internal method constructs the URL for file update requests
        and prepares the multipart form data payload.

        Args:
            store_connector_id: ID of the store connector
            store_file_id: ID of the file to update
            project_id: ID of the project
            file_path: Path to the file on disk
            pending_ingestion: Whether the file is pending ingestion
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the file update endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self._request_handler.base_url, f"{api_version}/Store/UpdateFile")

        payload = {
            "StoreConnectorId": store_connector_id,
            "StoreFileId": store_file_id,
            "ProjectId": project_id,
            "PendingIngestion": str(pending_ingestion).lower(),
        }
        files = {
            "File": (
                os.path.basename(file_path),
                open(file_path, "rb"),
                guess_type(file_path)[0],
            )
        }

        request_data = self._request_handler.prepare_request(
            url, payload=payload, files=files, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_file(
        self,
        project_id: str,
        file_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for get file endpoint.

        This internal method constructs the URL for file retrieval requests.

        Args:
            project_id: ID of the project
            file_id: ID of the file
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the get file endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/Store/GetFile/{project_id}/{file_id}",
        )

        request_data = self._request_handler.prepare_request(
            url, payload=None, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_files(
        self,
        project_id: str,
        store_connector_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for get files endpoint.

        This internal method constructs the URL for files retrieval requests.

        Args:
            project_id: ID of the project
            store_connector_id: ID of the store connector
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the get files endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/Store/GetAllFiles/{project_id}/{store_connector_id}",
        )

        request_data = self._request_handler.prepare_request(
            url, payload=None, correlation_id=correlation_id
        )

        return request_data

    def _pre_delete_file(
        self,
        project_id: str,
        file_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for delete file endpoint.

        This internal method constructs the URL for file deletion requests.

        Args:
            project_id: ID of the project
            file_id: ID of the file to delete
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the delete file endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/Store/DeleteFile/{project_id}/{file_id}",
        )

        request_data = self._request_handler.prepare_request(
            url, payload=None, correlation_id=correlation_id
        )

        return request_data
