from typing import List, Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BaseDeployments:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_get_deployments(
        self,
        tags: Optional[List[str]] = None,
        is_recommended: Optional[bool] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V2.value,
    ):
        """
        Prepare request data for retrieving deployments.

        This internal method constructs the URL and query parameters for deployment
        retrieval requests, including optional filtering by tags and recommendation status.

        Args:
            tags: Optional list of tags to filter deployments by
            is_recommended: Optional filter by recommended status
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the deployments endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )

        url = urljoin(
            self._request_handler.base_url, f"{api_version}/Deployments/paged"
        )

        # Build query parameters
        params = {}
        if tags is not None:
            params["tags"] = tags
        if is_recommended is not None:
            params["isRecommended"] = is_recommended

        request_data = self._request_handler.prepare_request(
            url=url, params=params, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_deployment(
        self,
        deployment_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for retrieving a single deployment.

        This internal method constructs the URL for deployment retrieval
        by ID using the specified API version.

        Args:
            deployment_id: The unique identifier of the deployment to retrieve
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the deployment endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )

        url = urljoin(
            self._request_handler.base_url, f"{api_version}/Deployments/{deployment_id}"
        )

        request_data = self._request_handler.prepare_request(
            url=url, correlation_id=correlation_id
        )

        return request_data
