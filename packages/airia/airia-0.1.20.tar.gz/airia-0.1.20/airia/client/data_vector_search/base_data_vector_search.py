from typing import Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BaseDataVectorSearch:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_get_file_chunks(
        self,
        data_store_id: str,
        file_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for get file chunks endpoint.

        This internal method constructs the URL for file chunks retrieval requests.

        Args:
            data_store_id: ID of the data store
            file_id: ID of the file
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the get file chunks endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )

        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/DataVectorSearch/chunks/{data_store_id}/{file_id}",
        )

        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id, params={"pageNumber": 1, "pageSize": 50}
        )

        return request_data
