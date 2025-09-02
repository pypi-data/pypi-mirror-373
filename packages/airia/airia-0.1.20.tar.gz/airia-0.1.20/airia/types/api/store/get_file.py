from typing import List, Optional

from pydantic import BaseModel, Field


class Timestamp(BaseModel):
    """Represents a timestamp with seconds and nanoseconds precision.

    Attributes:
        seconds: The number of seconds since the epoch
        nanos: The number of nanoseconds within the second
    """

    seconds: int
    nanos: int


class IngestionProcessingStatus(BaseModel):
    """Represents the processing status of a file during ingestion.

    Attributes:
        table_document_processing_mode: The processing mode for table documents
        user_errors: Optional list of user-related errors during processing
        system_errors: Optional list of system-related errors during processing
        status: The current processing status
    """

    table_document_processing_mode: str = Field(alias="tableDocumentProcessingMode")
    user_errors: Optional[List[str]] = Field(None, alias="userErrors")
    system_errors: Optional[List[str]] = Field(None, alias="systemErrors")
    status: str


class File(BaseModel):
    """Represents a file in the Airia system with metadata and processing information.

    Attributes:
        store_connector_id: Optional ID of the store connector
        parent_id: Optional ID of the parent file/folder
        has_parent_id: Whether the file has a parent ID
        id: Optional unique identifier for the file
        name: Optional name of the file
        size: Size of the file in bytes
        mime_type: Optional MIME type of the file
        path: Optional file path
        file_last_updated_at: Optional timestamp of last file update
        additional_metadata_json: Optional JSON string containing additional metadata
        has_additional_metadata_json: Whether the file has additional metadata
        file_hash: Optional hash of the file content
        status: Current status of the file
        user_errors: Optional list of user-related errors
        system_errors: Optional list of system-related errors
        folder_id: Optional ID of the containing folder
        has_folder_id: Whether the file has a folder ID
        external_id: Optional external identifier
        has_external_id: Whether the file has an external ID
        ingestion_duration: Duration of ingestion process in milliseconds
        has_ingestion_duration: Whether ingestion duration is available
        tokens_consumed: Number of tokens consumed during processing
        has_tokens_consumed: Whether token consumption data is available
        processing_message: Optional message about processing status
        has_processing_message: Whether a processing message is available
        processed_at: Optional timestamp when processing completed
        ingestion_processing_statuses: Optional list of processing statuses
    """

    store_connector_id: Optional[str] = Field(None, alias="storeConnectorId")
    parent_id: Optional[str] = Field(None, alias="parentId")
    has_parent_id: bool = Field(alias="hasParentId")
    id: Optional[str] = None
    name: Optional[str] = None
    size: int
    mime_type: Optional[str] = Field(None, alias="mimeType")
    path: Optional[str] = None
    file_last_updated_at: Optional[Timestamp] = Field(None, alias="fileLastUpdatedAt")
    additional_metadata_json: Optional[str] = Field(
        None, alias="additionalMetadataJson"
    )
    has_additional_metadata_json: bool = Field(alias="hasAdditionalMetadataJson")
    file_hash: Optional[str] = Field(None, alias="fileHash")
    status: str
    user_errors: Optional[List[str]] = Field(None, alias="userErrors")
    system_errors: Optional[List[str]] = Field(None, alias="systemErrors")
    folder_id: Optional[str] = Field(None, alias="folderId")
    has_folder_id: bool = Field(alias="hasFolderId")
    external_id: Optional[str] = Field(None, alias="externalId")
    has_external_id: bool = Field(alias="hasExternalId")
    ingestion_duration: int = Field(alias="ingestionDuration")
    has_ingestion_duration: bool = Field(alias="hasIngestionDuration")
    tokens_consumed: int = Field(alias="tokensConsumed")
    has_tokens_consumed: bool = Field(alias="hasTokensConsumed")
    processing_message: Optional[str] = Field(None, alias="processingMessage")
    has_processing_message: bool = Field(alias="hasProcessingMessage")
    processed_at: Optional[Timestamp] = Field(None, alias="processedAt")
    ingestion_processing_statuses: Optional[List[IngestionProcessingStatus]] = Field(
        None, alias="ingestionProcessingStatuses"
    )


class DownloadInfo(BaseModel):
    """Contains information needed to download a file.

    Attributes:
        file_id: Optional ID of the file to download
        url: Optional download URL for the file
    """

    file_id: Optional[str] = Field(None, alias="fileId")
    url: Optional[str] = None


class PreviewInfo(BaseModel):
    """Contains information for previewing a file.

    Attributes:
        preview_url: Optional URL for file preview
        last_modified_date_time_drive: Optional last modified datetime from drive
        description: Optional description of the file
        connector_type_id: Optional ID of the connector type
        connector_type_name: Optional name of the connector type
    """

    preview_url: Optional[str] = Field(None, alias="previewUrl")
    last_modified_date_time_drive: Optional[str] = Field(
        None, alias="lastModifiedDateTimeDrive"
    )
    description: Optional[str] = None
    connector_type_id: Optional[str] = Field(None, alias="connectorTypeId")
    connector_type_name: Optional[str] = Field(None, alias="connectorTypeName")


class GetFileResponse(BaseModel):
    """Response model for getting a single file.

    Contains file metadata, download information, and preview information.

    Attributes:
        file: Optional file object with metadata and processing information
        download_info: Optional download information for the file
        preview_info: Optional preview information for the file
    """

    file: Optional[File] = None
    download_info: Optional[DownloadInfo] = Field(None, alias="downloadInfo")
    preview_info: Optional[PreviewInfo] = Field(None, alias="previewInfo")
