from typing import Union, List, Literal
from .api_base_model import ApiBaseModel
from .study_amendment_reason import StudyAmendmentReason
from .geographic_scope import SubjectEnrollment


class StudyAmendment(ApiBaseModel):
    number: str
    summary: str
    substantialImpact: bool
    primaryReason: StudyAmendmentReason
    secondaryReasons: List[StudyAmendmentReason] = []
    enrollments: List[SubjectEnrollment]
    previousId: Union[str, None] = None
    instanceType: Literal["StudyAmendment"]
