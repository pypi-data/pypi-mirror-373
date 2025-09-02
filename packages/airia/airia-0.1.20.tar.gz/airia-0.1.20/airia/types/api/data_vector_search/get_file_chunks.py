from typing import List, Optional

from pydantic import BaseModel, Field


class FileChunk(BaseModel):
    """Represents a chunk of a file with score and metadata.

    Attributes:
        path: Path of the chunk
        score: Optional relevance score for the chunk
        chunk: The text content of the chunk
        sequence_number: Optional sequence number of the chunk in the document
        document_id: Unique identifier of the document (GUID format)
        document_name: Name of the document
    """

    path: Optional[str] = None
    score: Optional[float] = None
    chunk: str
    sequence_number: Optional[int] = Field(None, alias="sequenceNumber")
    document_id: Optional[str] = Field(None, alias="documentId")
    document_name: Optional[str] = Field(None, alias="documentName")


class GetFileChunksResponse(BaseModel):
    """Response model for file chunks retrieval.

    Attributes:
        data_store_id: The data store identifier (GUID format)
        file_id: The file identifier (GUID format)
        chunks: List of chunks from the file
        page_number: Current page number
        page_size: Page size used for pagination
        total_count: Total count of chunks
        total_pages: Total number of pages
    """

    data_store_id: Optional[str] = Field(None, alias="dataStoreId")
    file_id: Optional[str] = Field(None, alias="fileId")
    chunks: List[FileChunk]
    page_number: int = Field(alias="pageNumber")
    page_size: int = Field(alias="pageSize")
    total_count: int = Field(alias="totalCount")
    total_pages: int = Field(alias="totalPages")
