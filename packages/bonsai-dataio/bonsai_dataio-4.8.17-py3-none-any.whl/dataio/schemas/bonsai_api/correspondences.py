from typing import Optional

from pydantic import Field

from dataio.schemas.bonsai_api.dims import FlowObject

from .base_models import CorrespondenceModel


class ProductCorrespondence(CorrespondenceModel):
    external_name: str = Field(..., max_length=200)
    external_description: Optional[str] = None
    base_name: Optional[FlowObject] = None

    def __str__(self) -> str:
        return f"{self.external_name} - {self.base_name.name if self.base_name else 'None'}"


class LocationCorrespondence(CorrespondenceModel):
    description: Optional[str] = None
    comment: Optional[str] = None


class ActivityTypeCorrespondence(CorrespondenceModel):
    description: Optional[str] = None
    comment: Optional[str] = None


class FlowObjectCorrespondence(CorrespondenceModel):
    description: Optional[str] = None
    comment: Optional[str] = None
