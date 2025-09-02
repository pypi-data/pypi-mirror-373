from typing import List, Optional

from pydantic import BaseModel, Field

from .get_file import DownloadInfo, File


class GetFilesResponse(BaseModel):
    """Response model for getting multiple files.

    Contains a list of files, their download information, and total count.

    Attributes:
        files: Optional list of file objects with metadata and processing information
        download_infos: Optional list of download information for the files
        totalCount: Total number of files available (may be greater than files returned)
    """

    files: Optional[List[File]] = None
    download_infos: Optional[List[DownloadInfo]] = Field(None, alias="downloadInfos")
    totalCount: int
