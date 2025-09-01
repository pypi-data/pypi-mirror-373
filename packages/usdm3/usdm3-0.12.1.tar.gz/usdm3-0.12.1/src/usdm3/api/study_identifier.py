from typing import Literal
from .api_base_model import ApiBaseModel
from .organization import Organization


class StudyIdentifier(ApiBaseModel):
    studyIdentifier: str
    studyIdentifierScope: Organization
    instanceType: Literal["StudyIdentifier"]
