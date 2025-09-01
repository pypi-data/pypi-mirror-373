from typing import Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc
from .geographic_scope import SubjectEnrollment


class StudySite(ApiBaseModelNameLabelDesc):
    currentEnrollment: Union[SubjectEnrollment, None] = None
    instanceType: Literal["StudySite"]
