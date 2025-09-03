from typing import Optional
from pydantic import BaseModel

class ImageFile(BaseModel):
    href: str
    mime: str
    hash: Optional[str] = None
    filename: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class ArchiveFile(BaseModel):
    href: str
    mime: str

class StatementFile(BaseModel):
    href: str
    mime: str
    filename: str

class SourceCode(BaseModel):
    id: str
    submission_id: str
    filename: str
    source: str  # Base64-encoded