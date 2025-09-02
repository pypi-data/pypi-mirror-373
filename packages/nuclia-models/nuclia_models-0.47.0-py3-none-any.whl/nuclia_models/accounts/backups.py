from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field


class BackupCreate(BaseModel):
    kb_id: UUID4 = Field(..., description="The unique identifier of the knowledgebox to backup.")


class BackupCreateResponse(BaseModel):
    id: UUID4 = Field(..., description="The unique identifier of the created backup.")


class KBDataResponse(BaseModel):
    id: UUID4 = Field(..., description="The unique identifier of the knowledgebox.")
    slug: str = Field(..., description="A human-readable, URL-friendly identifier for the knowledgebox.")
    title: str = Field(..., description="The title of the knowledgebox.")
    created: datetime = Field(..., description="The timestamp when the knowledgebox was created.")


class BackupResponse(BaseModel):
    id: UUID4 = Field(..., description="The unique identifier of the backup.")
    account_id: UUID4 = Field(
        ..., description="The unique identifier of the account associated with the backup."
    )
    started_at: datetime = Field(..., description="The timestamp when the backup process started.")
    kb_data: KBDataResponse = Field(..., description="Metadata of the backed-up knowledgebox.")
    finished_at: Optional[datetime] = Field(
        None, description="The timestamp when the backup process finished."
    )
    size: Optional[int] = Field(None, description="The size of the backup in bytes.")


class BackupRestore(BaseModel):
    slug: str = Field(..., description="The slug of the new restored knowledgebox.")
    title: str = Field(..., description="The title of the new restored knowledgebox.")
