from typing import List, Literal
from .api_base_model import ApiBaseModelNameLabelDesc
from .code import Code


class StudyArm(ApiBaseModelNameLabelDesc):
    type: Code
    dataOriginDescription: str
    dataOriginType: Code
    populationIds: List[str] = []
    instanceType: Literal["StudyArm"]
