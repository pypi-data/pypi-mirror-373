from typing import Literal
from .api_base_model import ApiBaseModel
from .code import Code


class StudyTitle(ApiBaseModel):
    text: str
    type: Code
    instanceType: Literal["StudyTitle"]
