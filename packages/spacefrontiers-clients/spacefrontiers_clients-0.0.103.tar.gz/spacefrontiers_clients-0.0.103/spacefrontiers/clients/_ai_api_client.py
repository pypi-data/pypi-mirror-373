import asyncio
import typing

import grpc
from aiogrpcclient import BaseGrpcClient
from izihawa_loglib.request_context import RequestContext

from .protos.service_pb2 import (
    EmbedRequest,
    EmbedResponse,
    RerankRequest,
    RerankResponse,
)
from .protos.service_pb2_grpc import EmbedStub, OcrStub, RerankStub


class AiApiClient(BaseGrpcClient):
    stub_clses = {
        "embed": EmbedStub,
        "ocr": OcrStub,
        "rerank": RerankStub,
    }

    def __init__(
        self,
        endpoint: str = "grpc-api.spacefrontiers.org:443",
        api_key: str = None,
        max_attempts: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 30.0,
        backoff_multiplier: float = 2.0,
        retryable_status_codes: tuple[str] = ("CANCELLED", "UNAVAILABLE"),
        keepalive_time_ms: int = 15000,
        keepalive_timeout_ms: int = 30000,
        connection_timeout: float = None,
        max_message_length: int = 1024 * 1024 * 1024,
        compression=grpc.Compression.Gzip,
        extra_options: list[tuple[str, typing.Any]] | None = None,
    ):
        """Initialize the AI API client with gRPC connection settings.

        Args:
            endpoint: The gRPC server endpoint in the format 'host:port'.
            api_key: Optional API key for authentication.
            max_attempts: Maximum number of retry attempts for failed requests (default: 3).
            initial_backoff: Initial delay in seconds before first retry (default: 1.0).
            max_backoff: Maximum delay in seconds between retries (default: 30.0).
            backoff_multiplier: Multiplier applied to delay between consecutive retries (default: 2.0).
            retryable_status_codes: Tuple of gRPC status codes that trigger retry attempts (default: ("CANCELLED", "UNAVAILABLE")).
            connection_timeout: Maximum time in seconds to wait for connection establishment.
                              If None, uses the default gRPC timeout.
            max_message_length: Maximum size of gRPC messages in bytes (default: 1GB).
            compression: gRPC compression algorithm to use. If None, no compression is applied.
            extra_options: Additional gRPC channel options as list of (key, value) tuples.
        """

        super().__init__(
            endpoint=endpoint,
            max_attempts=max_attempts,
            initial_backoff=initial_backoff,
            max_backoff=max_backoff,
            backoff_multiplier=backoff_multiplier,
            retryable_status_codes=retryable_status_codes,
            keepalive_time_ms=keepalive_time_ms,
            keepalive_timeout_ms=keepalive_timeout_ms,
            connection_timeout=connection_timeout,
            max_message_length=max_message_length,
            compression=compression,
            extra_options=extra_options,
        )
        self._api_key = api_key

    def _prepare_metadata(
        self, request_context: RequestContext | None = None
    ) -> list[tuple[str, typing.Any]]:
        """Prepare gRPC metadata with optional request context.

        Args:
            request_context: Optional RequestContext object containing request_id and session_id

        Returns:
            List of metadata key-value tuples
        """
        metadata = []
        if request_context:
            if hasattr(request_context, "request_id"):
                metadata.append(("x-request-id", request_context.request_id))
            if hasattr(request_context, "request_source"):
                metadata.append(("x-request-source", request_context.request_source))
            if hasattr(request_context, "session_id"):
                metadata.append(("x-session-id", request_context.session_id))
        if self._api_key is not None:
            metadata.append(("x-api-key", self._api_key))
        return metadata

    async def embed(
        self,
        embed_request: EmbedRequest,
        chunk_size: int = 17,
        request_context: RequestContext | None = None,
    ) -> EmbedResponse:
        """Generate embeddings for a list of texts.

        Args:
            embed_request: EmbedRequest containing texts and task type (one of "classification", "retrieval.passage", "retrieval.query", "separation" or "text-matching")
            chunk_size: Number of texts to process in each batch (default: 17)
            request_context: Optional RequestContext object for request tracking

        Returns:
            EmbedResponse containing embeddings for each text and total token count
        """
        metadata = self._prepare_metadata(request_context)
        splitted_embed_responses = await asyncio.gather(
            *[
                self.stubs["embed"].embed(
                    EmbedRequest(
                        texts=embed_request.texts[i : i + chunk_size],
                        task=embed_request.task,
                    ),
                    metadata=metadata,
                )
                for i in range(0, len(embed_request.texts), chunk_size)
            ]
        )
        embeddings = []
        processed_tokens = 0
        for splitted_embed_response in splitted_embed_responses:
            embeddings.extend(splitted_embed_response.embeddings)
            processed_tokens += splitted_embed_response.processed_tokens
        return EmbedResponse(
            embeddings=embeddings,
            processed_tokens=processed_tokens,
        )

    async def rerank(
        self,
        rerank_request: RerankRequest,
        chunk_size: int = 17,
        request_context: RequestContext | None = None,
    ) -> RerankResponse:
        """Rerank a list of texts based on their relevance to a query.

        Args:
            rerank_request: RerankRequest containing query and texts to rerank
            chunk_size: Number of texts to process in each batch (default: 17)
            request_context: Optional RequestContext object for request tracking

        Returns:
            RerankResponse containing scores for each text and total token count
        """
        metadata = self._prepare_metadata(request_context)
        splitted_rerank_responses = await asyncio.gather(
            *[
                self.stubs["rerank"].rerank(
                    RerankRequest(
                        query=rerank_request.query,
                        texts=rerank_request.texts[i : i + chunk_size],
                    ),
                    metadata=metadata,
                )
                for i in range(0, len(rerank_request.texts), chunk_size)
            ]
        )
        scores = []
        processed_tokens = 0
        for splitted_rerank_response in splitted_rerank_responses:
            scores.extend(splitted_rerank_response.scores)
            processed_tokens += splitted_rerank_response.processed_tokens
        for i, score in enumerate(scores):
            score.index = i
        return RerankResponse(scores=scores, processed_tokens=processed_tokens)
