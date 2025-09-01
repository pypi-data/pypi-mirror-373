from typing import Literal, Union
from .api_base_model import ApiBaseModel
from .code import Code


class Range(ApiBaseModel):
    minValue: float
    maxValue: float
    unit: Union[Code, None] = None
    isApproximate: bool
    instanceType: Literal["Range"]
