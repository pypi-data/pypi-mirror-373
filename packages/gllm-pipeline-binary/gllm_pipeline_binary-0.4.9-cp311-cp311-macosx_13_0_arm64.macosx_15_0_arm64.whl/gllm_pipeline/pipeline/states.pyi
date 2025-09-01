from _typeshed import Incomplete
from gllm_core.event.event_emitter import EventEmitter
from pydantic import BaseModel
from typing import Any, TypedDict

class RAGState(TypedDict):
    '''A TypedDict representing the state of a Retrieval-Augmented Generation (RAG) pipeline.

    This docstring documents the original intention of each of the attributes in the TypedDict.
    However, in practice, the attributes may be modified or extended to suit the specific requirements of the
    application. The TypedDict is used to enforce the structure of the state object.

    Attributes:
        user_query (str): The original query from the user.
        queries (list[str]): A list of queries generated for retrieval.
        retrieval_params (dict[str, Any]): Parameters used for the retrieval process.
        chunks (list): A list of chunks retrieved from the knowledge base.
        history (list[Any]): The history of the conversation or interaction.
        context (str): The context information used for generating responses.
        response_synthesis_bundle (dict[str, Any]): Data used for synthesizing the final response.
        response (str): The generated response to the user\'s query.
        references (str | list[str]): References or sources used in generating the response.
        event_emitter (EventEmitter): An event emitter instance for logging purposes.

    Example:
        ```python
        state = {
            "user_query": "What is machine learning?",
            "queries": ["machine learning definition", "ML basics"],
            "retrieval_params": {"top_k": 5, "threshold": 0.8},
            "chunks": [
                {"content": "Machine learning is...", "score": 0.95},
                {"content": "ML algorithms include...", "score": 0.87}
            ],
            "history": [
                {"role": "user", "contents": ["What is machine learning?"]},
                {"role": "assistant", "contents": ["Machine learning is a subset of artificial intelligence..."]}
            ],
            "context": "Retrieved information about ML",
            "response_synthesis_bundle": {"template": "informative"},
            "response": "Machine learning is a subset of artificial intelligence...",
            "references": ["source1.pdf", "article2.html"],
            "event_emitter": EventEmitter()
        }
        ```
    '''
    user_query: str
    queries: list[str]
    retrieval_params: dict[str, Any]
    chunks: list[Any]
    history: list[Any]
    context: str
    response_synthesis_bundle: dict[str, Any]
    response: str
    references: str | list[str]
    event_emitter: EventEmitter

class RAGStateModel(BaseModel):
    '''A Pydantic BaseModel representing the state of a Retrieval-Augmented Generation (RAG) pipeline.

    This implementation provides runtime validation, default values, and enhanced type safety
    compared to the TypedDict version. It maintains compatibility with LangGraph while offering
    improved developer experience through automatic validation and sensible defaults.

    Attributes:
        user_query (str): The original query from the user.
        queries (list[str]): A list of queries generated for retrieval. Defaults to empty list.
        retrieval_params (dict[str, Any]): Parameters used for the retrieval process. Defaults to empty dict.
        chunks (list[Any]): A list of chunks retrieved from the knowledge base. Defaults to empty list.
        history (list[Any]): The history of the conversation or interaction. Defaults to empty list.
        context (str): The context information used for generating responses. Defaults to empty string.
        response_synthesis_bundle (dict[str, Any]): Data used for synthesizing the final response.
            Defaults to empty dict.
        response (str): The generated response to the user\'s query. Defaults to empty string.
        references (str | list[str]): References or sources used in generating the response.
            Defaults to empty list.
        event_emitter (EventEmitter | None): An event emitter instance for logging purposes. Defaults to None.

    Example:
        ```python
        # Basic usage with minimal required fields
        state = RAGStateModel(user_query="What is machine learning?")

        # Full usage with all fields
        state = RAGStateModel(
            user_query="What is machine learning?",
            queries=["machine learning definition", "ML basics"],
            retrieval_params={"top_k": 5, "threshold": 0.8},
            chunks=[
                {"content": "Machine learning is...", "score": 0.95},
                {"content": "ML algorithms include...", "score": 0.87}
            ],
            history=[
                {"role": "user", "contents": ["What is machine learning?"]},
                {"role": "assistant", "contents": ["Machine learning is a subset of artificial intelligence..."]}
            ],
            context="Retrieved information about ML",
            response_synthesis_bundle={"template": "informative"},
            response="Machine learning is a subset of artificial intelligence...",
            references=["source1.pdf", "article2.html"],
            event_emitter=EventEmitter()
        )

        # Convert to dictionary for pipeline processing
        state_dict = state.model_dump()

        # Use with json_encoders for special types
        state_json = state.model_dump_json()
        ```

    Example with custom JSON encoders:
        ```python
        from datetime import datetime
        from pydantic import BaseModel, Field

        class CustomStateModel(BaseModel):
            timestamp: datetime = Field(default_factory=datetime.now)

            class Config:
                json_encoders = {
                    datetime: lambda v: v.isoformat(),
                    EventEmitter: lambda v: str(v) if v else None
                }
        ```
    '''
    user_query: str
    queries: list[str]
    retrieval_params: dict[str, Any]
    chunks: list[Any]
    history: list[Any]
    context: str
    response_synthesis_bundle: dict[str, Any]
    response: str
    references: str | list[str]
    event_emitter: EventEmitter | None
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed: bool
        json_encoders: Incomplete
