from typing import Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc
from .code import Code


class Timing(ApiBaseModelNameLabelDesc):
    type: Code
    value: str
    valueLabel: str
    relativeToFrom: Code
    relativeFromScheduledInstanceId: Union[str, None] = None
    relativeToScheduledInstanceId: Union[str, None] = None
    windowLower: Union[str, None] = None
    windowUpper: Union[str, None] = None
    windowLabel: Union[str, None] = None
    instanceType: Literal["Timing"]
