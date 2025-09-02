import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from dataio.tools import BonsaiBaseModel


class User(BonsaiBaseModel):
    """Pydantic model representing a user."""

    email: EmailStr
    name: str
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False


class DataLicense(BonsaiBaseModel):
    """Pydantic model for Data License."""

    name: str
    description: str | None = None
    url: str
    create_time: datetime = Field(default_factory=datetime.now)
    created_by: User | None = None  # Assuming a ForeignKey-like relationship

    def __str__(self) -> str:
        return self.name


class Version(BonsaiBaseModel):
    version: str
    create_time: datetime = Field(default_factory=datetime.now)
    comments: str | None = None

    def __str__(self) -> str:
        return f"Version {self.version}"


class MetaData(BonsaiBaseModel):
    id: uuid.UUID
    created_by: User
    last_modified: datetime
    license: DataLicense
    version: Version
