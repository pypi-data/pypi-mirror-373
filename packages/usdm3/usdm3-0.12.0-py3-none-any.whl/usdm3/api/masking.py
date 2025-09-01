from .api_base_model import ApiBaseModelAndDesc
from .code import Code
from typing import Literal


class Masking(ApiBaseModelAndDesc):
    role: Code
    instanceType: Literal["Masking"]
