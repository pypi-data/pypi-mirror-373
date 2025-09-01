from typing import Literal, Union
from .api_base_model import ApiBaseModel
from .code import Code


class StudyAmendmentReason(ApiBaseModel):
    code: Code
    otherReason: Union[str, None] = None
    instanceType: Literal["StudyAmendmentReason"]
