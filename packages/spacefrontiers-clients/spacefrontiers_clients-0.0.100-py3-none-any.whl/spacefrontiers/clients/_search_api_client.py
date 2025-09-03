from aiobaseclient import BaseStandardClient
from izihawa_loglib.request_context import RequestContext
from izihawa_utils.common import filter_none

from spacefrontiers.clients.types import (
    ConversationRequest,
    ConversationResponse,
    SearchRequest,
    SearchResponse,
    SimilarRequest,
    SimpleSearchRequest,
)


class SearchApiClient(BaseStandardClient):
    """Client for interacting with the Search API.

    A client that handles communication with the Search API endpoints, including authentication
    and request handling.

    Args:
        base_url (str): The base URL of the Search API.
        api_key (str | None, optional): API key for authentication. Defaults to None.
        user_id (str | int | None, optional): User ID of the user. Defaults to None.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 2.
        retry_delay (float, optional): Delay between retry attempts in seconds. Defaults to 0.5.
    """

    def __init__(
        self,
        base_url: str = "https://api.spacefrontiers.org",
        api_key: str | None = None,
        user_id: str | int | None = None,
        max_retries: int = 2,
        retry_delay: float = 0.5,
        default_headers: dict[str, str] | None = None,
    ):
        """Initialize the SearchApiClient.

        Args:
            base_url (str): The base URL of the Search API.
            api_key (str | None, optional): API key for authentication. Defaults to None.
            user_id (str | int | None, optional): User ID of the user. Defaults to None.
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 2.
            retry_delay (float, optional): Delay between retry attempts in seconds. Defaults to 0.5.
            default_headers (dict[str, str] | None, optional): Default headers for requests. Defaults to None.
        """
        if default_headers is None:
            default_headers = {}
        default_headers.update(self._build_headers(api_key, user_id))
        super().__init__(
            base_url=base_url,
            default_headers=default_headers,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    def _build_headers(
        self,
        api_key: str | None = None,
        user_id: str | int | None = None,
    ) -> dict[str, str]:
        headers = {}
        if api_key is not None:
            headers["X-Api-Key"] = api_key
        if user_id is not None:
            headers["X-User-Id"] = str(user_id)
        return headers

    async def search(
        self,
        search_request: SearchRequest,
        request_context: RequestContext | None = None,
        timeout: float = 600.0,
        api_key: str | None = None,
        user_id: str | int | None = None,
    ) -> SearchResponse:
        """Execute a semantic search request with reranking and other advanced features.

        This method performs a full semantic search with capabilities like reranking,
        filtering, and other advanced search features.

        Args:
            search_request (SearchRequest): The search request parameters.
            request_context (RequestContext): Context for the request with tracking information.
            timeout (float, optional): Request timeout in seconds. Defaults to 600.0.

        Returns:
            SearchResponse: The search response containing results.
        """
        response = await self.post(
            "/v1/search/",
            json=filter_none(search_request.model_dump(exclude_none=True)),
            timeout=timeout,
            request_context=request_context,
            headers=self._build_headers(api_key, user_id),
        )
        return SearchResponse(**response)

    async def simple_search(
        self,
        simple_search_request: SimpleSearchRequest,
        request_context: RequestContext | None = None,
        timeout: float = 600.0,
        api_key: str | None = None,
        user_id: str | int | None = None,
    ) -> SearchResponse:
        """Execute a full-text search request with support for expert syntax.

        This method performs a simple full-text search that allows for expert query syntax
        to be used for more precise searching.

        Args:
            simple_search_request (SimpleSearchRequest): The simple search request parameters.
            request_context (RequestContext): Context for the request with tracking information.
            timeout (float, optional): Request timeout in seconds. Defaults to 600.0.

        Returns:
            SearchResponse: The search response containing results.
        """
        response = await self.post(
            "/v1/search/simple/",
            json=filter_none(simple_search_request.model_dump(exclude_none=True)),
            timeout=timeout,
            request_context=request_context,
            headers=self._build_headers(api_key, user_id),
        )
        return SearchResponse(**response)

    async def get_document_by_doi(
        self,
        doi: str,
        request_context: RequestContext | None = None,
        timeout: float = 600.0,
        api_key: str | None = None,
        user_id: str | int | None = None,
    ) -> dict:
        """Execute a full-text search request with support for expert syntax.

        This method performs a simple full-text search that allows for expert query syntax
        to be used for more precise searching.

        Args:
            doi (str): DOI.
            request_context (RequestContext): Context for the request with tracking information.
            timeout (float, optional): Request timeout in seconds. Defaults to 600.0.

        Returns:
            dict: Document
        """
        return await self.get(
            f"/v1/documents/doi/{doi}",
            timeout=timeout,
            request_context=request_context,
            headers=self._build_headers(api_key, user_id),
        )

    async def post_conversations(
        self,
        conversation_request: ConversationRequest,
        timeout: float = 60.0,
        request_context: RequestContext | None = None,
        api_key: str | None = None,
        user_id: str | int | None = None,
    ) -> ConversationResponse:
        """Execute a conversation search request.

        Args:
            conversation_request (ConversationRequest): The conversation request parameters.
            timeout (float, optional): Request timeout in seconds. Defaults to 60.0.
            request_context (RequestContext | None, optional): Context for the request. Defaults to None.

        Returns:
            ConversationResponse: The conversation response
        """
        response = await self.post(
            "/v1/conversations/",
            json=filter_none(conversation_request.model_dump(exclude_none=True)),
            request_context=request_context,
            timeout=timeout,
            headers=self._build_headers(api_key, user_id),
        )
        return ConversationResponse(**response)

    async def similar(
        self,
        similar_request: SimilarRequest,
        request_context: RequestContext | None = None,
        api_key: str | None = None,
        user_id: str | int | None = None,
    ) -> SearchResponse:
        response = await self.post(
            "/v1/search/similar/",
            json=filter_none(similar_request.model_dump(exclude_none=True)),
            request_context=request_context,
            headers=self._build_headers(api_key, user_id),
        )
        return SearchResponse(**response)
