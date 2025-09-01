from typing import Literal
from .api_base_model import ApiBaseModel
from .code import Code


class ResponseCode(ApiBaseModel):
    isEnabled: bool
    code: Code
    instanceType: Literal["ResponseCode"]
