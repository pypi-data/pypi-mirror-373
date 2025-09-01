from typing import Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc
from .code import Code


class StudyEpoch(ApiBaseModelNameLabelDesc):
    type: Code
    previousId: Union[str, None] = None
    nextId: Union[str, None] = None
    instanceType: Literal["StudyEpoch"]
