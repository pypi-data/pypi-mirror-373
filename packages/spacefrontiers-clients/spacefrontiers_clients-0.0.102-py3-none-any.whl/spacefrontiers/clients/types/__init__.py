import time
import typing
from datetime import datetime
from typing import Annotated, Literal, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

StrBool = Annotated[
    bool, PlainSerializer(lambda x: str(x), return_type=str, when_used="unless-none")
]
SourceName = Literal[
    "library",
    "reddit",
    "telegram",
]
ModelName = Literal[
    "google/gemini-2.5-flash",
    "google/gemini-2.5-flash-lite",
    "google/gemini-2.5-pro",
    "moonshotai/kimi-k2",
    "openai/gpt-4.1",
    "openai/gpt-5",
    "qwen/qwen3-235b-a22b",
    "x-ai/grok-4",
    "z-ai/glm-4.5",
]
FilterValue = Union[
    str, int, float, Tuple[Union[int, float, str], Union[int, float, str]]
]
FilterField = Literal[
    "ids",
    "uris",
    "type",
    "languages",
    "issued_at",
    "references.doi",
    "telegram_channel_usernames",
    "metadata.issns",
    "metadata.publisher",
    "metadata.volume",
    "metadata.issue",
    "metadata.series",
    "metadata.is_pmc",
    "metadata.is_pubmed",
    "metadata.author",
    "metadata.subreddit",
    "document_id",
    "field",
]
FiltersType = dict[FilterField, list[FilterValue]] | None


class PromptValue(BaseModel):
    value: str
    prompt_type: Literal["value"] = "value"


class PromptName(BaseModel):
    value: Literal[
        "request",
        "digest",
        "news",
    ] = "request"
    prompt_type: Literal["name"] = "name"


class Snippet(BaseModel):
    """A class representing a text snippet from a document."""

    field: str = Field(
        description="The field name from which the snippet was extracted"
    )
    text: str = Field(description="The actual text content of the snippet")
    payload: dict | None = Field(
        default=None, description="Additional metadata associated with the snippet"
    )
    score: float = Field(
        default=0.0, description="Relevance or ranking score of the snippet"
    )


class SearchDocument(BaseModel):
    """A class representing a search result document containing snippets."""

    source: SourceName = Field(description="The source identifier of the document")
    document: dict = Field(description="The complete document data")
    snippets: list[Snippet] = Field(description="List of snippets from the document")
    score: float = Field(
        default=0.0, description="Overall relevance or ranking score of the document"
    )

    def join_snippet_texts(
        self, separator: str = " <...> ", strip_snippets_fn=None
    ) -> str:
        """Joins the text of multiple snippets with intelligent separators.

        Consecutive snippets (based on chunk_id) are joined with a space,
        while non-consecutive snippets are joined with the specified separator.

        Args:
            separator (str): The separator to use between non-consecutive snippets.
                Defaults to " <...> ".

        Returns:
            str: The concatenated snippet texts with appropriate separators.
        """
        parts = []
        snippets = self.snippets

        if strip_snippets_fn:
            ordered_snippets = list(
                sorted(snippets, key=lambda x: x.score, reverse=True)
            )
            ordered_snippets = strip_snippets_fn(ordered_snippets)
            snippets = list(
                sorted(
                    ordered_snippets,
                    key=lambda x: (x.payload["field"], x.payload["chunk_id"]),
                )
            )

        for i, snippet in enumerate(snippets):
            if i > 0:
                if (
                    snippets[i - 1].payload["chunk_id"] + 1
                    == snippets[i].payload["chunk_id"]
                ):
                    parts.append(" ")
                else:
                    parts.append(separator)
            parts.append(snippet.text)

        return "".join(parts)


class SimpleSearchRequest(BaseModel):
    """A class representing a search request configuration."""

    query: str | None = Field(
        default=None,
        description="search query string",
    )
    source: SourceName = Field(description="Data source to search in")
    query_language: str | None = Field(
        default=None,
        description="Two-letter lowercased language code of the query for enabling language-specific processing",
    )
    limit: int = Field(
        default=10, ge=0, le=100, description="Maximum number of results to return"
    )
    offset: int = Field(
        default=0, ge=0, le=100, description="Number of results to skip for pagination"
    )
    filters: FiltersType | None = Field(
        default=None, description="Filters to apply to results"
    )
    scoring: Literal["default", "temporal"] = Field(
        default="default",
        description="Scoring for ranking documents, `temporal` is for ordering descending by date",
    )
    mode: typing.Literal["and", "or"] = "and"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": '+(dermatomyositis myositis "inflammatory myopathy" inflammatory myopathies) +(JAK "janus kinase" tofacitinib baricitinib ruxolitinib upadacitinib filgotinib)',
                    "source": "library",
                    "limit": 30,
                    "offset": 0,
                },
                {
                    "query": "To kill a Mockingbird",
                    "source": "library",
                    "limit": 5,
                },
                {
                    "query": "JAK",
                    "source": "library",
                    "limit": 30,
                    "offset": 0,
                    "filters": {
                        "ids": ["10.1136/annrheumdis-2020-218690"],
                    },
                },
            ]
        }
    }


class SearchResponse(BaseModel):
    """A class representing the response from a search request."""

    search_documents: list[SearchDocument] = Field(
        description="List of retrieved documents with their snippets"
    )
    count: int = Field(description="Number of results found")
    has_next: bool = Field(description="Whether there are more results available")
    total_count: int | None = Field(
        default=None,
        description="Maximal possible number of records stored in the database",
    )

    @staticmethod
    def empty_response() -> "SearchResponse":
        """
        Creates and returns an empty search response
        """
        return SearchResponse(
            search_documents=[],
            count=0,
            has_next=False,
        )


class BaseChunk(BaseModel):
    """A class representing a base chunk of text from a document."""

    document_id: str = Field(description="Unique identifier for the source document")
    field: str = Field(description="The field name containing the chunk")
    chunk_id: int = Field(
        description="Sequential identifier for the chunk within the document"
    )
    start_index: int = Field(
        description="Starting character position of the chunk in the field"
    )
    length: int = Field(description="Length of the chunk in characters")
    metadata: dict = Field(description="Additional metadata associated with the chunk")
    updated_at: int = Field(
        default_factory=lambda: int(time.time()),
        description="Timestamp of when the chunk was last updated",
    )
    uris: list[str] | None = Field(description="Uris of the document", default=None)

    def get_unique_id(self) -> str:
        """Generates a unique identifier for the chunk.

        Returns:
            str: A unique string identifier combining document_id, field, and chunk_id
                in the format 'document_id@field@chunk_id'
        """
        return f"{self.document_id}@{self.field}@{self.chunk_id}"


class PreparedChunk(BaseChunk):
    """A prepared chunk that includes the actual text content."""

    text: str = Field(description="The actual text content of the chunk")


class LlmConfig(BaseModel):
    """Configuration for the Language Learning Model."""

    model_name: ModelName = Field(description="Name of the language learning model")
    api_key: str | None = Field(
        default=None, description="API key for accessing the model"
    )
    max_context_length: int | None = Field(
        default=None, description="Maximum context length for the model"
    )

    model_config = ConfigDict(protected_namespaces=tuple())


class Range(BaseModel):
    """A class representing a numeric range with left and right bounds."""

    left: int = Field(description="The lower bound of the range")
    right: int = Field(description="The upper bound of the range")


class Query(BaseModel):
    """A class representing a search query with various metadata and processing options."""

    original_query: str | None = Field(default=None, description="Original user query")
    reformulated_query: str | None = Field(
        default=None, description="Reformulated user query"
    )
    keywords: list[str] = Field(
        default_factory=list, description="Extracted or relevant keywords"
    )
    filters: dict[str, list[str]] | None = Field(
        default=None, description="Filters to apply to results"
    )
    is_recent: bool = Field(
        default=False, description="Flag for recent content queries"
    )
    is_event: bool = Field(
        default=False, description="Flag for event or location queries"
    )
    date: tuple[datetime, datetime] | None = Field(
        default=None, description="Date range for temporal queries"
    )
    content_type: str | None = Field(
        default=None, description="Type of content to search for"
    )
    related_queries: list[str] = Field(
        default_factory=list, description="List of related search queries"
    )
    query_language: str | None = Field(
        default=None, description="Two-letter language code of the query"
    )
    instruction: str | None = Field(
        default=None, description="User instruction on how to render answer"
    )
    knowledge_source: Literal["search", "no_search"] | None = Field(
        default="search", description="The source of knowledge for the query"
    )
    classified_aspects: list[str] = Field(
        default_factory=list, description="Extracted or relevant keywords"
    )
    title: str | None = Field(default=None, description="Generated conversation title")

    @staticmethod
    def default_query(query: str | None) -> "Query":
        """Creates a default Query object with minimal configuration."""
        return Query(
            original_query=query,
            reformulated_query=query,
        )

    def __format__(self, __format_spec: str) -> str:
        return str(self)

    def __str__(self) -> str:
        if self.reformulated_query:
            return str(self.reformulated_query)
        elif self.original_query:
            return str(self.original_query)
        else:
            return "<no-query>"


class QueryClassifierConfig(BaseModel):
    """Configuration for query classification."""

    related_queries: int = Field(
        default=0, description="Number of related queries to generate"
    )


class NewsRequest(BaseModel):
    """A class representing a news request with a query."""

    topic: str = Field(description="Topic for the news")
    filters: FiltersType | None = Field(
        default=None,
        description="Filters to apply to results",
    )


class NewsResponse(BaseModel):
    """Response from the news endpoint."""

    items: list[dict] = Field(description="News items")
    search_documents: list[SearchDocument] = Field(
        description="List of retrieved and processed documents"
    )


class ConversationRequest(BaseModel):
    """A class representing a conversation request with an identifier and query."""

    query: str = Field(description="The query or message text for the conversation")
    llm_config: LlmConfig = Field(
        description="Language model configuration for classification"
    )
    sources_filters: dict[SourceName, FiltersType | None] = Field(
        description="The dict of sources and filters to use", default=None
    )
    prompt: PromptValue | PromptName = Field(
        default_factory=PromptName,
        description="Representation of the requested response",
        discriminator="prompt_type",
    )
    limit: int = Field(
        default=10,
        gt=0,
        le=200,
        description="An **approximate** limit of scoring chunks across all sources.",
    )
    id: str | None = Field(
        default=None, description="Unique identifier for the conversation"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What are side-effects of aspirin?",
                    "llm_config": {"model_name": "google/gemini-2.5-flash"},
                    "sources_filters": {"library": {}},
                    "limit": 30,
                },
                {
                    "query": "What has happened yesterday?",
                    "sources_filters": {"telegram": {}},
                    "llm_config": {"model_name": "google/gemini-2.5-flash"},
                    "limit": 30,
                },
            ]
        }
    }


class ConversationResponse(BaseModel):
    """Response from the search and processing conversation."""

    id: str = Field(description="Unique identifier for the conversation")
    answer: str = Field(description="The answer to the query")
    search_documents: list[SearchDocument] = Field(
        description="List of retrieved and processed documents"
    )
    heading: str | None = Field(default=None, description="Heading of the conversation")
    query: Query | None = Field(default=None, description="Processed query information")


class SearchRequest(BaseModel):
    """A class representing a search request with configuration options."""

    query: str = Field(description="The search query string")
    sources_filters: dict[SourceName, FiltersType | None] = Field(
        description="The dict of sources and filters to use"
    )
    limit: int = Field(
        default=10,
        gt=0,
        le=200,
        description="An **approximate** limit of scoring chunks",
    )
    is_reranking_enabled: bool = Field(
        default=True, description="Should we pass documents through reranker or not."
    )
    refining_target: int | None = Field(
        default=10,
        description="Should we pass documents through additional refinement or not.",
    )
    possible_languages: list[str] | None = Field(
        default=None,
        description="Possible languages of the user for language-specific processing",
    )
    query_classifier: QueryClassifierConfig | None = Field(
        default=None, description="Configuration for query classification"
    )
    mode: typing.Literal["and", "or"] = "and"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What are side-effects of aspirin?",
                    "sources_filters": {"library": {}},
                    "is_reranking_enabled": True,
                    "limit": 10,
                },
                {
                    "query": "What has happened yesterday?",
                    "sources_filters": {"telegram": {}},
                    "is_reranking_enabled": False,
                    "limit": 10,
                },
            ]
        }
    }


class SimilarRequest(BaseModel):
    """Configuration for recommendation requests.

    Attributes:
        positive_ids (list[str]): List of document IDs used as positive examples
    """

    positive_ids: list[str] = Field(default_factory=lambda: [])
    positive_uris: list[str] = Field(default_factory=lambda: [])
    sources: list[str]
    limit: int = Field(default=10, gt=0, le=100)
    filters: FiltersType = Field(
        default=None, description="Dictionary of filters to apply to the search"
    )
